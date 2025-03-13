from fastapi import FastAPI

app = FastAPI()

@app.get("/api/hello")
async def root():
    return {"message": "Hello World"}
