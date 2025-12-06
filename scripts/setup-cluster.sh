#!/bin/bash
set -e

echo "🚀 Setting up local Kubernetes cluster..."

# Check if kind is installed
if ! command -v kind &> /dev/null; then
    echo "❌ kind is not installed. Please install it first:"
    echo "   brew install kind  # macOS"
    echo "   or visit: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install it first:"
    echo "   brew install kubectl  # macOS"
    exit 1
fi

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ helm is not installed. Please install it first:"
    echo "   brew install helm  # macOS"
    exit 1
fi

# Delete existing cluster if it exists
if kind get clusters | grep -q "local-cluster"; then
    echo "🗑️  Deleting existing cluster..."
    kind delete cluster --name local-cluster
fi

# Create cluster
echo "📦 Creating kind cluster..."
kind create cluster --name local-cluster --config kind-config.yaml

# Wait for cluster to be ready
echo "⏳ Waiting for cluster to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Create namespaces
echo "📁 Creating namespaces..."
kubectl apply -f k8s/namespaces.yaml

# Label nodes (kind labels are set in config, but let's verify)
echo "🏷️  Verifying node labels..."
kubectl get nodes --show-labels

# Install nginx ingress controller
echo "🌐 Installing nginx ingress controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress controller to be ready
echo "⏳ Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

# Get ingress controller service details
echo "✅ Cluster setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Add to /etc/hosts:"
echo "      127.0.0.1 staging.local.app"
echo "      127.0.0.1 prod.local.app"
echo ""
echo "   2. Get ingress controller port:"
echo "      kubectl get svc -n ingress-nginx"
echo ""
echo "   3. Deploy applications:"
echo "      ./scripts/deploy-staging.sh"
echo "      ./scripts/deploy-prod.sh"

