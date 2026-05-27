#!/usr/bin/env python3

"""Step 4: run the SCC MCP agent."""

from __future__ import annotations

import asyncio
import json
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from openai import OpenAI

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://mcp.security.cisco.com/mcp")
MODEL = os.getenv("LLM_MODEL", "gpt-4o")

SYSTEM_PROMPT = """You are a Cisco Security Cloud Control assistant.

You have access to Security Cloud Control MCP tools for reading organizations, subscriptions, roles, users, and groups.

Guidelines:
- Prefer read-only operations unless the user explicitly asks for a write action.
- Present tool results clearly and concisely.
- If the user asks about subscriptions, roles, users, or admin groups for an organization and does not specify an organization ID, default to this organization ID from the environment: {default_org_id}.
- If the user explicitly provides a different organization ID in the prompt, use that value instead.
"""


def _get_access_token() -> str:
    token = os.getenv("SCC_API_KEY_TOKEN")
    if not token:
        raise SystemExit(
            "Missing SCC API key token. Set `SCC_API_KEY_TOKEN` in your environment."
        )
    return token


def _get_org_id() -> str:
    org_id = os.getenv("SCC_ORG_ID")
    if not org_id:
        raise SystemExit("Missing organization ID. Set `SCC_ORG_ID` in your environment.")
    return org_id


def _create_llm_client() -> OpenAI:
    return OpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
    )


def _mcp_tools_to_openai_tools(mcp_tools):
    tools = []
    for tool in mcp_tools:
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
        )
    return tools


async def _agent_loop(session, tools, user_prompt, llm_client: OpenAI):
    openai_tools = _mcp_tools_to_openai_tools(tools)
    system_prompt = SYSTEM_PROMPT.format(default_org_id=_get_org_id())
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    while True:
        response = llm_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=openai_tools,
        )

        choice = response.choices[0]
        if choice.finish_reason == "stop":
            print(f"\nAgent: {choice.message.content}\n")
            break

        if choice.finish_reason == "tool_calls":
            messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                print(f"  -> Calling: {tool_name}({json.dumps(tool_args, indent=2)})")
                result = await session.call_tool(tool_name, tool_args)

                if result.isError:
                    print(f"  !! Tool error: {result.content}")

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result.content),
                    }
                )


async def _async_main() -> None:
    headers = {"Authorization": f"Bearer {_get_access_token()}"}
    llm_client = _create_llm_client()

    async with streamablehttp_client(MCP_SERVER_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            tools = tools_result.tools

            print("Connected to the Security Cloud Control MCP server.")
            print(f"{len(tools)} tools available.\n")
            print("Try prompts like:")
            print("  - List my organizations")
            print("  - List user roles in the organization")
            print("  - List the admin groups for the organization")
            print("  - Change my organization name to <INSERT_ORG_NAME>\n")

            while True:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit"):
                    print("Goodbye!")
                    break
                await _agent_loop(session, tools, user_input, llm_client)


def main() -> int:
    asyncio.run(_async_main())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
