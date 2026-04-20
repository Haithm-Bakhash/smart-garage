from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Auth Service", description="Handles user login and tokens.")

# Expose the /metrics endpoint for Prometheus
Instrumentator().instrument(app).expose(app)

# The data we expect when someone logs in
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/v1/auth/login")
def login(request: LoginRequest):
    # Requirement 4: Basic Authentication
    if request.username == "haithm" and request.password == "smartgarage":
        return {"access_token": "super-secret-jwt-token-123", "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Wrong username or password")

@app.get("/api/v1/auth/verify/{token}")
def verify_token(token: str):
    if token == "super-secret-jwt-token-123":
        return {"valid": True, "user": "haithm"}
    
    raise HTTPException(status_code=401, detail="Invalid or expired token")