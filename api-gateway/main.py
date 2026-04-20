from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import httpx
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize Rate Limiter (tracks users by IP address)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="API Gateway - Secure Edition")

# Tell FastAPI to use our Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
@limiter.limit("100/minute") # Protect login from brute-force password guessing
async def login(request: Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post("http://auth-service:8000/api/v1/auth/login", json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Login failed")
    return response.json()

@app.post("/predict")
@limiter.limit("100/minute") # Stop users from spamming the expensive AI endpoint
async def predict_maintenance(request: Request, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token.")
    
    token = authorization.split(" ")[1]
    
    async with httpx.AsyncClient() as client:
        auth_check = await client.get(f"http://auth-service:8000/api/v1/auth/verify/{token}")
    
    if auth_check.status_code != 200:
        raise HTTPException(status_code=401, detail="Unauthorized. Fake or expired token.")
    
    data = await request.json()
    headers = {"x-api-key": "my-super-secret-password"}
    
    async with httpx.AsyncClient() as client:
        main_response = await client.post(
            "http://maintenance-service:8000/api/v1/maintenance/predict",
            json=data,
            headers=headers,
            timeout=30.0
        )
    return main_response.json()