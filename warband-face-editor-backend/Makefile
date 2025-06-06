.PHONY: help build up down logs shell clean test

help:
	@echo "Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start services (development)"
	@echo "  make down     - Stop services"
	@echo "  make logs     - View logs"
	@echo "  make shell    - Enter backend container shell"
	@echo "  make clean    - Remove containers and volumes"
	@echo "  make test     - Run tests"

build:
	docker-compose -f docker-compose.dev.yml build

up:
	docker-compose -f docker-compose.dev.yml up -d

down:
	docker-compose -f docker-compose.dev.yml down

logs:
	docker-compose -f docker-compose.dev.yml logs -f

shell:
	docker-compose -f docker-compose.dev.yml exec backend /bin/bash

clean:
	docker-compose -f docker-compose.dev.yml down -v
	docker system prune -f

test:
	docker-compose -f docker-compose.dev.yml exec backend pytest tests/ -v

# Production commands
prod-up:
	docker-compose --profile production up -d

prod-down:
	docker-compose --profile production down