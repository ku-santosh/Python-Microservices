default: dev

dev:
	@echo "Running in DEV environment..."
	@STAGE=dev docker-compose up --build

uat:
	@echo "Running in UAT environment..."
	@STAGE=uat docker-compose up --build

prod:
	@echo "Running in PROD environment..."
	@STAGE=prod docker-compose up --build

stop:
	@docker-compose down

test:
	@echo "Running tests across all services..."
	@STAGE=dev pytest services/auth/tests || true
	@STAGE=dev pytest services/products/tests || true
	@STAGE=dev pytest services/orders/tests || true
	@STAGE=dev pytest gateway/tests || true
