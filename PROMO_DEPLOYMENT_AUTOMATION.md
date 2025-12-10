# 🚀 PROMO: Guía Completa de Automatización de Deployment 2024-2025

## 🎯 Investigación Global de Herramientas y Mejores Prácticas

> **Documento promocional y educativo** sobre las mejores herramientas, comandos, scripts y accesorios para automatizar deployments en entornos de producción modernos.

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Herramientas CI/CD Principales](#herramientas-cicd-principales)
3. [Plataformas de Deployment Modernas](#plataformas-de-deployment-modernas)
4. [Scripts y Comandos Esenciales](#scripts-y-comandos-esenciales)
5. [Deployment para FastAPI + Next.js](#deployment-para-fastapi--nextjs)
6. [Docker y Kubernetes](#docker-y-kubernetes)
7. [Mejores Prácticas](#mejores-prácticas)
8. [Referencias y Recursos](#referencias-y-recursos)

---

## 🌟 Introducción

El deployment automatizado es fundamental para el desarrollo moderno de software. Esta guía compila las **mejores herramientas, comandos y scripts** disponibles globalmente en 2024-2025, basándose en investigación exhaustiva de múltiples fuentes y repositorios de la industria.

### ¿Por qué automatizar deployments?

- ✅ **Reducción de errores humanos** en producción
- ✅ **Deployments más rápidos** y frecuentes
- ✅ **Rollbacks automáticos** ante fallos
- ✅ **Consistencia** entre entornos (dev, staging, prod)
- ✅ **Monitoreo y logs** centralizados
- ✅ **Escalabilidad** automática según demanda

---

## 🔧 Herramientas CI/CD Principales

### 1. **GitHub Actions** ⭐ RECOMENDADO

**Mejor para**: Integración nativa con repositorios GitHub, proyectos open-source y equipos pequeños.

**Características destacadas**:
- Workflows event-driven en YAML
- Marketplace con miles de actions reutilizables
- Integración directa con Docker y Kubernetes
- Secrets management integrado
- Minutes gratuitos generosos para proyectos públicos

**Ejemplo de workflow básico**:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          npm install
          pip install -r requirements.txt
      
      - name: Build
        run: |
          npm run build
          python -m pytest
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

**Pros**:
- Configuración simple y directa
- Gran ecosistema de actions
- Gratis para proyectos públicos
- Excelente documentación

**Contras**:
- Limitado para infraestructura multi-cloud compleja
- Minutes limitados en planes gratuitos para repos privados

---

### 2. **Jenkins**

**Mejor para**: Pipelines altamente personalizables, empresas con necesidades específicas.

**Características destacadas**:
- Pipeline-as-code con Jenkinsfile
- Extenso ecosistema de plugins (1800+)
- Soporte para Docker y Kubernetes
- Open source y self-hosted

**Ejemplo Jenkinsfile**:

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'myapp'
        REGISTRY = 'docker.io'
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t ${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER} .'
            }
        }
        
        stage('Test') {
            steps {
                sh 'docker run ${DOCKER_IMAGE}:${BUILD_NUMBER} npm test'
            }
        }
        
        stage('Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {
                    sh 'echo $PASS | docker login -u $USER --password-stdin'
                    sh 'docker push ${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}'
                }
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'kubectl set image deployment/myapp myapp=${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}'
                sh 'kubectl rollout status deployment/myapp'
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        failure {
            mail to: 'team@example.com',
                 subject: "Failed Pipeline: ${currentBuild.fullDisplayName}",
                 body: "Something went wrong with ${env.BUILD_URL}"
        }
    }
}
```

**Pros**:
- Extremadamente flexible
- Control total sobre infraestructura
- Ideal para CI/CD complejos

**Contras**:
- Requiere mantenimiento y administración
- Curva de aprendizaje pronunciada
- Problemas ocasionales de compatibilidad de plugins

---

### 3. **Argo CD** - GitOps para Kubernetes

**Mejor para**: Deployments declarativos en Kubernetes, GitOps workflows.

**Características destacadas**:
- Sincronización automática desde Git
- UI rica y CLI poderoso
- RBAC integrado
- Health checks automáticos
- Rollbacks con un click

**Instalación y uso básico**:

```bash
# Instalar Argo CD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Acceder a la UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Login con CLI
argocd login localhost:8080

# Crear aplicación
argocd app create myapp \
  --repo https://github.com/myorg/myrepo.git \
  --path k8s \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default

# Sincronizar
argocd app sync myapp

# Ver estado
argocd app get myapp
```

**Pros**:
- GitOps nativo - Git como fuente de verdad
- Excelente para microservicios
- Auditabilidad completa

**Contras**:
- Requiere Kubernetes
- Complejidad inicial

---

### 4. **GitLab CI/CD**

**Mejor para**: Equipos que buscan plataforma todo-en-uno (Git + CI/CD + Registry).

**Características destacadas**:
- Integración completa de DevOps
- Container registry incluido
- Auto DevOps con detección automática
- Kubernetes integration nativa

**Ejemplo `.gitlab-ci.yml`**:

```yaml
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $DOCKER_IMAGE .
    - docker push $DOCKER_IMAGE

test:
  stage: test
  image: $DOCKER_IMAGE
  script:
    - npm test
    - python -m pytest

deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config set-cluster k8s --server="$KUBE_URL" --insecure-skip-tls-verify=true
    - kubectl config set-credentials admin --token="$KUBE_TOKEN"
    - kubectl config set-context default --cluster=k8s --user=admin
    - kubectl config use-context default
    - kubectl set image deployment/myapp myapp=$DOCKER_IMAGE
    - kubectl rollout status deployment/myapp
  only:
    - main
```

**Pros**:
- Plataforma unificada
- Excelente para equipos medianos/grandes
- Auto DevOps simplifica setup

**Contras**:
- Puede ser costoso para planes avanzados
- Self-hosting requiere recursos considerables

---

### 5. **CircleCI**

**Mejor para**: Builds rápidos, proyectos cloud-native.

**Características destacadas**:
- Paralelización inteligente
- Orbs (paquetes de configuración reutilizables)
- Excelente performance
- Docker Layer Caching

**Ejemplo `.circleci/config.yml`**:

```yaml
version: 2.1

orbs:
  node: circleci/node@5.0
  python: circleci/python@2.1

workflows:
  build-test-deploy:
    jobs:
      - build
      - test:
          requires:
            - build
      - deploy:
          requires:
            - test
          filters:
            branches:
              only: main

jobs:
  build:
    docker:
      - image: cimg/node:20.0
    steps:
      - checkout
      - node/install-packages
      - run: npm run build
      - persist_to_workspace:
          root: .
          paths:
            - .

  test:
    docker:
      - image: cimg/python:3.11
    steps:
      - attach_workspace:
          at: .
      - python/install-packages:
          pkg-manager: pip
      - run: pytest

  deploy:
    docker:
      - image: cimg/base:stable
    steps:
      - attach_workspace:
          at: .
      - run:
          name: Deploy to production
          command: |
            curl -X POST https://api.vercel.com/v1/deployments \
              -H "Authorization: Bearer $VERCEL_TOKEN" \
              -H "Content-Type: application/json" \
              -d @deployment.json
```

**Pros**:
- Muy rápido
- Paralelización eficiente
- Orbs reducen boilerplate

**Contras**:
- Plan gratuito limitado
- Menos flexible que Jenkins

---

## 🌐 Plataformas de Deployment Modernas

### 1. **Vercel** ⭐ MEJOR PARA NEXT.JS

**Características**:
- Deploy automático desde Git
- Edge Functions
- Preview deployments automáticos
- CDN global
- Zero-config para Next.js

**CLI Commands**:

```bash
# Instalar CLI
npm install -g vercel

# Login
vercel login

# Deploy a preview
vercel

# Deploy a producción
vercel --prod

# Ver logs
vercel logs

# Lista deployments
vercel ls

# Rollback (promover deployment anterior)
vercel rollback

# Variables de entorno
vercel env add OPENAI_API_KEY production
vercel env ls
```

**Script de deployment automatizado**:

```bash
#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '%s %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$1" >&2
}

log "Starting Vercel deployment..."

# Verificar variables requeridas
if [ -z "${VERCEL_TOKEN:-}" ]; then
  log "ERROR: VERCEL_TOKEN not set"
  exit 1
fi

# Build local
log "Building application..."
npm run build

# Deploy
log "Deploying to Vercel..."
vercel --prod --token="$VERCEL_TOKEN" --yes

log "Deployment completed successfully!"

# Health check
DEPLOYMENT_URL=$(vercel ls --token="$VERCEL_TOKEN" --meta gitBranch=main -S 1 | grep https | awk '{print $2}')
log "Checking health at $DEPLOYMENT_URL/api/health"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$DEPLOYMENT_URL/api/health")

if [ "$HTTP_CODE" -eq 200 ]; then
  log "✅ Health check passed!"
else
  log "❌ Health check failed with code $HTTP_CODE"
  exit 1
fi
```

---

### 2. **Railway**

**Características**:
- Deploy desde GitHub/GitLab
- Bases de datos managed
- Variables de entorno fáciles
- Excellent DX (Developer Experience)

**CLI Commands**:

```bash
# Instalar
npm install -g @railway/cli

# Login
railway login

# Inicializar proyecto
railway init

# Link a proyecto existente
railway link

# Deploy
railway up

# Ver logs
railway logs

# Abrir en browser
railway open

# Variables de entorno
railway variables set KEY=value
railway variables
```

**Deployment script**:

```bash
#!/usr/bin/env bash
set -euo pipefail

log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

log "Deploying to Railway..."

# Login (usando token de CI/CD)
railway login --browserless

# Deploy
railway up --service "$RAILWAY_SERVICE_ID"

log "Railway deployment triggered successfully!"
```

---

### 3. **Render**

**Características**:
- Deploy automático desde Git
- Static sites, web services, databases
- Preview environments
- Gratis para proyectos personales

**API Deployment Script**:

```bash
#!/usr/bin/env bash
set -euo pipefail

SERVICE_ID="${RENDER_SERVICE_ID}"
API_KEY="${RENDER_API_KEY}"

log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

log "Triggering Render deployment..."

RESPONSE=$(curl -s -X POST \
  "https://api.render.com/v1/services/$SERVICE_ID/deploys" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json")

DEPLOY_ID=$(echo "$RESPONSE" | jq -r '.id')

log "Deployment triggered: $DEPLOY_ID"

# Esperar por completado (opcional)
log "Waiting for deployment to complete..."
while true; do
  STATUS=$(curl -s "https://api.render.com/v1/deploys/$DEPLOY_ID" \
    -H "Authorization: Bearer $API_KEY" | jq -r '.status')
  
  log "Current status: $STATUS"
  
  if [ "$STATUS" = "live" ]; then
    log "✅ Deployment successful!"
    break
  elif [ "$STATUS" = "build_failed" ] || [ "$STATUS" = "deactivated" ]; then
    log "❌ Deployment failed with status: $STATUS"
    exit 1
  fi
  
  sleep 10
done
```

---

### 4. **DigitalOcean App Platform**

**Características**:
- Managed containers
- Auto-scaling
- Build from Dockerfile o buildpacks
- Integración con DO databases

**doctl CLI**:

```bash
# Instalar
brew install doctl  # macOS
# o descargar desde https://github.com/digitalocean/doctl

# Autenticación
doctl auth init

# Crear app desde spec
doctl apps create --spec app.yaml

# Update app
doctl apps update $APP_ID --spec app.yaml

# Lista apps
doctl apps list

# Ver logs
doctl apps logs $APP_ID --follow

# App spec ejemplo (app.yaml)
```

```yaml
name: my-fastapi-app
services:
  - name: api
    github:
      repo: username/repo
      branch: main
      deploy_on_push: true
    source_dir: /
    dockerfile_path: Dockerfile
    http_port: 8000
    instance_count: 2
    instance_size_slug: professional-xs
    routes:
      - path: /api
    envs:
      - key: OPENAI_API_KEY
        scope: RUN_TIME
        type: SECRET
        value: ${OPENAI_API_KEY}
    health_check:
      http_path: /health
      initial_delay_seconds: 30
      period_seconds: 10
```

---

## 📜 Scripts y Comandos Esenciales

### Script de Deploy Universal

```bash
#!/usr/bin/env bash
# deploy.sh - Script universal de deployment
# Uso: ./deploy.sh [vercel|railway|render|docker]

set -euo pipefail
IFS=$'\n\t'

# Configuración
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/deploy.log"

# Colores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Funciones de utilidad
log() {
  local level=$1
  shift
  local message="$*"
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  
  echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
  
  case $level in
    ERROR)
      echo -e "${RED}❌ $message${NC}" >&2
      ;;
    SUCCESS)
      echo -e "${GREEN}✅ $message${NC}"
      ;;
    WARN)
      echo -e "${YELLOW}⚠️  $message${NC}"
      ;;
    *)
      echo "$message"
      ;;
  esac
}

