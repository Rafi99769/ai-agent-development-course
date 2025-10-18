from langchain_core.tools import tool
from typing import Literal
import json
import os

TODO_FILE_PATH = "todos.json"


@tool(
    description="Insert a new todo item. Status of the new item will be `pending` by default."
)
def create_todo(item: str):
    if os.path.exists(TODO_FILE_PATH):
        with open(TODO_FILE_PATH, "r") as f:
            todos = json.load(f)
    else:
        todos = []

    new_id = 1 if not todos else todos[-1]["id"] + 1

    todos.append({"id": new_id, "item": item, "status": "pending"})
    with open(TODO_FILE_PATH, "w") as f:
        json.dump(todos, f)

    return f"Todo item created with ID: {new_id}"


@tool(description="Read all todo items.")
def read_todos():
    if os.path.exists(TODO_FILE_PATH):
        with open(TODO_FILE_PATH, "r") as f:
            todos = json.load(f)
    else:
        todos = []

    return json.dumps(todos, indent=4)


@tool(
    description="Update the status of a todo item. Status can be `working` or `completed`."
)
def update_todo(item_id: int, status: Literal["working", "completed"]):
    with open(TODO_FILE_PATH, "r") as f:
        todos = json.load(f)

    for todo in todos:
        if todo["id"] == item_id:
            todo["status"] = status
            break

    with open(TODO_FILE_PATH, "w") as f:
        json.dump(todos, f)

    return f"Todo item with ID {item_id} updated to status: {status}"
