#!/bin/bash

# Deployment script for WhatsApp MCP on OpenShift
# This script deploys the complete application stack

set -e

# Configuration
NAMESPACE=${NAMESPACE:-whatsapp-mcp}
BRIDGE_IMAGE=${BRIDGE_IMAGE:-whatsapp-bridge}
MCP_IMAGE=${MCP_IMAGE:-whatsapp-mcp-server}
TAG=${TAG:-latest}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying WhatsApp MCP to OpenShift...${NC}"

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

# Create ServiceAccount
echo -e "${YELLOW}Creating ServiceAccount...${NC}"
cat <<EOF | oc apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: whatsapp-mcp
  namespace: ${NAMESPACE}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: ${NAMESPACE}
  name: whatsapp-mcp-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: whatsapp-mcp-rolebinding
  namespace: ${NAMESPACE}
subjects:
- kind: ServiceAccount
  name: whatsapp-mcp
  namespace: ${NAMESPACE}
roleRef:
  kind: Role
  name: whatsapp-mcp-role
  apiGroup: rbac.authorization.k8s.io
EOF

# Apply webhook secret
echo -e "${YELLOW}Applying webhook secret...${NC}"
oc apply -f webhook-secret.yaml

# Apply BuildConfigs first
echo -e "${YELLOW}Applying BuildConfigs...${NC}"
oc apply -f buildconfig.yaml

# Apply ConfigMap
echo -e "${YELLOW}Applying ConfigMap...${NC}"
oc apply -f configmap.yaml

# Note: Using emptyDir volumes instead of PVCs for simplicity

# Apply deployment (images will be pulled from ImageStreams)
echo -e "${YELLOW}Applying deployment...${NC}"
oc apply -f deployment.yaml

# Apply Service
echo -e "${YELLOW}Applying Service...${NC}"
oc apply -f service.yaml

# Apply Route
echo -e "${YELLOW}Applying Route...${NC}"
oc apply -f route.yaml

# Wait for deployment to be ready
echo -e "${YELLOW}Waiting for deployment to be ready...${NC}"
oc rollout status deployment/whatsapp-mcp --timeout=300s

# Show deployment status
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${BLUE}Deployment status:${NC}"
oc get pods -l app=whatsapp-mcp
oc get services -l app=whatsapp-mcp
oc get routes -l app=whatsapp-mcp

# Show logs
echo -e "${YELLOW}Recent logs from WhatsApp Bridge:${NC}"
oc logs -l app=whatsapp-mcp -c whatsapp-bridge --tail=10

echo -e "${YELLOW}Recent logs from MCP Server:${NC}"
oc logs -l app=whatsapp-mcp -c whatsapp-mcp-server --tail=10

echo -e "${GREEN}WhatsApp MCP is now deployed and running!${NC}"
echo -e "${BLUE}Access the application via the routes shown above.${NC}"