error_exit() {
  log ERROR "$1"
  exit 1
}

# Verificar requisitos
check_requirements() {
  log INFO "Checking requirements..."
  
  local required_cmds=("git" "curl" "jq")
  for cmd in "${required_cmds[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
      error_exit "$cmd is required but not installed"
    fi
  done
  
  log SUCCESS "All requirements met"
}

# Pre-deployment checks
pre_deploy_checks() {
  log INFO "Running pre-deployment checks..."
  
  # Check git status
  if [[ -n $(git status -s) ]]; then
    log WARN "Uncommitted changes detected"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      error_exit "Deployment cancelled"
    fi
  fi
  
  # Check branch
  local branch
  branch=$(git rev-parse --abbrev-ref HEAD)
  log INFO "Current branch: $branch"
  
  if [[ "$branch" != "main" ]] && [[ "$branch" != "master" ]]; then
    log WARN "Not on main/master branch"
  fi
  
  log SUCCESS "Pre-deployment checks passed"
}

# Build application
build_app() {
  log INFO "Building application..."
  
  # Install dependencies
  if [ -f "package.json" ]; then
    log INFO "Installing Node.js dependencies..."
    npm ci || error_exit "npm install failed"
  fi
  
  if [ -f "requirements.txt" ]; then
    log INFO "Installing Python dependencies..."
    pip install -r requirements.txt || error_exit "pip install failed"
  fi
  
  # Run tests
  log INFO "Running tests..."
  if [ -f "package.json" ]; then
    npm test || log WARN "Tests failed but continuing..."
  fi
  
  # Build
  if [ -f "package.json" ]; then
    log INFO "Building Next.js..."
    npm run build || error_exit "Build failed"
  fi
  
  log SUCCESS "Build completed"
}

