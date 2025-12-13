# GKE Deployment Checklist

Use this checklist to ensure a successful deployment of the BMC Chatbot system on GKE.

## Pre-Deployment Checklist

### ☐ 1. Prerequisites

- [ ] GCP project created and billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] `kubectl` installed
- [ ] `docker` installed
- [ ] Domain name registered (for production)
- [ ] Project ID noted: `_______________________`

### ☐ 2. Enable GCP APIs

```bash
gcloud services enable container.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable compute.googleapis.com
```

- [ ] Container API enabled
- [ ] Artifact Registry API enabled
- [ ] Secret Manager API enabled
- [ ] Compute Engine API enabled

### ☐ 3. Prepare Secrets

Collect all required credentials:

- [ ] OpenAI API key: `sk-...`
- [ ] MongoDB URI: `mongodb+srv://...`
- [ ] WhatsApp access token (if using)
- [ ] WhatsApp verify token (if using)
- [ ] WhatsApp phone number ID (if using)
- [ ] Admin password
- [ ] Groq API key (optional)
- [ ] Gemini API key (optional)
- [ ] N8N webhook URL (optional)
- [ ] PostgreSQL URI (optional)
- [ ] Google Sheets credentials (optional)

## Infrastructure Setup

### ☐ 4. Create GKE Cluster

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export CLUSTER_NAME="bmc-chatbot-cluster"

gcloud container clusters create-auto $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --release-channel=regular \
    --enable-autoscaling \
    --enable-autorepair \
    --enable-autoupgrade \
    --workload-pool=$PROJECT_ID.svc.id.goog
```

- [ ] Cluster created successfully
- [ ] Cluster name: `_______________________`
- [ ] Region: `_______________________`

### ☐ 5. Configure kubectl

```bash
gcloud container clusters get-credentials $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID
```

- [ ] kubectl configured
- [ ] Can list nodes: `kubectl get nodes`

### ☐ 6. Create Artifact Registry

```bash
gcloud artifacts repositories create bmc-chatbot \
    --repository-format=docker \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="BMC Chatbot container images"
```

- [ ] Repository created
- [ ] Docker auth configured: `gcloud auth configure-docker ${REGION}-docker.pkg.dev`

### ☐ 7. Setup IAM and Service Accounts

```bash
# Create service accounts
gcloud iam service-accounts create external-secrets \
    --project=$PROJECT_ID

gcloud iam service-accounts create bmc-chatbot \
    --project=$PROJECT_ID

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:external-secrets@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Setup Workload Identity
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

- [ ] Service accounts created
- [ ] IAM permissions granted
- [ ] Workload Identity configured

### ☐ 8. Install External Secrets Operator

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm repo update

helm install external-secrets \
    external-secrets/external-secrets \
    --namespace external-secrets-system \
    --create-namespace \
    --set installCRDs=true
```

- [ ] Helm repo added
- [ ] External Secrets Operator installed
- [ ] Verify: `kubectl get pods -n external-secrets-system`

### ☐ 9. Store Secrets in Google Secret Manager

```bash
# OpenAI
echo -n "sk-your-key" | gcloud secrets create openai-api-key \
    --data-file=- --project=$PROJECT_ID

# MongoDB
echo -n "mongodb+srv://..." | gcloud secrets create mongodb-uri \
    --data-file=- --project=$PROJECT_ID

# WhatsApp
echo -n "your-token" | gcloud secrets create whatsapp-token \
    --data-file=- --project=$PROJECT_ID

echo -n "verify-token" | gcloud secrets create whatsapp-verify-token \
    --data-file=- --project=$PROJECT_ID

echo -n "phone-id" | gcloud secrets create whatsapp-phone-number-id \
    --data-file=- --project=$PROJECT_ID

# Admin
echo -n "SecurePass123!" | gcloud secrets create admin-password \
    --data-file=- --project=$PROJECT_ID

