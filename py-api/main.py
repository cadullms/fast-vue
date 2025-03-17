from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

static_dir = Path(__file__).resolve().parent / "static"

api = FastAPI(openapi_prefix="/api")
app.mount("/api", api)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

@api.get("/hello")
async def hello():
    return {"message": "Hello World"}
