from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.mcp import MCPServerStdio, MCPServerSSE, MCPServerStreamableHTTP
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
import chromadb

class MyAgent:
    def __init__(self, model: OpenAIChatModel, mcp_servers: list[MCPServerStdio | MCPServerSSE | MCPServerStreamableHTTP]):
        self.model = model
        self.agent = Agent(model, 
                            toolsets=mcp_servers, 
                            tools=[duckduckgo_search_tool()],
                            deps_type=int,
                            system_prompt=(f"You are a helpful assistant")
                            )

        self._register_tools()

    def _register_tools(self):
        @self.agent.tool_plain
        def retrieve(query: str):
            """Retrieve documents from the collection"""
            collection_name = "policies"
            client = chromadb.PersistentClient(path="./my_rag/chroma")
            if collection_name not in [col.name for col in client.list_collections()]:
                return "Collection not found"
            else:
                collection = client.get_or_create_collection(name=collection_name)
                results = collection.query(query_texts=[query], n_results=5)
                return results

    def basic_query_test(self):
        query = "What is the HR policy?"

        print("--- MAKING THE AGENT CALL ---")
        response = self.agent.run_sync(query)
        return response.output

    async def basic_query_test_async(self, query='Explain how to use structured outputs in Pydantic AI in a short response.'):
        result = await self.agent.run(query)
        return result.output


# IDEA: Subagent to analyze each team, main orchestrator to make a power ranking