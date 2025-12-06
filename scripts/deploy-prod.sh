#!/bin/bash
set -e

echo "🚀 Deploying to production environment..."

# Build and load app image
echo "📦 Building application image..."
docker build -t demo-app:latest ./app

echo "📥 Loading image into kind cluster..."
kind load docker-image demo-app:latest --name local-cluster

# Deploy PostgreSQL
echo "🐘 Deploying PostgreSQL..."
helm upgrade --install postgresql-prod ./helm/postgresql \
  --namespace prod \
  --create-namespace \
  --values ./helm/postgresql/values-prod.yaml \
  --set postgresql.database=appdb \
  --set postgresql.username=appuser \
  --set postgresql.password=apppass

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
kubectl wait --namespace prod \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=postgresql \
  --timeout=300s

# Deploy Redis
echo "🔴 Deploying Redis..."
helm upgrade --install redis-prod ./helm/redis \
  --namespace prod \
  --create-namespace \
  --values ./helm/redis/values-prod.yaml \
  --set password=""

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
kubectl wait --namespace prod \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=redis \
  --timeout=300s

# Deploy application
echo "🚀 Deploying application..."
helm upgrade --install demo-app-prod ./helm/demo-app \
  --namespace prod \
  --create-namespace \
  --values ./helm/demo-app/values-prod.yaml \
  --set image.repository=demo-app \
  --set image.tag=latest \
  --set image.pullPolicy=IfNotPresent

# Wait for application to be ready
echo "⏳ Waiting for application to be ready..."
kubectl wait --namespace prod \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=demo-app \
  --timeout=300s

echo "✅ Production deployment complete!"
echo ""
echo "📋 Access your application:"
echo "   http://prod.local.app:<INGRESS_PORT>"
echo ""
echo "   To get the ingress port:"
echo "   kubectl get svc -n ingress-nginx"

