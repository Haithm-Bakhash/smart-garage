import os
import jwt
import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Auth Service - Secure Edition", description="Handles secure JWT generation.")

Instrumentator().instrument(app).expose(app)


JWT_SECRET = os.getenv("JWT_SECRET", "fallback-insecure-secret")
ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/v1/auth/login")
def login(request: LoginRequest):
    
    if request.username == "admin" and request.password == "admin":
        # Generate a real JWT valid for 1 hour
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        payload = {
            "sub": request.username,
            "exp": expiration
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
        
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Wrong username or password")

@app.get("/api/v1/auth/verify/{token}")
def verify_token(token: str):
    try:
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return {"valid": True, "user": payload.get("sub")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")