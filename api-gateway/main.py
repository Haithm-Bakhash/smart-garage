from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post("http://auth-service:8000/api/v1/auth/login", json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Login failed")
    return response.json()

@app.post("/predict")
async def predict_maintenance(request: Request, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token. Please login first.")
    
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