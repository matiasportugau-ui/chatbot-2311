# 🚀 Quick Reference: Deployment Automation

> **Referencia rápida** de comandos y herramientas para deployment. Ver [PROMO_DEPLOYMENT_AUTOMATION.md](./PROMO_DEPLOYMENT_AUTOMATION.md) para la guía completa.

---

## 📑 Índice Rápido

- [CI/CD Tools](#cicd-tools)
- [Cloud Platforms](#cloud-platforms)
- [Docker Commands](#docker-commands)
- [Kubernetes Commands](#kubernetes-commands)
- [Deployment Scripts](#deployment-scripts)

---

## 🔧 CI/CD Tools

### GitHub Actions
```bash
# Crear workflow
mkdir -p .github/workflows
cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm install && npm run build
      - run: vercel --prod
EOF
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Build') { steps { sh 'docker build -t app .' } }
        stage('Test') { steps { sh 'npm test' } }
        stage('Deploy') { steps { sh 'kubectl apply -f k8s/' } }
    }
}
```

### Argo CD
```bash
argocd app create myapp --repo https://github.com/user/repo.git \
  --path k8s --dest-server https://kubernetes.default.svc
argocd app sync myapp
```

---

## 🌐 Cloud Platforms

### Vercel
```bash
npm install -g vercel
vercel login
vercel --prod                    # Deploy to production
vercel env add KEY production    # Add environment variable
vercel logs                      # View logs
vercel rollback                  # Rollback deployment
```

### Railway
```bash
npm install -g @railway/cli
railway login
railway link
railway up                       # Deploy
railway logs                     # View logs
railway variables set KEY=value  # Set environment variable
```

### Render
```bash
# Trigger deployment via API
curl -X POST https://api.render.com/v1/services/$SERVICE_ID/deploys \
  -H "Authorization: Bearer $API_KEY"
```

### DigitalOcean
```bash
# Install doctl
brew install doctl
doctl auth init
doctl apps create --spec app.yaml
doctl apps logs $APP_ID --follow
```

---

## 🐳 Docker Commands

### Build & Run
```bash
# Build
docker build -t myapp:latest .
docker build -t myapp:v1.0.0 --target production .

# Run
docker run -d -p 8000:8000 --name myapp myapp:latest
docker run -d -e OPENAI_API_KEY=$KEY myapp:latest

# Logs
docker logs -f myapp
docker logs --tail 100 myapp

# Clean
docker system prune -a
docker volume prune
```

### Docker Compose
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build

# Scale
docker-compose up -d --scale backend=3
```

---

## ☸️ Kubernetes Commands

### Basic Operations
```bash
# Apply manifests
kubectl apply -f k8s/

# Get resources
kubectl get pods
kubectl get deployments
kubectl get services

# Describe
kubectl describe deployment myapp
kubectl describe pod myapp-xxxxx

# Logs
kubectl logs -f deployment/myapp
kubectl logs -f pod/myapp-xxxxx
```

### Deployment Management
```bash
# Scale
kubectl scale deployment myapp --replicas=5

# Update image
kubectl set image deployment/myapp myapp=myapp:v2.0.0
kubectl rollout status deployment/myapp

# Rollback
kubectl rollout undo deployment/myapp
kubectl rollout history deployment/myapp

# Restart
kubectl rollout restart deployment/myapp
```

### Debugging
```bash
# Port forward
kubectl port-forward service/myapp 8000:80

# Execute command in pod
kubectl exec -it myapp-xxxxx -- /bin/bash

# Get pod events
kubectl get events --sort-by=.metadata.creationTimestamp
```

### Secrets & ConfigMaps
```bash
# Create secret
kubectl create secret generic api-secrets \
  --from-literal=openai-key=$OPENAI_API_KEY

# Create configmap
kubectl create configmap app-config \
  --from-file=config.json

# View secrets
kubectl get secrets
kubectl describe secret api-secrets
```

---

## 📜 Deployment Scripts

### Universal Deploy Script
```bash
#!/bin/bash
# deploy.sh - Universal deployment script
set -euo pipefail

PLATFORM=${1:-vercel}

case $PLATFORM in
  vercel)
    vercel --prod --token="$VERCEL_TOKEN" --yes
    ;;
  railway)
    railway up
    ;;
  docker)
    docker-compose pull
    docker-compose up -d
    ;;
  k8s)
    kubectl apply -f k8s/
    kubectl rollout status deployment/myapp
    ;;
  *)
    echo "Usage: $0 [vercel|railway|docker|k8s]"
    exit 1
    ;;