# Optional: Groq, Gemini, N8N, PostgreSQL, etc.
```

- [ ] OpenAI API key stored
- [ ] MongoDB URI stored
- [ ] WhatsApp credentials stored
- [ ] Admin password stored
- [ ] Optional credentials stored
- [ ] Verify: `gcloud secrets list --project=$PROJECT_ID`

### ☐ 10. Create Static IP

```bash
gcloud compute addresses create bmc-chatbot-ip \
    --global \
    --project=$PROJECT_ID

# Get IP
gcloud compute addresses describe bmc-chatbot-ip --global --format="value(address)"
```

- [ ] Static IP created
- [ ] IP address: `_______________________`

### ☐ 11. Configure DNS

- [ ] Created A record pointing to static IP
- [ ] Domain: `_______________________`
- [ ] DNS propagated (check with `nslookup`)

## Build & Deploy

### ☐ 12. Update Configuration Files

```bash
cd k8s/

# Replace PROJECT_ID
find . -name "*.yaml" -type f -exec sed -i "s/PROJECT_ID/$PROJECT_ID/g" {} +

# Update domain in ingress.yaml
sed -i "s/chatbot.yourdomain.com/your-actual-domain.com/g" ingress.yaml
```

- [ ] PROJECT_ID replaced in all files
- [ ] Domain updated in ingress.yaml
- [ ] Allowed origins updated in api-deployment.yaml

### ☐ 13. Build Docker Images

```bash
# Using helper script
export VERSION="v1.0.0"
./build-and-push.sh
```

Or manually:

```bash
# API Server
docker build -f k8s/Dockerfile.api \
    -t $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/api-server:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/api-server:latest

# Agents
docker build -f k8s/Dockerfile.agents \
    -t $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/agents:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/agents:latest

# Webhooks
docker build -f k8s/Dockerfile.webhooks \
    -t $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/webhooks:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/bmc-chatbot/webhooks:latest
```

- [ ] API server image built and pushed
- [ ] Agents image built and pushed
- [ ] Webhooks image built and pushed
- [ ] Images visible in Artifact Registry

### ☐ 14. Deploy to Kubernetes

```bash
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f api-service.yaml
kubectl apply -f agents-deployment.yaml
kubectl apply -f webhooks-deployment.yaml
kubectl apply -f webhooks-service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f cronjobs.yaml
```

- [ ] Namespace created
- [ ] Secrets configured
- [ ] API deployment created
- [ ] API service created
- [ ] Agents deployment created
- [ ] Webhooks deployment created
- [ ] Webhooks service created
- [ ] Ingress created
- [ ] CronJobs created

## Verification

### ☐ 15. Verify Deployments

```bash
kubectl get all -n bmc-chatbot
```

- [ ] All pods are Running
- [ ] Services are created
- [ ] Ingress has IP assigned

### ☐ 16. Check Pods

```bash
kubectl get pods -n bmc-chatbot
```

Expected pods:
- [ ] `api-server-xxx` (2 replicas)
- [ ] `webhooks-xxx` (2 replicas)
- [ ] `agents-xxx` (1 replica)

### ☐ 17. Check Secrets

```bash
kubectl get externalsecrets -n bmc-chatbot
kubectl describe externalsecret bmc-chatbot-secrets -n bmc-chatbot
```

- [ ] ExternalSecret status is "SecretSynced"
- [ ] Secret `bmc-chatbot-secrets` exists

### ☐ 18. Check Logs

```bash
# API Server
kubectl logs -n bmc-chatbot -l app.kubernetes.io/name=api-server --tail=50

# Webhooks
kubectl logs -n bmc-chatbot -l app.kubernetes.io/name=webhooks --tail=50

