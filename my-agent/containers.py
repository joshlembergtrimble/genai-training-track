import logging

from dependency_injector import containers, providers

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

from myagent import MyAgent

import os
import dotenv
dotenv.load_dotenv()

AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_ENDPOINT")
AZURE_OPENAI_API_KEY=os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION=os.environ.get("AZURE_OPENAI_API_VERSION")

def create_azure_provider():
    """Factory function to create AzureProvider"""
    return AzureProvider(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
        api_key=AZURE_OPENAI_API_KEY,
    )

class Container(containers.DeclarativeContainer):
    # Use Factory to create the provider on-demand
    azure_provider = providers.Factory(create_azure_provider)
    
    # Use Factory for the model to avoid deepcopy issues
    model = providers.Factory(
        OpenAIChatModel,
        "gpt-4.1",
        provider=azure_provider,
    )

    # Singleton for the agent (will reuse the same agent instance)
    myagent = providers.Singleton(MyAgent, model=model)