# Deploy to Vercel
deploy_vercel() {
  log INFO "Deploying to Vercel..."
  
  if [ -z "${VERCEL_TOKEN:-}" ]; then
    error_exit "VERCEL_TOKEN not set"
  fi
  
  vercel --prod --token="$VERCEL_TOKEN" --yes || error_exit "Vercel deployment failed"
  
  log SUCCESS "Deployed to Vercel"
}

# Deploy to Railway
deploy_railway() {
  log INFO "Deploying to Railway..."
  
  railway up || error_exit "Railway deployment failed"
  
  log SUCCESS "Deployed to Railway"
}

# Deploy to Render
deploy_render() {
  log INFO "Deploying to Render..."
  
  if [ -z "${RENDER_SERVICE_ID:-}" ] || [ -z "${RENDER_API_KEY:-}" ]; then
    error_exit "RENDER_SERVICE_ID and RENDER_API_KEY must be set"
  fi
  
  curl -X POST \
    "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys" \
    -H "Authorization: Bearer $RENDER_API_KEY" \
    || error_exit "Render deployment failed"
  
  log SUCCESS "Deployed to Render"
}

# Deploy with Docker Compose
deploy_docker() {
  log INFO "Deploying with Docker Compose..."
  
  docker-compose pull || error_exit "Failed to pull images"
  docker-compose down || log WARN "Failed to stop containers"
  docker-compose up -d || error_exit "Failed to start containers"
  
  log SUCCESS "Deployed with Docker"
}