# Agents
kubectl logs -n bmc-chatbot -l app.kubernetes.io/name=agents --tail=50
```

- [ ] No error logs in API server
- [ ] No error logs in webhooks
- [ ] No error logs in agents
- [ ] MongoDB connection successful
- [ ] OpenAI API connection successful

### ☐ 19. Test Endpoints

```bash
# Get ingress IP
INGRESS_IP=$(kubectl get ingress bmc-chatbot-ingress -n bmc-chatbot -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test health endpoint
curl http://$INGRESS_IP/health
```

- [ ] Health endpoint responds with 200 OK
- [ ] Health endpoint shows "healthy" status

### ☐ 20. Test SSL Certificate (wait 15+ minutes)

```bash
kubectl get managedcertificate bmc-chatbot-cert -n bmc-chatbot
```

- [ ] Certificate status is "Active"
- [ ] HTTPS works: `curl https://your-domain.com/health`

### ☐ 21. Test API Endpoints

```bash
# Chat endpoint
curl -X POST https://your-domain.com/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"Hello, what products do you offer?"}'
```

- [ ] Chat endpoint works
- [ ] Gets response from AI

### ☐ 22. Verify CronJobs

```bash
kubectl get cronjobs -n bmc-chatbot
```

- [ ] `product-mapper` CronJob exists
- [ ] `followup-agent` CronJob exists
- [ ] `repo-research` CronJob exists

### ☐ 23. Manual CronJob Test

```bash
# Test product mapper
kubectl create job --from=cronjob/product-mapper manual-test -n bmc-chatbot

# Check logs
kubectl logs -n bmc-chatbot job/manual-test
```

- [ ] Manual job completes successfully
- [ ] No errors in job logs

## Post-Deployment

### ☐ 24. Setup Monitoring

- [ ] Access Cloud Monitoring dashboard
- [ ] Create custom dashboard for BMC Chatbot
- [ ] Add CPU/Memory metrics
- [ ] Add request rate metrics
- [ ] Add error rate metrics

### ☐ 25. Setup Alerting

- [ ] Create alert for pod crashes
- [ ] Create alert for high error rate
- [ ] Create alert for high latency
- [ ] Create alert for resource usage
- [ ] Configure notification channels

### ☐ 26. Setup Log Aggregation

- [ ] Verify logs in Cloud Logging
- [ ] Create log-based metrics
- [ ] Setup log exports (if needed)

### ☐ 27. Security Review

- [ ] Secrets not exposed in logs
- [ ] HTTPS enforced
- [ ] Network policies applied (optional)
- [ ] Cloud Armor configured (optional)
- [ ] Workload Identity working

### ☐ 28. Performance Testing

- [ ] Load test API endpoints
- [ ] Verify auto-scaling works
- [ ] Check response times
- [ ] Monitor resource usage

### ☐ 29. Documentation

- [ ] Update team documentation
- [ ] Document custom configurations
- [ ] Document operational procedures
- [ ] Create runbook for common issues

### ☐ 30. Backup & Recovery

- [ ] MongoDB backup strategy in place
- [ ] Disaster recovery plan documented
- [ ] Test restoration procedure

## Ongoing Maintenance

### Regular Tasks

- [ ] Monitor logs daily
- [ ] Check resource usage weekly
- [ ] Review alerts weekly
- [ ] Update images monthly
- [ ] Rotate secrets quarterly
- [ ] Review IAM permissions quarterly
- [ ] Test disaster recovery annually

### Update Checklist

When deploying updates:

1. [ ] Build new image with version tag
2. [ ] Push to Artifact Registry
3. [ ] Test image locally/staging
4. [ ] Update deployment manifest
5. [ ] Apply with `kubectl apply`
6. [ ] Monitor rollout
7. [ ] Verify health endpoints
8. [ ] Check logs for errors
9. [ ] Rollback if needed

## Notes

Deployment Date: `_______________________`
Deployed By: `_______________________`
Version: `_______________________`

Additional Notes:
```
_____________________________________________________________________________

_____________________________________________________________________________

_____________________________________________________________________________
```

## Status

- [ ] ✅ Deployment Complete
- [ ] ⚠️  Deployment Partial (note issues above)
- [ ] ❌ Deployment Failed (note reasons above)
