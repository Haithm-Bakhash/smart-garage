import logging
from fastapi import FastAPI
from infrastructure.web import router  
from prometheus_fastapi_instrumentator import Instrumentator

# Set up global logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Smart Garage API",
    description="An AI-powered microservice for predicting vehicle maintenance."
)

Instrumentator().instrument(app).expose(app)

app.include_router(router)

# A simple health check so we know the server is awake
@app.get("/")
def home():
    return {"message": "Welcome to the Smart Garage API! The server is running."}