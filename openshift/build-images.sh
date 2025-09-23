#!/bin/bash

# Build script for WhatsApp MCP OpenShift deployment
# This script builds both container images from GitHub repository

set -e

# Configuration
NAMESPACE=${NAMESPACE:-whatsapp-mcp}
REGISTRY=${REGISTRY:-image-registry.openshift-image-registry.svc:5000}
BRIDGE_IMAGE=${BRIDGE_IMAGE:-whatsapp-bridge}
MCP_IMAGE=${MCP_IMAGE:-whatsapp-mcp-server}
TAG=${TAG:-latest}
GITHUB_REPO=${GITHUB_REPO:-https://github.com/akram/whatsapp-mcp.git}
GITHUB_REF=${GITHUB_REF:-main}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building WhatsApp MCP container images from GitHub...${NC}"
echo -e "${YELLOW}Repository: ${GITHUB_REPO}${NC}"
echo -e "${YELLOW}Branch/Ref: ${GITHUB_REF}${NC}"

# Check if we're logged into OpenShift
if ! oc whoami &> /dev/null; then
    echo -e "${RED}Error: Not logged into OpenShift. Please run 'oc login' first.${NC}"
    exit 1
fi

# Create namespace if it doesn't exist
echo -e "${YELLOW}Creating namespace: ${NAMESPACE}${NC}"
oc create namespace ${NAMESPACE} --dry-run=client -o yaml | oc apply -f -

# Switch to the namespace
oc project ${NAMESPACE}

# Apply BuildConfigs
echo -e "${YELLOW}Applying BuildConfigs...${NC}"
oc apply -f buildconfig.yaml

# Start builds from GitHub
echo -e "${YELLOW}Starting WhatsApp Bridge build from GitHub...${NC}"
oc start-build ${BRIDGE_IMAGE} --follow

echo -e "${YELLOW}Starting MCP Server build from GitHub...${NC}"
oc start-build ${MCP_IMAGE} --follow

echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "${YELLOW}Images built:${NC}"
echo "  - ${REGISTRY}/${NAMESPACE}/${BRIDGE_IMAGE}:${TAG}"
echo "  - ${REGISTRY}/${NAMESPACE}/${MCP_IMAGE}:${TAG}"

# Show build status
echo -e "${YELLOW}Build status:${NC}"
oc get builds -n ${NAMESPACE}

# Show ImageStreams
echo -e "${YELLOW}ImageStreams:${NC}"
oc get imagestreams -n ${NAMESPACE}
