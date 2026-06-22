from fastapi import FastAPI

app = FastAPI(title="FPL Jubilee Ascent API")


@app.get("/")
def read_root() -> dict[str, str]:
    """Return health check status or root message."""
    return {"status": "ok", "message": "Welcome to FPL Jubilee Ascent API"}
