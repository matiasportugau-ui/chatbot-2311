# BMC Chatbot GKE - Quick Reference

Quick commands for common operations.

## 🚀 Initial Setup

```bash
# Set environment variables
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export CLUSTER_NAME="bmc-chatbot-cluster"

# Create GKE Autopilot cluster
gcloud container clusters create-auto $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID

# Get credentials
gcloud container clusters get-credentials $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID

# Create Artifact Registry
gcloud artifacts repositories create bmc-chatbot \
    --repository-format=docker \
    --location=$REGION \
    --project=$PROJECT_ID
```

## 🔐 Secrets Setup

```bash
# Store secrets in Google Secret Manager
echo -n "sk-your-key" | gcloud secrets create openai-api-key --data-file=- --project=$PROJECT_ID
echo -n "mongodb+srv://..." | gcloud secrets create mongodb-uri --data-file=- --project=$PROJECT_ID
echo -n "your-token" | gcloud secrets create whatsapp-token --data-file=- --project=$PROJECT_ID
echo -n "your-password" | gcloud secrets create admin-password --data-file=- --project=$PROJECT_ID
```

## 🐳 Build & Push Images

```bash
# Using the helper script
cd k8s/
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export VERSION="v1.0.0"  # or "latest"
./build-and-push.sh

# Manual build
docker build -f k8s/Dockerfile.api -t $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/api-server:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/api-server:latest
```

## 📦 Deployment

```bash
# Update manifests with your PROJECT_ID
cd k8s/
find . -name "*.yaml" -type f -exec sed -i "s/PROJECT_ID/$PROJECT_ID/g" {} +

# Deploy everything
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f api-service.yaml
kubectl apply -f agents-deployment.yaml
kubectl apply -f webhooks-deployment.yaml
kubectl apply -f webhooks-service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f cronjobs.yaml

# Or deploy all at once
kubectl apply -f .
```

## 🔍 Monitoring

```bash
# Get all resources
kubectl get all -n bmc-chatbot

# Get pods
kubectl get pods -n bmc-chatbot
kubectl get pods -n bmc-chatbot -w  # watch

# Get services
kubectl get svc -n bmc-chatbot

# Get ingress
kubectl get ingress -n bmc-chatbot

# Check secrets sync
kubectl get externalsecrets -n bmc-chatbot
kubectl describe externalsecret bmc-chatbot-secrets -n bmc-chatbot

# Check cronjobs
kubectl get cronjobs -n bmc-chatbot
kubectl get jobs -n bmc-chatbot
```

## 📝 Logs

```bash
# API server logs
kubectl logs -n bmc-chatbot -l app.kubernetes.io/name=api-server -f

# Webhooks logs
kubectl logs -n bmc-chatbot -l app.kubernetes.io/name=webhooks -f

# Agents logs
kubectl logs -n bmc-chatbot -l app.kubernetes.io/name=agents -f

# Specific pod logs
kubectl logs -n bmc-chatbot <pod-name> -f

# Previous logs (if crashed)
kubectl logs -n bmc-chatbot <pod-name> --previous

# CronJob logs
kubectl logs -n bmc-chatbot job/product-mapper-<timestamp> --tail=100
```

## 🔧 Debugging

```bash
# Describe pod
kubectl describe pod -n bmc-chatbot <pod-name>

# Get events
kubectl get events -n bmc-chatbot --sort-by='.lastTimestamp'

# Execute commands in pod
kubectl exec -it -n bmc-chatbot <pod-name> -- /bin/bash

# Port forward
kubectl port-forward -n bmc-chatbot svc/api-service 8000:80

# Check resource usage
kubectl top pods -n bmc-chatbot
kubectl top nodes
```

## 🔄 Updates

```bash
# Update image
kubectl set image deployment/api-server \
    api-server=$REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/api-server:v1.1.0 \
    -n bmc-chatbot

# Watch rollout
kubectl rollout status deployment/api-server -n bmc-chatbot

# Rollout history
kubectl rollout history deployment/api-server -n bmc-chatbot

# Rollback
kubectl rollout undo deployment/api-server -n bmc-chatbot
```

## 📊 Scaling

```bash
# Scale manually
kubectl scale deployment api-server --replicas=4 -n bmc-chatbot

# Auto-scaling (create HPA)
kubectl autoscale deployment api-server \
    --cpu-percent=70 \
    --min=2 \
    --max=10 \
    -n bmc-chatbot

# Check HPA
kubectl get hpa -n bmc-chatbot
```

## 🧪 Testing

```bash
# Get ingress IP
kubectl get ingress bmc-chatbot-ingress -n bmc-chatbot

# Test health endpoint
curl http://<INGRESS-IP>/health

# Test API endpoint
curl https://chatbot.yourdomain.com/health
curl -X POST https://chatbot.yourdomain.com/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"Hello"}'

# Manually trigger CronJob
kubectl create job --from=cronjob/product-mapper manual-test -n bmc-chatbot
```

## 🗑️ Cleanup

```bash
# Delete all resources
kubectl delete namespace bmc-chatbot

# Delete cluster
gcloud container clusters delete $CLUSTER_NAME --region=$REGION --project=$PROJECT_ID

# Delete artifact registry
gcloud artifacts repositories delete bmc-chatbot --location=$REGION --project=$PROJECT_ID

# Delete static IP
gcloud compute addresses delete bmc-chatbot-ip --global --project=$PROJECT_ID
```

## 🆘 Troubleshooting

### Pods not starting
```bash
# Check pod events
kubectl describe pod -n bmc-chatbot <pod-name>

# Check logs
kubectl logs -n bmc-chatbot <pod-name>

# Check secrets
kubectl get secrets -n bmc-chatbot
kubectl describe externalsecret bmc-chatbot-secrets -n bmc-chatbot
```

### Secrets not syncing
```bash
# Check External Secrets Operator
kubectl get pods -n external-secrets-system

# Force secret refresh
kubectl annotate externalsecret bmc-chatbot-secrets -n bmc-chatbot \
    force-sync=$(date +%s) --overwrite

# Check IAM permissions
gcloud projects get-iam-policy $PROJECT_ID
```

### Ingress not working
```bash
# Check ingress status
kubectl describe ingress bmc-chatbot-ingress -n bmc-chatbot

# Check certificate status (takes 15+ minutes)
kubectl describe managedcertificate bmc-chatbot-cert -n bmc-chatbot

# Check backend config
kubectl describe backendconfig bmc-chatbot-backend-config -n bmc-chatbot

# Verify DNS
nslookup chatbot.yourdomain.com
```

### CronJob not running
```bash
# Check cronjob schedule
kubectl get cronjobs -n bmc-chatbot

# Check jobs
kubectl get jobs -n bmc-chatbot

# View job logs
kubectl logs -n bmc-chatbot job/<job-name>

# Manually trigger
kubectl create job --from=cronjob/product-mapper manual-run -n bmc-chatbot
```

## 📚 Additional Resources

- [GKE Autopilot Docs](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)
- [External Secrets](https://external-secrets.io/)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
