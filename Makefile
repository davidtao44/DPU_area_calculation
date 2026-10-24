.PHONY: up down logs test lint dev-api dev-web

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f area-lab

test:
	.venv/bin/python -m pytest backend/tests
	cd frontend && npm test

lint:
	.venv/bin/ruff check backend scripts
	.venv/bin/ruff format --check backend scripts
	cd frontend && npm run lint

dev-api:
	.venv/bin/python -m uvicorn area_lab.main:create_app --factory --host 127.0.0.1 --port 8000

dev-web:
	cd frontend && npm run dev
