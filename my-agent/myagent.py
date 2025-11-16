from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.mcp import MCPServerStdio, MCPServerSSE, MCPServerStreamableHTTP
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

class MyAgent:
    def __init__(self, model: OpenAIChatModel, mcp_servers: list[MCPServerStdio | MCPServerSSE | MCPServerStreamableHTTP]):
        self.model = model
        self.agent = Agent(model, 
                            toolsets=mcp_servers, 
                            tools=[duckduckgo_search_tool()],
                            deps_type=int,
                            system_prompt=(f"You are a helpful assistant")
                            )

    def basic_query_test(self):
        query = "Hey can you echo the deps?"

        print("--- MAKING THE AGENT CALL ---")
        response = self.agent.run_sync(query, deps=42)
        return response.output

    async def basic_query_test_async(self, query='Explain how to use structured outputs in Pydantic AI in a short response.'):
        result = await self.agent.run(query)
        return result.output

# IDEA: Subagent to analyze each team, main orchestrator to make a power ranking