import logging
from fastapi import FastAPI
from infrastructure.web import router  
from prometheus_fastapi_instrumentator import Instrumentator


logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Smart Garage API",
    description="An AI-powered microservice for predicting vehicle maintenance."
)

Instrumentator().instrument(app).expose(app)

app.include_router(router)


@app.get("/")
def home():
    return {"message": "Welcome to the Smart Garage API! The server is running."}