# Post-deployment verification
verify_deployment() {
  local url=$1
  log INFO "Verifying deployment at $url..."
  
  sleep 5  # Wait for services to start
  
  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url/health" || echo "000")
  
  if [ "$http_code" -eq 200 ]; then
    log SUCCESS "Health check passed!"
  else
    log ERROR "Health check failed with code: $http_code"
    return 1
  fi
}

# Rollback function
rollback() {
  log WARN "Initiating rollback..."
  
  case $1 in
    vercel)
      vercel rollback
      ;;
    docker)
      docker-compose down
      docker-compose up -d
      ;;
    *)
      log ERROR "Rollback not implemented for platform: $1"
      return 1
      ;;
  esac
  
  log SUCCESS "Rollback completed"
}

# Cleanup
cleanup() {
  log INFO "Cleaning up..."
  # Add cleanup tasks here
}

# Trap para manejar errores
trap 'log ERROR "Deployment failed!"; cleanup; exit 1' ERR
trap 'cleanup' EXIT

# Main execution
main() {
  local platform=${1:-}
  
  if [ -z "$platform" ]; then
    echo "Usage: $0 [vercel|railway|render|docker]"
    exit 1
  fi
  
  log INFO "Starting deployment to $platform..."
  
  check_requirements
  pre_deploy_checks
  build_app
  
  case $platform in
    vercel)
      deploy_vercel
      ;;
    railway)
      deploy_railway
      ;;
    render)
      deploy_render
      ;;
    docker)
      deploy_docker
      ;;
    *)
      error_exit "Unknown platform: $platform"
      ;;
  esac
  
  log SUCCESS "Deployment completed successfully! 🎉"
}

