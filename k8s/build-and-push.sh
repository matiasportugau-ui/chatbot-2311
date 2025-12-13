#!/bin/bash
# BMC Chatbot - GKE Deployment Helper Script
# This script helps build and push Docker images to Google Artifact Registry

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

# Check if required environment variables are set
check_env_vars() {
    local missing_vars=()
    
    if [ -z "$PROJECT_ID" ]; then
        missing_vars+=("PROJECT_ID")
    fi
    
    if [ -z "$REGION" ]; then
        missing_vars+=("REGION")
    fi
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        echo ""
        echo "Please set them:"
        echo "  export PROJECT_ID='your-gcp-project-id'"
        echo "  export REGION='us-central1'"
        exit 1
    fi
}

# Check if required commands are available
check_requirements() {
    local missing_cmds=()
    
    if ! command -v gcloud &> /dev/null; then
        missing_cmds+=("gcloud")
    fi
    
    if ! command -v docker &> /dev/null; then
        missing_cmds+=("docker")
    fi
    
    if [ ${#missing_cmds[@]} -gt 0 ]; then
        print_error "Missing required commands:"
        for cmd in "${missing_cmds[@]}"; do
            echo "  - $cmd"
        done
        exit 1
    fi
}

# Build and push a Docker image
build_and_push() {
    local service=$1
    local dockerfile=$2
    local version=${3:-latest}
    
    local image_name="${REGION}-docker.pkg.dev/${PROJECT_ID}/bmc-chatbot/${service}:${version}"
    
    print_info "Building ${service} image..."
    
    # Build image
    docker build \
        -f "k8s/${dockerfile}" \
        -t "${image_name}" \
        --platform linux/amd64 \
        . || {
        print_error "Failed to build ${service} image"
        return 1
    }
    
    print_success "Built ${service} image"
    
    print_info "Pushing ${service} image to Artifact Registry..."
    
    # Push image
    docker push "${image_name}" || {
        print_error "Failed to push ${service} image"
        return 1
    }
    
    print_success "Pushed ${service} image: ${image_name}"
}

# Main script
main() {
    echo "=========================================="
    echo "BMC Chatbot - Docker Image Builder"
    echo "=========================================="
    echo ""
    
    # Check requirements
    print_info "Checking requirements..."
    check_requirements
    check_env_vars
    print_success "All requirements met"
    echo ""
    
    # Show configuration
    print_info "Configuration:"
    echo "  Project ID: $PROJECT_ID"
    echo "  Region: $REGION"
    echo ""
    
    # Get version tag (default to latest)
    VERSION=${VERSION:-latest}
    print_info "Building version: $VERSION"
    echo ""
    
    # Configure Docker for GCP
    print_info "Configuring Docker authentication..."
    gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet || {
        print_error "Failed to configure Docker authentication"
        exit 1
    }
    print_success "Docker authentication configured"
    echo ""
    
    # Build and push images
    print_info "Building and pushing images..."
    echo ""
    
    # API Server
    build_and_push "api-server" "Dockerfile.api" "$VERSION"
    echo ""
    
    # Agents
    build_and_push "agents" "Dockerfile.agents" "$VERSION"
    echo ""
    
    # Webhooks
    build_and_push "webhooks" "Dockerfile.webhooks" "$VERSION"
    echo ""
    
    print_success "All images built and pushed successfully!"
    echo ""
    echo "Images:"
    echo "  - ${REGION}-docker.pkg.dev/${PROJECT_ID}/bmc-chatbot/api-server:${VERSION}"
    echo "  - ${REGION}-docker.pkg.dev/${PROJECT_ID}/bmc-chatbot/agents:${VERSION}"
    echo "  - ${REGION}-docker.pkg.dev/${PROJECT_ID}/bmc-chatbot/webhooks:${VERSION}"
    echo ""
    echo "Next steps:"
    echo "  1. Update k8s manifests with correct PROJECT_ID"
    echo "  2. Create secrets in Google Secret Manager"
    echo "  3. Deploy to GKE: kubectl apply -f k8s/"
    echo ""
}

# Run main function
main
