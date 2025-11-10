from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

class MyAgent:
    def __init__(self, model: OpenAIChatModel):
        self.model = model
        self.agent = Agent(model)

    def basic_query_test(self):
        query = "What is the capital of France?"

        response = self.agent.run_sync(query)
        return response.output