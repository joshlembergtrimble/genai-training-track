from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
import os
import requests
import random

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional

import asyncio

import dotenv
dotenv.load_dotenv()

# Load environment variables
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_ENDPOINT")
AZURE_OPENAI_API_KEY=os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION=os.environ.get("AZURE_OPENAI_API_VERSION")

# Pydantic models
class Meal(BaseModel):
    name: str = Field(...)
    num_fed: Optional[int] = Field(None, description='number of people this meal feeds')
    ingredients: List[str] = Field(...)

class MealList(BaseModel):
    meals: List[Meal]

# Agent functions
def run_agent_query(query='What are the key features of Pydantic AI in a short response.'):
    '''
    Synchroneous run function
    '''
    model = OpenAIChatModel(
        'gpt-4.1',
        provider=AzureProvider(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
            api_key=AZURE_OPENAI_API_KEY,
        ),
    )
    agent = Agent(model)

    result = agent.run_sync(query)
    print("Agent Response:")
    print(result.output)

async def run_agent_query_async(query='Explain how to use structured outputs in Pydantic AI in a short response.'):
    '''
    async run function
    '''
    model = OpenAIChatModel(
        'gpt-4.1',
        provider=AzureProvider(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
            api_key=AZURE_OPENAI_API_KEY,
        ),
    )
    agent = Agent(model)

    result = await agent.run(query)
    print("Agent Response:")
    print(result.output)

async def run_agent_query_stream():
    model = OpenAIChatModel(
        'gpt-4.1',
        provider=AzureProvider(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
            api_key=AZURE_OPENAI_API_KEY,
        ),
    )
    agent = Agent(model)

    user_prompt = "Tell me a sci-fi story about a lost spaceship in a long response."
    async with agent.run_stream(user_prompt) as response:
        async for part in response.stream_text():
            print(part, end='', flush=True)

def run_agent_stateful():
    model = OpenAIChatModel(
        'gpt-4.1',
        provider=AzureProvider(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
            api_key=AZURE_OPENAI_API_KEY,
        )
    )
    agent = Agent(model,
                  system_prompt='You are a question answering agent. Your name is Morpheus.')

    query = ''
    response = None
    while True:
        query = input("\n> ").strip()
        if query=='exit':
            break
        msg_hist = response.all_messages() if response else None
        response = agent.run_sync(query, message_history=msg_hist)
        print(response.output)

def run_agent_structured_output(query='give me three meal ideas for families of varying sizes'):
    model = OpenAIChatModel(
        'gpt-4.1',
        provider=AzureProvider(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
            api_key=AZURE_OPENAI_API_KEY,
        )
    )
    agent = Agent(model,
                  system_prompt='You are a meal planning agent.',
                  output_type=MealList)
    try:
        response = agent.run_sync(query)
        print("OUTPUT")
        for meal in response.output.meals:
            print(meal)
    except ValidationError as e:
        print("Validation Error:", e)
        print("The AI's response did not match the expected structure.")

def run_agent_with_tool():
    model = OpenAIChatModel(
        'gpt-4.1',
        provider=AzureProvider(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
            api_key=AZURE_OPENAI_API_KEY,
        )
    )
    myagent = Agent(model)
                    #,tools=[duckduckgo_search_tool()])


    # Plain tools (dont need context)
    @myagent.tool_plain
    def get_curr_time():
        from datetime import datetime # stupid to import here but it's for cleanliness
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @myagent.tool_plain
    def get_weather(city: str):
        url = f"https://wttr.in/{city}?format=3"  # short summary
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code}"
        
    @myagent.tool_plain
    def get_random_city():
        cities = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
            "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
            "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte",
            "San Francisco", "Indianapolis", "Seattle", "Denver", "Washington",
            "Boston", "El Paso", "Nashville", "Detroit", "Oklahoma City",
            "Portland", "Las Vegas", "Memphis", "Louisville", "Baltimore"
        ]
        return random.choice(cities)

    print(myagent.run_sync("Pick a random city and give me the weather").output)

async def run_agent_with_tool_dep_inj():
    '''
    Running an agent with a tool that uses dependency injection.
    '''
    # Tool with dependency injection and context
    @dataclass
    class Fruit:
        type: str
            
    model = OpenAIChatModel(
        'gpt-4.1',
        provider=AzureProvider(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
            api_key=AZURE_OPENAI_API_KEY,
        )
    )
    myagent = Agent(model,
                    deps_type=Fruit)
    
    @myagent.tool
    def get_fruit_color(ctx: RunContext[dict]):
        match ctx.deps.type.lower():
            case "apple":
                return "red"
            case "banana":
                return "yellow"
            case "orange":
                return "orange"

    deps = Fruit("Banana")

    response = await myagent.run("What color is the fruit? call get_fruit_color", deps=deps)

    print("OUTPUT")
    print(response.output)



# asyncio.run(run_agent_stateful())
asyncio.run(run_agent_with_tool_dep_inj())

