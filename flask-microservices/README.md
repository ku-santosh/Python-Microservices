# Flask Microservices Example
## Python Microservices Project (Full Package)

This repository contains a small microservices example (auth, products, orders) with multi-environment configuration, Docker, tests, and CI/CD examples.

This package contains a Python microservices example with a dedicated **db_service (gRPC)** and services:
- auth
- products
- orders
- token_service
- db_service (gRPC server)

## Added features

- Postgres-backed users and orders (SQLAlchemy, hashed passwords via bcrypt)
- Traefik reverse-proxy for docker-compose routing
- Kubernetes manifests under `k8s/`
- Helm chart scaffold under `charts/microservices`

## Quick start (development)

1. Copy `.env.dev` to `.env` or set STAGE=dev (we use .env.dev by default in compose).
2. Generate gRPC Python files (requires `grpcio-tools`):
   ```bash
   python -m pip install grpcio grpcio-tools
   python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto proto/db_service.proto
   ```
   This will create `proto/db_service_pb2.py` and `proto/db_service_pb2_grpc.py` used by services.
3. Build and start with Docker Compose:
   ```bash
   STAGE=dev docker-compose up --build
   ```

### Flask Microservices Project
```bash
# Development
docker-compose up --build


# Or using Makefile
make dev
make uat
make prod
```


### 4. Access Services
- Auth: `http://localhost/auth`
- Auth: `http://localhost:5001`
- Products: `http://localhost/products`
- Products: `http://localhost:5002`
- Orders: `http://localhost/orders`
- Orders: `http://localhost:5003`
- Token Service: `http://localhost:5004`
- db_service (gRPC): localhost:50051 (and health HTTP at 50052)
- Traefik Dashboard: `http://localhost:8080`


### 5. Running Tests
```bash
make test
```


---


## ☸️ Kubernetes Deployment


1. Apply manifests:
```bash
kubectl apply -f k8s/microservices-all.yaml
```


2. Deploy with Helm:
```bash
helm install microservices charts/microservices -n microservices --create-namespace
```


3. Access via Ingress:
- `/auth` → Auth Service
- `/orders` → Orders Service
- `/products` → Products Service


---


## 🔄 CI/CD Pipeline
- Defined in `.github/workflows/ci.yml`.
- Runs on push/PR to `main`:
- Install dependencies
- Run tests
- Build & push Docker images to registry


Set GitHub secrets:
- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_ACCESS_TOKEN`


---


## ✅ Next Steps
- Add Alembic migrations for DB schema.
- Add Persistent Volumes in Kubernetes.
- Enable TLS in Traefik with Let's Encrypt.


---

## Database setup (Postgres)
Run migrations or create tables manually. Example SQL is included in `migrations/schema.sql`.

📌 You now have a **production-ready microservices project** with Flask, Postgres, Traefik, Docker, Kubernetes, Helm, and CI/CD.

## Notes
- After generating protos, run the services. If you prefer not to generate protos, you can still inspect code and proto files.
- Each service performs a simple TCP health check to the db_service gRPC port at startup and prints connection status lines like:
  - "Successfully connected to the database."
  - "Error connecting to the database: <error>"