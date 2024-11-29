APPLICATION_NAME="organization_management_backend_service"

black = black -S -l 160 --target-version py311 src/
isort = isort src/
flake8 = poetry run flake8 --show-source --statistics  --exit-zero --config linter_config.flake8 src/


.PHONY: help
help:     ## Show this help.
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

.PHONY: clean
clean:  ## Remove all build, test, coverage and Python artifacts
	rm -rf tests/__pycache__
	rm -rf pydantic/__pycache__
	rm -rf dist
	rm -rf htmlcov
	rm -rf coverage.xml
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . | grep -E "(__pycache__)" | xargs rm -rf

.PHONY: venv
venv:
	poetry env use 3.12
	poetry install
	poetry update

.PHONY: lint
lint:  ## Check style with flake8, isort and black
	$(isort)
	$(flake8)
	$(black)

.PHONY: test-db
test-db: cleanup-dirs  ## Run test postgres db (port: 5432)
	docker-compose up -d postgresdb

.PHONY: cleanup-dirs
cleanup-dirs:
	rm -rf /tmp/organization_management_backend_service
	mkdir -p /tmp/organization_management_backend_service


.PHONY: test
test:   ## Run tests quickly with the default Python
	poetry run pytest -s -v

.PHONY: coverage
coverage:  ## Run pytest and generate coverage report
	PROFILE=test poetry run pytest -s -v --cov-report xml:cov.xml --cov=.

run_debug:  ## Run the debug script
	poetry run python -m organization_management_backend_service.debug

run_main:  ## Run the main script directly
	poetry run python -m organization_management_backend_service.main

run:  ## Run the uvicorn server
	PROFILE=local poetry run uvicorn organization_management_backend_service.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: start_postgres
start_postgres:  ## Start local postgres using docker
                ## username = postgres ; password = postgres
	docker run --name organization_management_backend_service-postgres --rm \
	-e POSTGRES_USER=postgres \
	-e POSTGRES_PASSWORD=postgres \
	-e PGDATA=/var/lib/postgresql/data/pgdata \
	-v /tmp:/var/lib/postgresql/data \
	-p 5432:5432 \
	-it public.ecr.aws/docker/library/postgres:13.11

postgres_logs:  ## Show postgres logs
	echo "To exit press CTRL+C"
	docker logs -f organization_management_backend_service-postgres

.PHONY: docker-build
docker-build:
	docker build --platform linux/x86_64 -t organization_management_backend_service:latest .


.PHONY: docker-prod-run
docker-prod-run:  ## Run containers using docker-compose
	docker-compose up -d api

.PHONY: docker-dev-run
docker-dev-run:  ## Run containers using docker-compose for dev
	docker-compose up -d dev

.PHONY: docker-local-run
docker-local-run:  ## Run containers using docker-compose for local testing
	docker-compose up -d local

.PHONY: docker-stop
docker-stop:  ## Stop containers
	docker-compose down

.PHONY: docker-stop-prod
docker-stop-prod:  ## Stop container for prod
	docker-compose stop api

.PHONY: docker-stop-dev
docker-stop-dev:  ## Stop container for dev
	docker-compose stop dev

.PHONY: docker-stop-local
docker-stop-local:  ## Stop container for local
	docker-compose stop local
