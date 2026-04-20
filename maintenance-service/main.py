import logging
from fastapi import FastAPI
from infrastructure.web import router  # Importing our routes from web.py!
from prometheus_fastapi_instrumentator import Instrumentator

# Set up global logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Smart Garage API",
    description="An AI-powered microservice for predicting vehicle maintenance."
)

# Expose the /metrics endpoint for Prometheus
Instrumentator().instrument(app).expose(app)

# Plug the routes from web.py into our main application
app.include_router(router)

# A simple health check so we know the server is awake
@app.get("/")
def home():
    return {"message": "Welcome to the Smart Garage API! The server is running."}