# Execute main function
main "$@"
```

---

## 🐍 Deployment para FastAPI + Next.js

### Docker Compose Production-Ready

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MONGODB_URI=${MONGODB_URI}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  logs:
```

### Dockerfile para FastAPI (Multi-stage)

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Dockerfile para Next.js (Multi-stage)

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### NGINX Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=web_limit:10m rate=30r/s;

    server {
        listen 80;
        server_name example.com;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Frontend
        location / {
            limit_req zone=web_limit burst=20 nodelay;
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # Backend API
        location /api {
            limit_req zone=api_limit burst=10 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health checks (no rate limit)
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }
    }
}
```

---

## ☸️ Docker y Kubernetes

### Comandos Docker Esenciales

```bash
# Build
docker build -t myapp:latest .
docker build -t myapp:v1.0.0 --target production .

# Push
docker tag myapp:latest registry.example.com/myapp:latest
docker push registry.example.com/myapp:latest

# Run
docker run -d -p 8000:8000 --name myapp myapp:latest
docker run -d -p 8000:8000 -e OPENAI_API_KEY=$KEY myapp:latest

# Logs
docker logs -f myapp
docker logs --tail 100 myapp

# Inspect
docker inspect myapp
docker stats myapp

# Clean up
docker system prune -a
docker volume prune
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
  labels:
    app: fastapi
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: myregistry/fastapi:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: fastapi-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fastapi-service
            port:
              number: 80
