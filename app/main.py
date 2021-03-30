import uvicorn as uvicorn
from fastapi import FastAPI

from app.api.api_v1.api import api_router

app = FastAPI()

app.include_router(api_router, prefix="/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
