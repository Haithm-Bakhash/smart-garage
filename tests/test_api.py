import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_unauthorized_access():
    """Ensure the Gateway blocks requests without a Bearer token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/predict",
            json={"make": "Toyota", "model": "Camry", "year": 2015, "mileage": 95000}
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
            json={"make": "Honda", "model": "Civic", "year": 2020, "mileage": 30000}
        )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_and_predict():
    """Test the full Auth and AI Prediction flow (Happy Path)."""
    async with httpx.AsyncClient() as client:
        # 1. Login to get the real JWT token
        login_res = await client.post(
            f"{BASE_URL}/login",
            json={"username": "haithm", "password": "smartgarage"}
        )
        assert login_res.status_code == 200
        token = login_res.json().get("access_token")
        assert token is not None

        # 2. Use the token to request an AI prediction
        headers = {"Authorization": f"Bearer {token}"}
        predict_res = await client.post(
            f"{BASE_URL}/predict",
            headers=headers,
            json={"make": "Toyota", "model": "Camry", "year": 2015, "mileage": 95000},
            timeout=15.0 # Give Gemini some time to respond
        )
        
        # Verify the structure of the AI's response
        assert predict_res.status_code == 200
        data = predict_res.json()
        assert "upcoming_issues" in data
        assert "estimated_cost_usd" in data
        assert "ai_notes" in data