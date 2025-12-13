# BMC Chatbot - GKE Deployment Configuration

Complete Kubernetes deployment configuration for the BMC chatbot system on Google Kubernetes Engine (GKE) Autopilot.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Scaling](#scaling)
- [Updates & Rollbacks](#updates--rollbacks)
- [Security](#security)

---

## 🎯 Overview

This deployment configuration provides:

- **High Availability**: Multiple replicas for API and webhook services
- **Auto-scaling**: GKE Autopilot automatically manages node scaling
- **SSL/HTTPS**: Managed certificates via Google Certificate Manager
- **Secrets Management**: External Secrets Operator integration with Google Secret Manager
- **Scheduled Tasks**: CronJobs for background agents
- **Monitoring**: Prometheus annotations and Cloud Monitoring integration

### Components

| Component | Description | Replicas | Resources |
|-----------|-------------|----------|-----------|
| **API Server** | FastAPI REST API | 2 | 256Mi-512Mi, 250m-500m CPU |
| **Webhooks** | WhatsApp/webhook handlers | 2 | 256Mi-512Mi, 250m-500m CPU |
| **Agents** | Background workers | 1 | 512Mi-1Gi, 500m-1000m CPU |
| **CronJobs** | Scheduled tasks | On-demand | Variable |

---

## 🏗️ Architecture

```
Internet
    ↓
[GCE Load Balancer + SSL Certificate]
    ↓
[GKE Ingress Controller]
    ↓
    ├─→ /api/* → API Service (ClusterIP) → API Pods (2 replicas)
    ├─→ /webhooks/* → Webhooks Service (ClusterIP) → Webhook Pods (2 replicas)
    └─→ Background Agents (1 replica, no service)
    
External Services:
- MongoDB Atlas (MONGODB_URI)
- Google Secret Manager (secrets)
- OpenAI/Groq/Gemini APIs
- WhatsApp Business API
- N8N Workflows (optional)
```

---

## 📦 Prerequisites

### 1. Google Cloud Platform

- Active GCP project with billing enabled
- GKE API enabled
- Artifact Registry API enabled
- Secret Manager API enabled
- Compute Engine API enabled

### 2. Tools Installation

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install kubectl
gcloud components install kubectl

# Install External Secrets Operator (ESO) CLI (optional)
helm repo add external-secrets https://charts.external-secrets.io
```

### 3. Required Credentials

All secrets should be stored in Google Secret Manager:

- `openai-api-key` - OpenAI API key
- `groq-api-key` - Groq API key (optional)
- `gemini-api-key` - Google Gemini API key (optional)
- `whatsapp-token` - WhatsApp access token
- `whatsapp-verify-token` - WhatsApp verify token
- `whatsapp-phone-number-id` - WhatsApp phone number ID
- `mongodb-uri` - MongoDB connection string
- `n8n-webhook-url` - N8N webhook URL (optional)
- `n8n-api-key` - N8N API key (optional)
- `postgres-uri` - PostgreSQL connection string (optional)
- `admin-password` - Admin dashboard password
- `google-sheets-credentials` - Google Sheets service account JSON (optional)
- `google-sheet-id` - Google Sheet ID (optional)

---

## 🚀 Quick Start

### 1. Set Environment Variables

```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export CLUSTER_NAME="bmc-chatbot-cluster"
export DOMAIN="chatbot.yourdomain.com"
```

### 2. Create GKE Autopilot Cluster

```bash
gcloud container clusters create-auto $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --release-channel=regular \
    --enable-autoscaling \
    --enable-autorepair \
    --enable-autoupgrade \
    --workload-pool=$PROJECT_ID.svc.id.goog
```

### 3. Configure kubectl

```bash
gcloud container clusters get-credentials $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID
```

### 4. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create bmc-chatbot \
    --repository-format=docker \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="BMC Chatbot container images"
```

### 5. Store Secrets in Google Secret Manager

```bash
# Example: Store OpenAI API key
echo -n "sk-your-openai-key" | gcloud secrets create openai-api-key \
    --data-file=- \
    --replication-policy="automatic" \
    --project=$PROJECT_ID

# Repeat for all required secrets
# See "Configuration" section for complete list
```

### 6. Install External Secrets Operator

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm repo update

helm install external-secrets \
    external-secrets/external-secrets \
    --namespace external-secrets-system \
    --create-namespace \
    --set installCRDs=true
```

### 7. Setup IAM and Workload Identity

```bash
# Create service account for External Secrets
gcloud iam service-accounts create external-secrets \
    --project=$PROJECT_ID \
    --description="Service account for External Secrets Operator" \
    --display-name="External Secrets"

# Grant Secret Manager access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:external-secrets@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create service account for application
gcloud iam service-accounts create bmc-chatbot \
    --project=$PROJECT_ID \
    --description="Service account for BMC Chatbot application" \
    --display-name="BMC Chatbot"

# Bind Kubernetes SA to GCP SA (Workload Identity)
kubectl create namespace bmc-chatbot

gcloud iam service-accounts add-iam-policy-binding \
    external-secrets@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[bmc-chatbot/external-secrets-sa]"

gcloud iam service-accounts add-iam-policy-binding \
    bmc-chatbot@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[bmc-chatbot/bmc-chatbot-sa]"
```

### 8. Update Configuration Files

Replace `PROJECT_ID` in all YAML files:

```bash
cd k8s/
find . -name "*.yaml" -type f -exec sed -i "s/PROJECT_ID/$PROJECT_ID/g" {} +
```

Update domain in `ingress.yaml`:

```bash
sed -i "s/chatbot.yourdomain.com/$DOMAIN/g" ingress.yaml
```

### 9. Create Static IP

```bash
gcloud compute addresses create bmc-chatbot-ip \
    --global \
    --project=$PROJECT_ID
    
# Get the IP address
gcloud compute addresses describe bmc-chatbot-ip --global --format="value(address)"
```

### 10. Deploy Application

```bash
# Apply manifests in order
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f api-service.yaml
kubectl apply -f agents-deployment.yaml
kubectl apply -f webhooks-deployment.yaml
kubectl apply -f webhooks-service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f cronjobs.yaml

# Verify deployment
kubectl get all -n bmc-chatbot
```

---

## ⚙️ Detailed Setup

### Building and Pushing Container Images

You need to build three container images:

#### Using the Build Script

```bash
# Set environment variables
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export VERSION="v1.0.0"  # or "latest"

# Run from repository root directory
./k8s/build-and-push.sh
```

The script will:
1. Check requirements (gcloud, docker)
2. Configure Docker authentication
3. Build all three images
4. Push to Artifact Registry

#### Manual Build

If you prefer to build images manually:

```bash
# Build API server image (run from repository root)
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/api-server:latest \
    -f k8s/Dockerfile.api .

# Push to Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/api-server:latest
```

**Note:** All Dockerfiles are in the `k8s/` directory but should be built from the repository root to include all source files.

#### Image Descriptions

**1. API Server** (`k8s/Dockerfile.api`)
- Based on Python 3.11 slim
- Runs FastAPI application via `api_server.py`
- Exposes port 8000
- Includes health check endpoint
- Non-root user (uid 1000)

**2. Background Agents** (`k8s/Dockerfile.agents`)
- Based on Python 3.11 slim
- Runs `automated_agent_system.py`
- Includes git for repository operations
- Non-root user (uid 1000)
- Can be overridden for specific agent tasks

**3. Webhooks** (`k8s/Dockerfile.webhooks`)
- Based on Python 3.11 slim
- Runs `sistema_completo_integrado.py` on port 8080
- Includes health check endpoint
- Non-root user (uid 1000)

All Dockerfiles include:
- Multi-stage caching for faster builds
- Security best practices (non-root user, minimal packages)
- Health checks where applicable
- Optimized layer ordering

### Setting Up DNS

Point your domain to the static IP:

```bash
# Get static IP
IP=$(gcloud compute addresses describe bmc-chatbot-ip --global --format="value(address)")

echo "Create an A record in your DNS provider:"
echo "  Name: chatbot (or @)"
echo "  Type: A"
echo "  Value: $IP"
echo "  TTL: 300"
```

---

## 🔧 Configuration

### Environment Variables

All configuration is managed through Kubernetes secrets (via Google Secret Manager).

#### Required Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `openai-api-key` | OpenAI API key | `sk-...` |
| `mongodb-uri` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/bmc` |
| `whatsapp-token` | WhatsApp access token | `EAAxxxx...` |
| `admin-password` | Admin password | `SecurePassword123!` |

#### Optional Secrets

| Secret Name | Description |
|-------------|-------------|
| `groq-api-key` | Groq API key for alternative LLM |
| `gemini-api-key` | Google Gemini API key |
| `n8n-webhook-url` | N8N workflow webhook URL |
| `postgres-uri` | PostgreSQL connection string |
| `google-sheets-credentials` | Service account JSON |

### Configurable Values

Edit these in the YAML files:

- **Domain**: `ingress.yaml` → Replace `chatbot.yourdomain.com`
- **Replicas**: `*-deployment.yaml` → Change `spec.replicas`
- **Resources**: `*-deployment.yaml` → Adjust `resources.requests/limits`
- **CronJob Schedules**: `cronjobs.yaml` → Modify `spec.schedule`
- **Image Registry**: All deployments → Update image paths

---

## 🚢 Deployment

### Initial Deployment

```bash
# Deploy all resources
kubectl apply -f k8s/

# Watch deployment progress
kubectl get pods -n bmc-chatbot -w
```

### Verify Deployment

```bash
# Check all resources
kubectl get all -n bmc-chatbot

# Check pods
kubectl get pods -n bmc-chatbot

# Check services
kubectl get svc -n bmc-chatbot

# Check ingress
kubectl get ingress -n bmc-chatbot

# Check secrets
kubectl get externalsecrets -n bmc-chatbot
kubectl get secrets -n bmc-chatbot

# Check CronJobs
kubectl get cronjobs -n bmc-chatbot
```

### View Logs

```bash
# API server logs
kubectl logs -n bmc-chatbot -l app.kubernetes.io/name=api-server -f

# Webhooks logs
kubectl logs -n bmc-chatbot -l app.kubernetes.io/name=webhooks -f

# Agents logs
kubectl logs -n bmc-chatbot -l app.kubernetes.io/name=agents -f

# CronJob logs (after execution)
kubectl logs -n bmc-chatbot -l app.kubernetes.io/name=product-mapper-job --tail=100
```

### Test Endpoints

```bash
# Get ingress IP
IP=$(kubectl get ingress bmc-chatbot-ingress -n bmc-chatbot -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test health endpoint
curl http://$IP/health

# Test with domain (after DNS propagation)
curl https://chatbot.yourdomain.com/health
curl https://chatbot.yourdomain.com/api/chat -X POST -H "Content-Type: application/json" -d '{"message":"Hello"}'
```

---

## 📊 Monitoring

### Cloud Monitoring

GKE automatically exports metrics to Cloud Monitoring:

1. Go to Cloud Console → Monitoring → Dashboards
2. Create custom dashboard with:
   - Pod CPU/Memory usage
   - Request rate
   - Error rate
   - Latency

### Prometheus Integration

Pods are annotated for Prometheus scraping:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

### Logging

View logs in Cloud Logging:

```bash
# View API logs
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=bmc-chatbot AND resource.labels.container_name=api-server" \
    --limit 50 \
    --format json

# View webhook logs
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=bmc-chatbot AND resource.labels.container_name=webhooks" \
    --limit 50 \
    --format json
```

### Health Checks

Built-in health checks:

- **API Server**: `GET /health`
- **Webhooks**: `GET /health`
- **Agents**: Process check via liveness probe

### Alerts

Set up Cloud Monitoring alerts for:

```bash
# Example: Create alert for high error rate
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="BMC Chatbot High Error Rate" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=5 \
    --condition-threshold-duration=300s
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Pods Not Starting

```bash
# Check pod status
kubectl describe pod -n bmc-chatbot <pod-name>

# Check events
kubectl get events -n bmc-chatbot --sort-by='.lastTimestamp'

# Common causes:
# - Image pull errors (check Artifact Registry permissions)
# - Resource constraints (adjust requests/limits)
# - Secret not found (verify External Secrets)
```

#### 2. Secrets Not Syncing

```bash
# Check ExternalSecret status
kubectl describe externalsecret bmc-chatbot-secrets -n bmc-chatbot

# Check SecretStore
kubectl describe secretstore gcpsm-secret-store -n bmc-chatbot

# Verify IAM permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:external-secrets@$PROJECT_ID.iam.gserviceaccount.com"

# Force secret refresh
kubectl annotate externalsecret bmc-chatbot-secrets -n bmc-chatbot \
    force-sync=$(date +%s) --overwrite
```

#### 3. Ingress Not Working

```bash
# Check ingress status
kubectl describe ingress bmc-chatbot-ingress -n bmc-chatbot

# Check ManagedCertificate status (can take 15+ minutes)
kubectl describe managedcertificate bmc-chatbot-cert -n bmc-chatbot

# Verify DNS
dig chatbot.yourdomain.com

# Check backend health
kubectl get backendconfig bmc-chatbot-backend-config -n bmc-chatbot -o yaml
```

#### 4. CronJobs Not Running

```bash
# Check CronJob status
kubectl get cronjobs -n bmc-chatbot

# Check last job execution
kubectl get jobs -n bmc-chatbot

# View job logs
kubectl logs -n bmc-chatbot job/<job-name>

# Manually trigger a job
kubectl create job --from=cronjob/product-mapper manual-run -n bmc-chatbot
```

#### 5. Database Connection Issues

```bash
# Test MongoDB connectivity from a pod
kubectl run -it --rm debug --image=mongo:latest --restart=Never -n bmc-chatbot -- \
    mongosh "$MONGODB_URI"

# Check if secret is properly mounted
kubectl exec -n bmc-chatbot <pod-name> -- env | grep MONGODB_URI
```

### Debug Commands

```bash
# Get detailed pod information
kubectl get pod <pod-name> -n bmc-chatbot -o yaml

# Execute commands in pod
kubectl exec -it <pod-name> -n bmc-chatbot -- /bin/bash

# Port forward for local testing
kubectl port-forward -n bmc-chatbot svc/api-service 8000:80

# Check resource usage
kubectl top pods -n bmc-chatbot
kubectl top nodes
```

---

## 📈 Scaling

### Horizontal Scaling

#### Manual Scaling

```bash
# Scale API servers
kubectl scale deployment api-server -n bmc-chatbot --replicas=4

# Scale webhooks
kubectl scale deployment webhooks -n bmc-chatbot --replicas=3
```

#### Auto-scaling with HPA

Create HorizontalPodAutoscaler:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-server-hpa
  namespace: bmc-chatbot
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

Apply:

```bash
kubectl apply -f api-server-hpa.yaml
kubectl get hpa -n bmc-chatbot -w
```

### Vertical Scaling

Update resource requests/limits in deployment files:

```bash
# Edit deployment
kubectl edit deployment api-server -n bmc-chatbot

# Or patch directly
kubectl patch deployment api-server -n bmc-chatbot -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "api-server",
          "resources": {
            "requests": {"memory": "512Mi", "cpu": "500m"},
            "limits": {"memory": "1Gi", "cpu": "1000m"}
          }
        }]
      }
    }
  }
}'
```

---

## 🔄 Updates & Rollbacks

### Update Container Images

```bash
# Build new image with version tag
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/api-server:v1.1.0 .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/api-server:v1.1.0

