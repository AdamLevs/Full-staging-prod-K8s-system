#!/bin/bash
set -e

echo "🚀 Deploying to staging environment..."

# Build and load app image
echo "📦 Building application image..."
docker build -t demo-app:latest ./app

echo "📥 Loading image into kind cluster..."
kind load docker-image demo-app:latest --name local-cluster

# Deploy PostgreSQL
echo "🐘 Deploying PostgreSQL..."
helm upgrade --install postgresql-staging ./helm/postgresql \
  --namespace staging \
  --create-namespace \
  --values ./helm/postgresql/values-staging.yaml \
  --set postgresql.database=appdb \
  --set postgresql.username=appuser \
  --set postgresql.password=apppass

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
kubectl wait --namespace staging \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=postgresql \
  --timeout=300s

# Deploy Redis
echo "🔴 Deploying Redis..."
helm upgrade --install redis-staging ./helm/redis \
  --namespace staging \
  --create-namespace \
  --values ./helm/redis/values-staging.yaml \
  --set password=""

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
kubectl wait --namespace staging \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=redis \
  --timeout=300s

# Deploy application
echo "🚀 Deploying application..."
helm upgrade --install demo-app-staging ./helm/demo-app \
  --namespace staging \
  --create-namespace \
  --values ./helm/demo-app/values-staging.yaml \
  --set image.repository=demo-app \
  --set image.tag=latest \
  --set image.pullPolicy=IfNotPresent

# Wait for application to be ready
echo "⏳ Waiting for application to be ready..."
kubectl wait --namespace staging \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=demo-app \
  --timeout=300s

echo "✅ Staging deployment complete!"
echo ""
echo "📋 Access your application:"
echo "   http://staging.local.app:<INGRESS_PORT>"
echo ""
echo "   To get the ingress port:"
echo "   kubectl get svc -n ingress-nginx"

