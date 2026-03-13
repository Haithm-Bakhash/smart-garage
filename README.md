# AutoMesh-HW2 — Distributed Microservices System

## Overview

AutoMesh-HW2 is a cloud-ready distributed system built with Python and FastAPI. It extends the original Smart Garage AI microservice (HW#1) into a full distributed architecture with multiple communicating services, an API gateway, authentication, and asynchronous messaging.

---

## Architecture

The system consists of 5 components running in Docker containers:

```
Client
  └── API Gateway (port 8000)
        ├── Auth Service (port 8001)      ← REST (synchronous)
        └── Maintenance Service (port 8002) ← REST (synchronous)
              └── RabbitMQ (port 5672)    ← Async message
                    └── Notification Service (no port, background worker)
```

### Services

| Service | Technology | Responsibility |
|---|---|---|
| API Gateway | FastAPI | Single entry point — routes requests, verifies tokens |
| Auth Service | FastAPI | Issues and validates JWT tokens |
| Maintenance Service | FastAPI + Gemini AI | Predicts vehicle maintenance issues |
| Notification Service | Python + Pika | Listens to RabbitMQ, sends email alerts |
| RabbitMQ | RabbitMQ 3.13 | Message broker for async communication |

---

## Requirements Fulfilled

### 1. Two Additional Microservices
- **Auth Service** — handles user login and token validation
- **Notification Service** — background worker that processes maintenance alerts

### 2. Service-to-Service Communication

**REST (synchronous):**
- API Gateway → Auth Service: `GET /api/v1/auth/verify/{token}`
- API Gateway → Maintenance Service: `POST /api/v1/maintenance/predict`

**Asynchronous Messaging:**
- Maintenance Service publishes a JSON message to the `maintenance_alerts` queue in RabbitMQ after every successful prediction
- Notification Service consumes from the same queue and processes alerts independently

### 3. API Gateway Pattern
- All external traffic enters through a single port (8000)
- The gateway handles token verification before forwarding requests
- Internal services are not directly exposed to the client

### 4. Authentication & Authorization
- `POST /login` issues a Bearer token upon valid credentials
- Every request to `/predict` must include `Authorization: Bearer <token>`
- The gateway rejects unauthorized requests with `401 Unauthorized`
- The maintenance service also requires an internal `x-api-key` header, preventing direct bypass

---

## Communication Design

### Synchronous flow (REST)
When a client calls `POST /predict`:
1. Gateway checks the `Authorization` header
2. Gateway calls Auth Service to verify the token
3. If valid, Gateway forwards the request to Maintenance Service with an internal API key
4. Maintenance Service calls Gemini AI and returns the prediction
5. Gateway returns the result to the client

### Asynchronous flow (RabbitMQ)
After step 4 above:
1. Maintenance Service publishes a message to the `maintenance_alerts` queue
2. Notification Service (running independently) picks up the message
3. Notification Service logs/sends the email alert — completely decoupled from the HTTP response

This design means the client never waits for the notification to be sent. The HTTP response returns immediately, and the notification happens in the background.

---

## How to Run

### Prerequisites
- Docker Desktop installed and running

### Start the system
```bash
docker compose up --build
```

### Test the system
```bash
# Step 1: Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "haithm", "password": "smartgarage"}'

# Step 2: Predict (use the token from step 1)
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer super-secret-jwt-token-123" \
  -d '{"make": "Toyota", "model": "Camry", "year": 2015, "mileage": 95000}'
```

### Check notification logs
```bash
docker compose logs notification-service
```

### Stop everything
```bash
docker compose down
```

---

## Technologies Used

- **FastAPI** — REST API framework
- **Pydantic** — data validation
- **Google Gemini AI** (`gemini-2.0-flash`) — maintenance prediction
- **RabbitMQ** — async message broker
- **Pika** — Python RabbitMQ client
- **Docker & Docker Compose** — containerization
- **Uvicorn** — ASGI server