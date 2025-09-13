# Python Microservices Project (Full Package)

This package contains a Python microservices example with a dedicated **db_service (gRPC)** and services:
- auth
- products
- orders
- token_service
- db_service (gRPC server)

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
4. Services:
   - Auth: http://localhost:5001
   - Products: http://localhost:5002
   - Orders: http://localhost:5003
   - Token Service: http://localhost:5004
   - db_service (gRPC): localhost:50051 (and health HTTP at 50052)
   - Traefik Dashboard: http://localhost:8080

## Database setup (Postgres)
Run migrations or create tables manually. Example SQL is included in `migrations/schema.sql`.

## Notes
- After generating protos, run the services. If you prefer not to generate protos, you can still inspect code and proto files.
- Each service performs a simple TCP health check to the db_service gRPC port at startup and prints connection status lines like:
  - "Successfully connected to the database."
  - "Error connecting to the database: <error>"


## Project Structure

#python-microservices-full/

- ├─ README.md
- ├─ docker-compose.yml 
- ├─ .env.dev
- ├─ .env.uat
- ├─ .env.prod
- ├─ migrations/
- │  └─ schema.sql
- ├─ proto/
- │  ├─ db_service.proto
- │  ├─ db_service_pb2.py         # placeholder
- │  └─ db_service_pb2_grpc.py    # placeholder
- ├─ services/
- │  ├─ common/
- │  │  └─ db_client.py
- │  ├─ db_service/
- │  │  ├─ server.py
- │  │  └─ requirements.txt
- │  │  └─ Dockerfile
- │  ├─ auth/
- │  │  ├─ app.py
- │  │  ├─ utils.py
- │  │  ├─ requirements.txt
- │  │  └─ Dockerfile
- │  ├─ products/
- │  │  ├─ app.py
- │  │  ├─ requirements.txt
- │  │  └─ Dockerfile
- │  ├─ orders/
- │  │  ├─ app.py
- │  │  ├─ requirements.txt
- │  │  └─ Dockerfile
- │  └─ token_service/
- │     ├─ app.py
- │     ├─ requirements.txt
- │     └─ Dockerfile
- ├─ gateway/
- │  └─ traefik_dynamic.yml
- ├─ k8s/
- │  └─ microservices-all.yaml
- └─ .github/
- │  └─ workflows/
- │     └─ ci.yml