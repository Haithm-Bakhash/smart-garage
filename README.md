# Smart Garage — Final Project

## What is this?

Smart Garage is a distributed microservices platform built for the Smart IoT & AI-powered Automotive domain. The idea is simple: you feed it a vehicle's make, model, year, and mileage, and it uses Groq's LLaMA 3.3 70B AI to predict upcoming maintenance issues, estimate repair costs, and send email alerts asynchronously.

It was built as a final project covering microservices architecture, container orchestration, observability, and security — all running inside a Kubernetes cluster.

---

## Architecture

```text
User (GUI / frontend.html)
  └── API Gateway (port 8080, Rate-Limited)
        ├── Auth Service (port 8001)          ← REST — issues real JWTs
        └── Maintenance Service (port 8002)   ← REST — Groq AI + caching
              └── RabbitMQ (port 5672)        ← async message broker
                    └── Notification Service  ← email alert worker
```

5 decoupled services, each running in its own container inside the cluster.

---

## Features

### AI-Powered Predictions
The maintenance service builds a mechanic-style prompt from the vehicle data and sends it to Groq's LLaMA 3.3 70B model. Responses are cached in memory by vehicle profile so repeated requests don't waste API quota. If the AI fails or hits a quota limit, the system falls back to a deterministic mileage-based algorithm automatically.

### Frontend GUI
A plain HTML/JS frontend (`frontend.html`) handles login, grabs a JWT from the gateway, and renders the AI prediction. No framework needed — serve it locally with Python and open it in a browser (see below).

### Security
- JWTs are generated with PyJWT and expire after 1 hour
- Rate limiting via `slowapi` — 100 requests/minute on the gateway
- All secrets (API keys, JWT secret) are stored as Kubernetes Secrets and injected at runtime, never hardcoded

### Observability
- **Metrics**: Prometheus + Grafana (request rates, latency)
- **Logs**: Fluent Bit → Elasticsearch → Kibana (structured, centralized)
- **Tracing**: Jaeger for cross-service request tracking
- **Reliability**: Kubernetes `livenessProbes` + RabbitMQ Dead Letter Queue (DLQ)

---

## Prerequisites

Make sure you have these installed before starting:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Kubernetes enabled
- `kubectl` configured to point at your local cluster
- Python 3.10+
- A [Groq API key](https://console.groq.com) (free, no credit card required)

---

## Setup & Deployment

### 1. Configure secrets

Before deploying, open `k8s/secrets.yaml` and paste your actual values in plain text — since the file uses `stringData`, Kubernetes handles the encoding automatically. Do NOT base64-encode them manually or they'll be double-encoded and break at runtime.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: smart-garage-secrets
type: Opaque
stringData:
  GROQ_API_KEY: "your-groq-key-here"
  MAINTENANCE_API_KEY: "your-api-password-here"
  JWT_SECRET: "your-jwt-secret-here"
```

**Do not commit this file with real values in it.** Add `k8s/secrets.yaml` to your `.gitignore`.

### 2. Deploy to Kubernetes

Apply the manifests in this order:

```bash
# Secrets first
kubectl apply -f k8s/secrets.yaml

# Core microservices
kubectl apply -f k8s/automesh-stack.yaml

# Optional: observability stack
kubectl apply -f k8s/monitoring-stack.yaml
kubectl apply -f k8s/logging-stack.yaml
kubectl apply -f k8s/extra-reliability-tools.yaml
```

### 3. Port-forward the gateway

The services run inside the cluster, so you need to forward the gateway port to your machine:

```bash
kubectl port-forward svc/api-gateway 8080:8080
```

Keep this terminal open while using the app.

### 4. Serve the frontend

Open a new terminal, navigate to the project folder, and run:

```bash
python3 -m http.server 5500
```

Then open your browser and go to:

```
http://localhost:5500/frontend.html
```

Click **Analyze Vehicle** and it will handle login and show the AI prediction.

> ⚠️ Do not open `frontend.html` by double-clicking it. The browser will block API calls when opened as a local file. Always use the Python server.

### 5. Access observability dashboards (optional)

```bash
# Grafana
kubectl port-forward svc/grafana 3000:3000
# → http://localhost:3000

# Kibana
kubectl port-forward svc/kibana 5601:5601
# → http://localhost:5601

# Jaeger
kubectl port-forward svc/jaeger 16686:16686
# → http://localhost:16686
```

---

## Running Tests

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-test.txt

pytest tests/ -v
```

The test suite covers: JWT validation, rate limiting, invalid token rejection, and the full AI prediction flow.

---

## Teardown

```bash
kubectl delete -f k8s/automesh-stack.yaml
```

---

## Tech Stack

| Layer | Tools |
|---|---|
| Backend | FastAPI, Pydantic, PyJWT, slowapi |
| AI | Groq LLaMA 3.3 70B |
| Messaging | RabbitMQ, Pika |
| Infra | Docker, Kubernetes |
| Observability | Prometheus, Grafana, ELK Stack, Jaeger |
| Testing / CI | Pytest, HTTPX, GitHub Actions |

---