# Update deployment
kubectl set image deployment/api-server \
    api-server=$REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/api-server:v1.1.0 \
    -n bmc-chatbot

# Monitor rollout
kubectl rollout status deployment/api-server -n bmc-chatbot

# Check rollout history
kubectl rollout history deployment/api-server -n bmc-chatbot
```

### Rolling Updates

```bash
# Apply updated manifest
kubectl apply -f api-deployment.yaml

# Watch rolling update
kubectl rollout status deployment/api-server -n bmc-chatbot -w
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/api-server -n bmc-chatbot

# Rollback to specific revision
kubectl rollout undo deployment/api-server -n bmc-chatbot --to-revision=2

# Check rollback status
kubectl rollout status deployment/api-server -n bmc-chatbot
```

### Blue-Green Deployment

For zero-downtime deployments:

```bash
# Create new deployment with v2
kubectl apply -f api-deployment-v2.yaml

# Test v2
kubectl port-forward deployment/api-server-v2 8080:8000 -n bmc-chatbot

# Switch service to v2
kubectl patch service api-service -n bmc-chatbot -p '{"spec":{"selector":{"version":"v2"}}}'

# Delete old deployment
kubectl delete deployment api-server -n bmc-chatbot
```

---

## 🔒 Security

### Best Practices

1. **Secrets Management**
   - ✅ Use External Secrets Operator
   - ✅ Store secrets in Google Secret Manager
   - ❌ Never commit secrets to Git
   - ✅ Rotate secrets regularly

2. **Network Security**
   - ✅ Use HTTPS everywhere (managed certificates)
   - ✅ Enable Cloud Armor for DDoS protection
   - ✅ Configure Network Policies
   - ✅ Use Private GKE cluster (for production)

3. **Pod Security**
   - ✅ Run as non-root user
   - ✅ Drop all capabilities
   - ✅ Use read-only root filesystem (where possible)
   - ✅ Set resource limits

4. **Authentication & Authorization**
   - ✅ Use Workload Identity
   - ✅ Implement least privilege IAM
   - ✅ Enable Binary Authorization (optional)
   - ✅ Use IAP for admin endpoints (optional)

### Enable Cloud Armor

Create security policy:

```bash
gcloud compute security-policies create bmc-chatbot-armor-policy \
    --description "Cloud Armor policy for BMC Chatbot"

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
    --security-policy bmc-chatbot-armor-policy \
    --expression "true" \
    --action "rate-based-ban" \
    --rate-limit-threshold-count 100 \
    --rate-limit-threshold-interval-sec 60 \
    --ban-duration-sec 600

# Apply to ingress (update ingress.yaml annotation)
# cloud.google.com/armor-config: '{"bmc-chatbot-security-policy": "bmc-chatbot-armor-policy"}'
```

### Network Policies

Restrict pod-to-pod communication:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-server-netpol
  namespace: bmc-chatbot
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: api-server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: TCP
      port: 27017  # MongoDB
```

### Audit Logging

Enable GKE audit logs:

```bash
gcloud container clusters update $CLUSTER_NAME \
    --region=$REGION \
    --enable-cloud-logging \
    --logging=SYSTEM,WORKLOAD \
    --enable-cloud-monitoring \
    --monitoring=SYSTEM
```

---

## 📚 Additional Resources

- [GKE Autopilot Documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)
- [External Secrets Operator](https://external-secrets.io/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Google Cloud Architecture Framework](https://cloud.google.com/architecture/framework)

---

## 🆘 Support

For issues or questions:

1. Check logs: `kubectl logs -n bmc-chatbot <pod-name>`
2. Review events: `kubectl get events -n bmc-chatbot`
3. Check Cloud Monitoring dashboards
4. Review this documentation

---

## 📝 License

See main repository LICENSE file.