```

### Kubectl Commands

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get deployments
kubectl get pods
kubectl get services

# Describe
kubectl describe deployment fastapi-app
kubectl describe pod fastapi-app-xxxxx

# Logs
kubectl logs -f deployment/fastapi-app
kubectl logs -f pod/fastapi-app-xxxxx --all-containers

# Scale
kubectl scale deployment fastapi-app --replicas=5

# Update image (rolling update)
kubectl set image deployment/fastapi-app fastapi=myregistry/fastapi:v2.0.0
kubectl rollout status deployment/fastapi-app

# Rollback
kubectl rollout undo deployment/fastapi-app
kubectl rollout history deployment/fastapi-app

# Port forward
kubectl port-forward service/fastapi-service 8000:80

# Secrets
kubectl create secret generic api-secrets \
  --from-literal=openai-key=$OPENAI_API_KEY

# Delete
kubectl delete -f k8s/
```

### Helm Chart

```yaml
# helm/values.yaml
replicaCount: 3

image:
  repository: myregistry/fastapi
  tag: "latest"
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80
  targetPort: 8000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: fastapi-tls
      hosts:
        - api.example.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

**Helm commands**:

```bash
# Install
helm install fastapi-app ./helm -f ./helm/values.yaml

# Upgrade
helm upgrade fastapi-app ./helm -f ./helm/values.yaml

# Rollback
helm rollback fastapi-app 1

# List releases
helm list

# Uninstall
helm uninstall fastapi-app
```

---

## 🎯 Mejores Prácticas

### 1. **Seguridad**

```bash
# ✅ DO: Usar secrets management
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value --secret-id openai-key --query SecretString --output text)

# ❌ DON'T: Hardcodear secrets
export OPENAI_API_KEY="sk-proj-abc123..."

# ✅ DO: Escanear vulnerabilidades
docker scan myapp:latest
trivy image myapp:latest

# ✅ DO: Usar usuarios non-root en containers
RUN useradd -m -u 1000 appuser
USER appuser

# ✅ DO: Actualizar dependencias regularmente
npm audit fix
pip install --upgrade pip-audit && pip-audit
```

### 2. **Monitoreo y Observabilidad**

```bash
# Health check endpoint
# FastAPI
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Prometheus metrics
# pip install prometheus-fastapi-instrumentator
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### 3. **Logs Estructurados**

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### 4. **Testing en CI/CD**

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:6
        ports:
          - 27017:27017
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        env:
          MONGODB_URI: mongodb://localhost:27017/test
        run: |
          pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### 5. **Estrategias de Rollback**

```bash
# Blue-Green Deployment
kubectl apply -f deployment-green.yaml
# Verificar que funciona
kubectl set service production app=green
# Si falla, rollback inmediato
kubectl set service production app=blue

# Canary Deployment
# 90% tráfico a stable, 10% a canary
kubectl apply -f canary-deployment.yaml
# Monitorear métricas
# Si OK, promover canary gradualmente

# Rolling update con pause
kubectl set image deployment/app app=myapp:v2.0.0
kubectl rollout pause deployment/app
# Verificar pods
kubectl rollout resume deployment/app
```

### 6. **Automation Scripts Collection**

```bash
# scripts/backup-database.sh
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MONGO_URI="${MONGODB_URI}"

mongodump --uri="$MONGO_URI" --out="$BACKUP_DIR/backup_$TIMESTAMP"
tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" "$BACKUP_DIR/backup_$TIMESTAMP"
rm -rf "$BACKUP_DIR/backup_$TIMESTAMP"

# Mantener solo últimos 7 backups
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: backup_$TIMESTAMP.tar.gz"
```

```bash
# scripts/rotate-secrets.sh
#!/bin/bash
set -euo pipefail

# Rotar API keys automáticamente
OLD_KEY=$(kubectl get secret api-secrets -o jsonpath='{.data.openai-key}' | base64 -d)
NEW_KEY=$(generate_new_key_from_openai_api)

kubectl create secret generic api-secrets-new \
  --from-literal=openai-key=$NEW_KEY

kubectl set env deployment/app --from=secret/api-secrets-new
kubectl rollout status deployment/app

# Verificar que funciona
if [ $? -eq 0 ]; then
  kubectl delete secret api-secrets
  kubectl create secret generic api-secrets \
    --from-literal=openai-key=$NEW_KEY
  echo "Secret rotated successfully"
else
  echo "Rollback to old secret"
  kubectl set env deployment/app --from=secret/api-secrets
fi
```

