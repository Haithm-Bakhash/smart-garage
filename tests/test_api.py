import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_unauthorized_access():
    """Ensure the Gateway blocks requests without a Bearer token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/predict",
            json={
                "make": "Toyota", "model": "Camry", "year": 2015, "mileage": 95000,
                "engine_type": "2.5L 4-Cylinder", "transmission": "Automatic", 
                "driving_environment": "City / Stop-and-Go", "current_symptoms": "None"
            }
        )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_failure():
    """Ensure the Gateway rejects invalid credentials."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/login",
            json={"username": "hacker", "password": "wrongpassword"}
        )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_invalid_token():
    """Ensure the Gateway rejects fake or tampered JWT tokens."""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIs.FakePayload.FakeSignature"}
        response = await client.post(
            f"{BASE_URL}/predict",
            headers=headers,
            json={
                "make": "Honda", "model": "Civic", "year": 2020, "mileage": 30000,
                "engine_type": "1.5L Turbo", "transmission": "CVT", 
                "driving_environment": "Mostly Highway", "current_symptoms": "None"
            }
        )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_and_predict():
    """Test the full Auth and AI Prediction flow (Happy Path)."""
    async with httpx.AsyncClient() as client:
        # Login to get the real JWT token
        login_res = await client.post(
            f"{BASE_URL}/login",
            json={"username": "haithm", "password": "smartgarage"}
        )
        assert login_res.status_code == 200
        token = login_res.json().get("access_token")
        assert token is not None

        
        headers = {"Authorization": f"Bearer {token}"}
        predict_res = await client.post(
            f"{BASE_URL}/predict",
            headers=headers,
            json={
                "make": "Toyota", "model": "Camry", "year": 2015, "mileage": 95000,
                "engine_type": "2.5L 4-Cylinder", "transmission": "Automatic", 
                "driving_environment": "Extreme Heat", "current_symptoms": "Squeaking brakes"
            },
            timeout=15.0 
        )
        
      
        assert predict_res.status_code == 200
        data = predict_res.json()
        assert "upcoming_issues" in data
        assert "estimated_cost_usd" in data
        assert "ai_notes" in data