# Docker Setup Review - BMC Chatbot Project
**Date:** December 1, 2025

## Executive Summary

Your Docker environment has **several critical issues** that need attention:
- ✅ MongoDB 7.0 is running correctly (`bmc-mongodb`)
- ❌ Main application services are **NOT running** (`bmc-chat-api`, `bmc-n8n`)
- ❌ Duplicate/orphaned MongoDB container running
- ❌ Many failed builds from unrelated projects
- ⚠️ Unnecessary Kubernetes cluster consuming resources

---

## Current Container Status

### ✅ **Correctly Running Containers**

| Container | Image | Status | Network | Purpose |
|-----------|-------|--------|---------|---------|
| `bmc-mongodb` | mongo:7.0 | Up 44 hours | `sistema-cotizaciones-bmc_bmc-network` | ✅ **Correct** - Main database |

### ❌ **Issues Found**

#### 1. **Orphaned MongoDB Container**
- **Container:** `compassionate_zhukovsky`
- **Image:** `mongo:latest` (MongoDB 8.2.2)
- **Status:** Running but **NOT in docker-compose.yml**
- **Network:** `bridge` (default, not on bmc-network)
- **Port:** No ports exposed (internal only)
- **Problem:** This is a duplicate/orphaned container that should be removed
- **Impact:** Wasting resources, potential confusion

#### 2. **Missing Application Services**
According to `docker-compose.yml`, these services should be running but are **NOT**:

| Service | Expected Container | Status | Issue |
|---------|-------------------|--------|-------|
| `chat-api` | `bmc-chat-api` | ❌ Not running | Main FastAPI backend missing |
| `n8n` | `bmc-n8n` | ❌ Not running | Workflow automation missing |

#### 3. **Unexpected Containers Running**

| Container | Purpose | Should Run? | Notes |
|-----------|---------|-------------|-------|
| `ollama` | Local LLM server | ⚠️ Maybe | Not in docker-compose.yml, may be for local testing |
| `elegant_mccarthy` | Python devcontainer | ❌ Stopped | Exited 5 hours ago - cleanup needed |
| 9x `kindest/node` | Kubernetes cluster | ❌ No | Not part of this project, consuming ~1.5GB RAM |

---

## Build Status Analysis

### Failed Builds (Recent)
- **4 failed builds** in last 3-4 days for `dev_containers_target_stage`
- **Many failed builds** 3 weeks ago for services like:
  - `apps/dashboard`
  - `services/quotation`
  - `apps/orchestrator/rasa/actions`
  - `packages/background-agents`

**Analysis:** These build names don't match your current project structure. They appear to be from a different project or an old architecture.

### Your Project Structure (from docker-compose.yml)
```
Expected Services:
├── mongodb (mongo:7.0) ✅ Running
├── chat-api (FastAPI) ❌ Not running
└── n8n (workflow) ❌ Not running
```

---

## Resource Usage

### High Resource Consumers
1. **Kind Control Plane** (`desktop-control-plane`): 238% CPU, 956MB RAM
2. **Kind Workers** (9 nodes): ~150-180MB RAM each = ~1.5GB total
3. **MongoDB 7.0** (`bmc-mongodb`): 87MB RAM, 4.4% CPU ✅ Normal
4. **MongoDB Latest** (`compassionate_zhukovsky`): 48MB RAM, 23% CPU ❌ Unnecessary

**Total Wasted Resources:** ~2GB RAM, significant CPU on unused Kubernetes cluster

---

## Network Analysis

### Networks in Use
| Network | Purpose | Containers |
|---------|---------|------------|
| `sistema-cotizaciones-bmc_bmc-network` | ✅ Main project network | `bmc-mongodb` |
| `bridge` | Default | `compassionate_zhukovsky` (orphaned) |
| `kind` | Kubernetes | 11 kind containers |
| `chatbot-full_default` | Empty | No containers |
| `chatbot_auto-atc-network` | Empty | No containers |
| `ultimate-chatbot` | Empty | No containers |

**Issue:** Multiple unused networks from previous projects.

---

## Volumes Analysis

