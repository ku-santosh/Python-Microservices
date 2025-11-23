# Python Microservices (FastAPI) with db_service (gRPC)

This package contains services rewritten to **FastAPI**. The gRPC protobufs must be generated locally
with grpcio-tools to enable actual gRPC functionality. Placeholder proto stubs are included but you
must regenerate real files as described below.

To generate real stubs:
1. Install grpc tools: `python -m pip install grpcio grpcio-tools`
2. Run: `python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto proto/db_service.proto`
3. Rebuild Docker images and run docker-compose.

