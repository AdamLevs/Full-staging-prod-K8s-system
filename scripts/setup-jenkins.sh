#!/bin/bash
set -e

echo "🚀 Setting up Jenkins..."

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create Jenkins network if it doesn't exist
docker network create jenkins-net 2>/dev/null || true

# Start Jenkins
echo "📦 Starting Jenkins container..."
cd jenkins
docker-compose up -d

echo "⏳ Waiting for Jenkins to start..."
sleep 30

# Get initial admin password
echo "🔑 Getting initial admin password..."
JENKINS_PASSWORD=$(docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "Password not available yet. Check Jenkins logs.")

echo ""
echo "✅ Jenkins is starting!"
echo ""
echo "📋 Next steps:"
echo "   1. Open Jenkins in your browser: http://localhost:8080"
echo "   2. Initial admin password: ${JENKINS_PASSWORD}"
echo "   3. Install suggested plugins"
echo "   4. Create admin user"
echo ""
echo "   5. Configure Jenkins to use Docker, kubectl, helm, and kind:"
echo "      - Go to Manage Jenkins > Global Tool Configuration"
echo "      - Ensure Docker, kubectl, helm, and kind are available in PATH"
echo ""
echo "   6. Create a new Pipeline job:"
echo "      - New Item > Pipeline"
echo "      - Pipeline definition: Pipeline script from SCM"
echo "      - SCM: Git"
echo "      - Repository URL: file:///workspace (or your git repo)"
echo "      - Script Path: jenkins/Jenkinsfile"
echo ""
echo "   7. Make sure Jenkins has access to:"
echo "      - Docker socket (already mounted)"
echo "      - kubectl config (may need to copy ~/.kube/config)"
echo ""
echo "   To copy kubectl config to Jenkins:"
echo "   docker cp ~/.kube/config jenkins:/var/jenkins_home/.kube/config"

