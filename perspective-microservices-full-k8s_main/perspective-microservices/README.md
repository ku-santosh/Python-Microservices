# 📌 Perspective Microservices Project

This project implements a **microservices architecture** in Python (Flask), with separate services for:

- **db-proxy** → Handles all database interactions (Postgres)  
- **perspective-service** → CRUD endpoints for perspectives  
- **columnstate-service** → Manages column state JSON objects  
- **filtermodel-service** → Handles filter model JSON objects  

The stack is fully containerized with **Docker**, orchestrated with **Docker Compose** for local development, and deployable to **Azure Kubernetes Service (AKS)** with CI/CD pipelines.

---

## 🚀 Features

- Modular microservices (`Flask` + `Requests`)  
- Database layer abstracted into `db-proxy` (PostgreSQL + JSONB fields)  
- Environment-based configuration (`dev`, `uat`, `prod`)  
- `docker-compose.yml` for local dev  
- Kubernetes manifests for AKS (dev/uat/prod)  
- GitHub Actions CI/CD pipeline  
- SQL initialization (`init.sql`) with schema + seed data  
- Automated deployment script (`deploy.sh`)  
- **Ingress setup for single load balancer access**

---

## 🛠️ Project Structure

perspective-microservices/
│── db-proxy/
│── perspective-service/
│── columnstate-service/
│── filtermodel-service/
│── k8s/ (dev, uat, prod manifests)
│── .github/workflows/cicd.yml
│── docker-compose.yml
│── init.sql
│── .env.dev / .env.uat / .env.prod
│── deploy.sh
│── README.md











# Perspective Microservices (Full Code)

This archive contains full working Flask microservices:
- db-proxy (talks to Postgres)
- perspective-service (routes for perspectives)
- columnstate-service (column_state upserts/deletes)
- filtermodel-service (filter_model upserts)

Use `docker-compose up --build` at the project root to run everything locally.

Endpoints:
- db-proxy: http://localhost:5000
- perspective-service: http://localhost:5001/api/v1/perspectives
- columnstate-service: http://localhost:5002/api/v1/column_state
- filtermodel-service: http://localhost:5003/api/v1/filter_model
