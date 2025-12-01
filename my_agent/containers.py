from typing import Any

from dependency_injector import containers, providers

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.mcp import CallToolFunc, MCPServerStdio, ToolResult
from pydantic_ai import RunContext

from core import MyAgent

import os
import dotenv
dotenv.load_dotenv()

AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY=os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION=os.environ.get("AZURE_OPENAI_API_VERSION")

def create_azure_provider():
    """Factory function to create AzureProvider"""
    return AzureProvider(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
        api_key=AZURE_OPENAI_API_KEY,
    )


async def process_tool_call(
    ctx: RunContext[int],
    call_tool: CallToolFunc,
    name: str,
    tool_args: dict[str, Any],
) -> ToolResult:
    """A tool call processor that passes along the deps."""
    return await call_tool(name, tool_args, {'deps': ctx.deps})


class Container(containers.DeclarativeContainer):
    # Use Factory to create the provider on-demand
    azure_provider = providers.Factory(create_azure_provider)
    
    # Use Factory for the model to avoid deepcopy issues
    model = providers.Factory(
        OpenAIChatModel,
        "gpt-4.1",
        provider=azure_provider,
    )

    weather_server = providers.Factory(
        MCPServerStdio,
        command='uv',
        args=['run', 'my_mcp/weather.py', 'stdio'], 
        timeout=10.0,
        tool_prefix='weather'
    )

    espn_fantasy_server = providers.Factory(
        MCPServerStdio,
        command='uv',
        args=['run', 'my_mcp/espn_fantasy.py', 'stdio'], 
        timeout=10.0,
        tool_prefix='espn'
    )

    sleeper_fantasy_server = providers.Factory(
        MCPServerStdio,
        command='uv',
        args=['run', 'my_mcp/sleeper_fantasy.py', 'stdio'], 
        timeout=10.0,
        tool_prefix="sleeper"
    )

    deps_server = providers.Factory(
        MCPServerStdio,
        command='uv',
        args=['run', 'my_mcp/mcp_with_deps.py', 'stdio'], 
        timeout=10.0,
        tool_prefix="deps",
        process_tool_call=process_tool_call
    )

    # Singleton for the agent (will reuse the same agent instance)
    mcp_servers = providers.List(
                                weather_server,
                                espn_fantasy_server,
                                sleeper_fantasy_server,
                                deps_server
                                )
    myagent = providers.Singleton(MyAgent, model=model, mcp_servers=mcp_servers)