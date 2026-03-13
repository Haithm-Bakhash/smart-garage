# AutoMesh-HW2 — API Documentation

Base URL: `http://localhost:8000`

---

## Authentication

### POST /login

Authenticates a user and returns a Bearer token.

**Request body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Example request:**
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "haithm", "password": "smartgarage"}'
```

**Success response — 200 OK:**
```json
{
  "access_token": "super-secret-jwt-token-123",
  "token_type": "bearer"
}
```

**Error response — 401 Unauthorized:**
```json
{
  "detail": "Login failed"
}
```

---

## Maintenance Prediction

### POST /predict

Predicts upcoming maintenance issues for a vehicle using Gemini AI.
Requires a valid Bearer token in the `Authorization` header.
After returning the prediction, asynchronously publishes an alert to RabbitMQ.

**Headers:**
| Header | Value | Required |
|---|---|---|
| `Authorization` | `Bearer <token>` | Yes |
| `Content-Type` | `application/json` | Yes |

**Request body:**
```json
{
  "make": "string",
  "model": "string",
  "year": 2015,
  "mileage": 95000
}
```

| Field | Type | Description |
|---|---|---|
| `make` | string | Vehicle manufacturer (e.g. Toyota) |
| `model` | string | Vehicle model (e.g. Camry) |
| `year` | integer | Model year |
| `mileage` | integer | Current mileage in miles |

**Example request:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer super-secret-jwt-token-123" \
  -d '{"make": "Toyota", "model": "Camry", "year": 2015, "mileage": 95000}'
```

**Success response — 200 OK:**
```json
{
  "upcoming_issues": [
    "Replace brake pads",
    "Perform wheel alignment",
    "Replace cabin filter"
  ],
  "estimated_cost_usd": 320,
  "ai_notes": "Your Camry is at a common milestone for brake and tire maintenance."
}
```

| Field | Type | Description |
|---|---|---|
| `upcoming_issues` | array of strings | List of predicted maintenance tasks |
| `estimated_cost_usd` | integer | Total estimated repair cost in USD |
| `ai_notes` | string | AI-generated contextual note |

**Error response — 401 Unauthorized (missing/invalid token):**
```json
{
  "detail": "Missing or invalid token. Please login first."
}
```

**Error response — 500 Internal Server Error:**
```json
{
  "detail": "Internal Server Error"
}
```

---

## Internal Service Endpoints

These endpoints are used internally between services. They are not intended for direct client use.

### Auth Service (port 8001)

#### POST /api/v1/auth/login
Issues a token. Called by the API Gateway on behalf of the client.

#### GET /api/v1/auth/verify/{token}
Validates a token. Called by the API Gateway before forwarding requests.

**Success response — 200 OK:**
```json
{
  "valid": true,
  "user": "haithm"
}
```

### Maintenance Service (port 8002)

#### POST /api/v1/maintenance/predict
The core AI prediction endpoint. Requires internal header `x-api-key`.

**Additional required header:**
```
x-api-key: my-super-secret-password
```

---

## Async Messaging (RabbitMQ)

After every successful prediction, the Maintenance Service publishes the following JSON message to the `maintenance_alerts` queue:

```json
{
  "car": "Toyota Camry",
  "issues": ["Replace brake pads", "Perform wheel alignment"],
  "cost": 320
}
```

The Notification Service consumes this queue and processes each message independently of the HTTP response cycle.

**RabbitMQ Management Dashboard:** `http://localhost:15672`
- Username: `guest`
- Password: `guest`