### Named Volumes (Relevant)
- ✅ `mongodb_data` - Used by `bmc-mongodb`
- ✅ `ollama` - Used by Ollama container
- ✅ `chatbot_qdrant_data` - Vector database (if used)
- ✅ `ultimate-chatbot_n8n_data` - n8n data (if used)

### Anonymous Volumes
- 30+ anonymous volumes - many likely orphaned

---

## Recommendations

### 🔴 **Critical Actions (Do First)**

1. **Stop and remove orphaned MongoDB container:**
   ```bash
   docker stop compassionate_zhukovsky
   docker rm compassionate_zhukovsky
   ```

2. **Start your application services:**
   ```bash
   docker compose up -d
   ```
   This should start:
   - `bmc-chat-api` (FastAPI backend)
   - `bmc-n8n` (workflow automation)
   - Verify `bmc-mongodb` stays running

3. **Verify services are running:**
   ```bash
   docker compose ps
   ```

### 🟡 **Important Actions (Do Soon)**

4. **Clean up Kubernetes cluster (if not needed):**
   ```bash
   # If you don't need Kubernetes:
   kind delete cluster --name desktop  # or appropriate cluster name
   # Or stop all kind containers:
   docker stop $(docker ps -q --filter ancestor=kindest/node:v1.34.0)
   ```

5. **Remove stopped containers:**
   ```bash
   docker container prune -f
   ```

6. **Clean up unused networks:**
   ```bash
   docker network prune -f
   ```

7. **Clean up unused volumes (be careful!):**
   ```bash
   # Review first:
   docker volume ls
   # Then remove unused:
   docker volume prune -f
   ```

### 🟢 **Optional Actions (Maintenance)**

8. **Review and clean up failed builds:**
   - The failed builds appear to be from a different project
   - Consider cleaning up old build cache if needed

9. **Decide on Ollama:**
   - If you're using Ollama for local LLM, keep it
   - If not, stop and remove it:
     ```bash
     docker stop ollama
     docker rm ollama
     ```

10. **Update docker-compose.yml if needed:**
    - If Ollama should be part of your stack, add it to docker-compose.yml
    - Ensure all services are properly configured

---

## Expected State After Fixes

### Running Containers (Expected)
```
NAMES           STATUS    IMAGE              PORTS
bmc-mongodb     Up        mongo:7.0          0.0.0.0:27017->27017/tcp
bmc-chat-api    Up        bmc-chat-api:latest  0.0.0.0:8000->8000/tcp
bmc-n8n         Up        n8nio/n8n:latest   0.0.0.0:5678->5678/tcp
```

### Networks (Expected)
- `sistema-cotizaciones-bmc_bmc-network` with all 3 services connected

### Resource Usage (Expected)
- MongoDB: ~100MB RAM
- FastAPI: ~200-300MB RAM
- n8n: ~300-500MB RAM
- **Total: ~600-900MB** (vs current ~2.5GB+)

---

## Verification Checklist

After applying fixes, verify:

- [ ] `docker compose ps` shows all 3 services running
- [ ] `bmc-chat-api` responds at `http://localhost:8000`
- [ ] `bmc-n8n` accessible at `http://localhost:5678`
- [ ] `bmc-mongodb` accessible at `mongodb://localhost:27017`
- [ ] No orphaned MongoDB containers
- [ ] Resource usage reduced
- [ ] All services on correct network (`sistema-cotizaciones-bmc_bmc-network`)

---

## Configuration Check

### MongoDB Connection String
Your `docker-compose.yml` correctly configures:
- **Service name:** `mongodb` (internal DNS)
- **Connection:** `mongodb://mongodb:27017/bmc_chat`
- **Port mapping:** `27017:27017` (host:container)

### Environment Variables Needed
Ensure these are set in `.env`:
- `OPENAI_API_KEY` - Required for chat-api
- `OPENAI_MODEL` - Optional (defaults to gpt-4o-mini)

---

## Summary

**Current State:** ⚠️ **Partially Configured**
- Database running ✅
- Application services missing ❌
- Orphaned containers present ❌
- Unnecessary resources consumed ❌

**After Fixes:** ✅ **Fully Operational**
- All services running
- Clean environment
- Optimal resource usage

**Priority:** Start with Critical Actions #1-3 to get your application running.

