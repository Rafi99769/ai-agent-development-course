from fastapi import FastAPI
from src.routers import router

app = FastAPI()

@app.get("/")
def greet():
    return {"message": "Hello, World! Welcome to the API!"}

app.include_router(router, prefix="/api")