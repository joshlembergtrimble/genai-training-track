from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

app = FastAPI()

class Item(BaseModel):
    text: str # Required because no default value
    is_done: bool = False
    model_config = ConfigDict(str_max_length=10)

@app.get("/")
def root():
    return {"Hello": "World"}

items = []

# While both below are at the same endpoint, the are different requests (post vs get) so they route correctly
@app.post("/items", response_model=list[Item])
def create_item(item: Item):
    items.append(item)
    return items

@app.get("/items", response_model=list[Item])
def list_items(limit: int = 10):
    return items[0:limit]

@app.get("/clear-items")
def clear_items():
    items.clear()
    return "Items list cleared successfully"

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    if item_id < len(items) and item_id >= 0:
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail=f"Item id {item_id} out of range (valid range [0-{len(items)}])")

def main():
    print("Hello from genai-training-track!")


if __name__ == "__main__":
    main()
