.PHONY: help setup-cluster deploy-staging deploy-prod deploy-all build clean stop-jenkins start-jenkins test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup-cluster: ## Setup Kubernetes cluster with kind
	@./scripts/setup-cluster.sh

deploy-staging: ## Deploy application to staging
	@./scripts/deploy-staging.sh

deploy-prod: ## Deploy application to production
	@./scripts/deploy-prod.sh

deploy-all: deploy-staging deploy-prod ## Deploy to both staging and production

build: ## Build application Docker image
	@echo "Building application image..."
	@docker build -t demo-app:latest ./app
	@echo "Loading image into kind cluster..."
	@kind load docker-image demo-app:latest --name local-cluster || true

test: ## Run application tests
	@echo "Running tests..."
	@cd app && python -m pytest test_main.py -v || true

clean: ## Clean up cluster and deployments
	@echo "Cleaning up..."
	@helm uninstall demo-app-staging -n staging 2>/dev/null || true
	@helm uninstall postgresql-staging -n staging 2>/dev/null || true
	@helm uninstall redis-staging -n staging 2>/dev/null || true
	@helm uninstall demo-app-prod -n prod 2>/dev/null || true
	@helm uninstall postgresql-prod -n prod 2>/dev/null || true
	@helm uninstall redis-prod -n prod 2>/dev/null || true
	@kind delete cluster --name local-cluster 2>/dev/null || true
	@echo "Cleanup complete!"

start-jenkins: ## Start Jenkins container
	@cd jenkins && docker-compose up -d
	@echo "Jenkins starting at http://localhost:8080"

stop-jenkins: ## Stop Jenkins container
	@cd jenkins && docker-compose down
	@echo "Jenkins stopped"

status: ## Show cluster status
	@echo "=== Nodes ==="
	@kubectl get nodes --show-labels
	@echo ""
	@echo "=== Staging Pods ==="
	@kubectl get pods -n staging
	@echo ""
	@echo "=== Production Pods ==="
	@kubectl get pods -n prod
	@echo ""
	@echo "=== Ingress Service ==="
	@kubectl get svc -n ingress-nginx

logs-staging: ## Show staging application logs
	@kubectl logs -n staging -l app.kubernetes.io/name=demo-app --tail=50 -f

logs-prod: ## Show production application logs
	@kubectl logs -n prod -l app.kubernetes.io/name=demo-app --tail=50 -f

