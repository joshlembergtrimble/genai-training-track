from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from my_agent.containers import Container
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# class Item(BaseModel):
#     text: str # Required because no default value
#     is_done: bool = False
#     model_config = ConfigDict(str_max_length=10)

class ChatMessage(BaseModel):
    """Format of messages sent to the browser."""

    role: Literal['user', 'model']
    timestamp: str
    content: str

class QueryRequest(BaseModel):
    """Request model for chat queries."""
    query: str

# Import and initialize agent
container = Container()
myagent = container.myagent()


@app.get("/")
def root():
    return {"Hello": "World"}

@app.get("/test")
def test():
    response = myagent.agent.run_sync('What are the key features of Pydantic AI in a short response.')
    return response.output

@app.post("/chat")
def chat(request: QueryRequest):
    """Send a query to the agent and return the response."""
    try:
        response = myagent.agent.run_sync(request.query)
        return {"response": response.output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


