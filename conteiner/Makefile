PYTHON := $(shell command -v python3 2> /dev/null || command -v python)

# Generate environment
generate:
	@if [ ! -f .env ]; then \
		echo "Generating .env file..."; \
		$(PYTHON) backend/app/generate_env.py; \
		sync; \
	else \
		echo ".env file already exists. Skipping generation."; \
	fi

# Run the application
up:
	@make generate
	chmod +x initdb/init.sh
	docker compose up --build

# Shut down the application
down:
	docker compose down -v
	@rm -f backend/.env .env

# Destroy everything ===> WARNING: This will remove all Docker containers, images, networks, and volumes
destroy:
	docker system prune -a --volumes
	@rm -f backend/.env .env frontend/ssl/fullchain.pem frontend/ssl/privkey.pem