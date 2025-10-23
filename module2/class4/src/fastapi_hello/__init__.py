from fastapi_hello.main import app

__all__ = ["app"]


def main() -> None:
    """Entry point for running the FastAPI application."""
    import uvicorn
    uvicorn.run("fastapi_hello.main:app", host="0.0.0.0", port=8000, reload=True)