---

## 📚 Referencias y Recursos

### Documentación Oficial
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Argo CD Documentation](https://argo-cd.readthedocs.io/)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

### Recursos de Aprendizaje
- [The Twelve-Factor App](https://12factor.net/) - Metodología para aplicaciones SaaS
- [Google Cloud Architecture Framework](https://cloud.google.com/architecture/framework)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [CNCF Cloud Native Trail Map](https://github.com/cncf/trailmap)

### Herramientas Complementarias
- **Monitoring**: Prometheus, Grafana, Datadog, New Relic
- **Logging**: ELK Stack, Loki, CloudWatch
- **Secrets Management**: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault
- **Infrastructure as Code**: Terraform, Pulumi, CloudFormation
- **Testing**: Selenium, Cypress, k6, Locust
- **Security**: Snyk, Trivy, OWASP ZAP, SonarQube

### Repositorios de Ejemplo
- [Awesome CI/CD](https://github.com/cicdops/awesome-ciandcd)
- [Bash Scripts Collection](https://github.com/djeada/Bash-Scripts)
- [Next.js + FastAPI Template](https://github.com/vintasoftware/nextjs-fastapi-template)
- [Kubernetes Examples](https://github.com/kubernetes/examples)
- [Docker Best Practices](https://github.com/hexops/dockerfile)

### Artículos Recomendados
- [Top 18 Continuous Deployment Tools for 2025](https://spacelift.io/blog/continuous-deployment-tools)
- [14 Best Automated Deployment Tools in 2025](https://www.functionize.com/automated-testing/best-automated-deployment-tools)
- [Building Production-Ready APIs with FastAPI](https://dev.to/nithinbharathwaj/advanced-fastapi-patterns-building-production-ready-apis-with-python-2024-guide-2mf9)
- [Deploy FastAPI with Docker for Production](https://pytutorial.com/deploy-fastapi-with-docker-for-production/)

---

## 🎓 Conclusión

Esta guía compila las mejores prácticas y herramientas disponibles para automatizar deployments en 2024-2025. La elección de herramientas dependerá de:

- **Tamaño del equipo**: GitHub Actions para equipos pequeños, Jenkins/GitLab para empresas
- **Stack tecnológico**: Vercel para Next.js, Railway/Render para full-stack simple
- **Presupuesto**: Opciones gratuitas vs enterprise
- **Complejidad**: Docker Compose para proyectos simples, Kubernetes para microservicios
- **Experiencia del equipo**: Plataformas managed vs self-hosted

**Recomendaciones generales**:
- ✅ Comienza con **GitHub Actions + Vercel** para proyectos Next.js/FastAPI
- ✅ Usa **Docker** para consistencia entre entornos
- ✅ Implementa **health checks** y **monitoring** desde el inicio
- ✅ Automatiza **testing** en CI/CD
- ✅ Practica **GitOps** cuando sea posible
- ✅ Mantén **secrets** fuera del código
- ✅ Documenta tus **scripts** y **workflows**

---

**Versión**: 1.0.0  
**Última actualización**: Diciembre 2024  
**Mantenedor**: BMC Uruguay - Sistema de Cotizaciones

---

## 📞 Soporte

Para más información sobre la implementación de estas herramientas en el proyecto BMC Chatbot 2311, consulta:
- `DEPLOYMENT_GUIDE.md` - Guía específica del proyecto
- `UNIFIED_LAUNCHER.md` - Sistema de lanzamiento unificado
- `README.md` - Documentación principal del proyecto

**¿Preguntas?** Abre un issue en el repositorio o contacta al equipo de desarrollo.

---

*Este documento fue creado mediante investigación global de las mejores prácticas y herramientas de deployment disponibles en la industria del software en 2024-2025.*