esac

echo "✅ Deployment to $PLATFORM completed!"
```

### Health Check Script
```bash
#!/bin/bash
# health-check.sh
set -euo pipefail

URL=${1:-http://localhost:8000/health}
MAX_RETRIES=30
RETRY_DELAY=5

for i in $(seq 1 $MAX_RETRIES); do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL" || echo "000")
  
  if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ Health check passed!"
    exit 0
  fi
  
  echo "⏳ Attempt $i/$MAX_RETRIES - Status: $HTTP_CODE"
  sleep $RETRY_DELAY
done

echo "❌ Health check failed after $MAX_RETRIES attempts"
exit 1
```

### Backup Script
```bash
#!/bin/bash
# backup.sh
set -euo pipefail

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database backup
mongodump --uri="$MONGODB_URI" --out="$BACKUP_DIR/backup_$TIMESTAMP"
tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" "$BACKUP_DIR/backup_$TIMESTAMP"
rm -rf "$BACKUP_DIR/backup_$TIMESTAMP"

# Keep only last 7 backups
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: backup_$TIMESTAMP.tar.gz"
```

---

## 🛠️ Useful One-Liners

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Check if service is running
curl -f http://localhost:8000/health || echo "Service down"

# Watch pod status
watch kubectl get pods

# Get all container logs
docker ps -q | xargs -I {} docker logs {}

# Clean up Docker completely
docker system prune -a --volumes -f

# Get resource usage
kubectl top nodes
kubectl top pods

# Force delete stuck pod
kubectl delete pod myapp-xxxxx --grace-period=0 --force

# Export all secrets
kubectl get secrets -o json | jq -r '.items[] | .metadata.name'

# Quickly test endpoint
time curl -w "\nHTTP: %{http_code}\nTime: %{time_total}s\n" http://localhost:8000/health
```

---

## 📊 Monitoring Commands

### Docker Stats
```bash
# Real-time stats
docker stats

# Stats for specific container
docker stats myapp

# Memory usage
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"
```

### Kubernetes Metrics
```bash
# Node metrics
kubectl top nodes

# Pod metrics
kubectl top pods

# Specific deployment
kubectl top pods -l app=myapp

# Watch resource usage
watch kubectl top pods
```

---

## 🔐 Security Best Practices

```bash
# Scan Docker image for vulnerabilities
docker scan myapp:latest
trivy image myapp:latest

# Check secrets in Git
git secrets --scan

# Audit npm packages
npm audit
npm audit fix

# Python security check
pip install safety
safety check

# Update all dependencies
npm update
pip install --upgrade -r requirements.txt
```

---

## 📚 Recursos Adicionales

- **Guía Completa**: [PROMO_DEPLOYMENT_AUTOMATION.md](./PROMO_DEPLOYMENT_AUTOMATION.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Docker Compose**: [docker-compose.prod.yml](./docker-compose.prod.yml)
- **Scripts**: [scripts/](./scripts/)

---

## 🎯 Checklist de Deployment

```markdown
- [ ] Tests pasan en local
- [ ] Variables de entorno configuradas
- [ ] Secrets almacenados de forma segura
- [ ] Health check implementado
- [ ] Logs configurados
- [ ] Monitoring setup (opcional)
- [ ] Backup configurado (si aplica)
- [ ] Documentación actualizada
- [ ] Plan de rollback definido
- [ ] Deploy a staging primero
- [ ] Verificar deployment en staging
- [ ] Deploy a producción
- [ ] Verificar deployment en producción
- [ ] Monitorear por 24h
```

---

**Última actualización**: Diciembre 2024  
**Versión**: 1.0.0

*Para ejemplos completos y mejores prácticas detalladas, consulta [PROMO_DEPLOYMENT_AUTOMATION.md](./PROMO_DEPLOYMENT_AUTOMATION.md)*
