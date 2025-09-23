#!/bin/bash

# Undeployment script for WhatsApp MCP from OpenShift
# This script removes the complete application stack

set -e

# Configuration
NAMESPACE=${NAMESPACE:-whatsapp-mcp}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Undeploying WhatsApp MCP from OpenShift...${NC}"

# Check if we're logged into OpenShift
if ! oc whoami &> /dev/null; then
    echo -e "${RED}Error: Not logged into OpenShift. Please run 'oc login' first.${NC}"
    exit 1
fi

# Switch to the namespace
oc project ${NAMESPACE} 2>/dev/null || {
    echo -e "${RED}Error: Namespace ${NAMESPACE} does not exist.${NC}"
    exit 1
}

# Remove Route
echo -e "${YELLOW}Removing Route...${NC}"
oc delete -f route.yaml --ignore-not-found=true

# Remove Service
echo -e "${YELLOW}Removing Service...${NC}"
oc delete -f service.yaml --ignore-not-found=true

# Remove Deployment
echo -e "${YELLOW}Removing Deployment...${NC}"
oc delete -f deployment.yaml --ignore-not-found=true

# Remove ConfigMap
echo -e "${YELLOW}Removing ConfigMap...${NC}"
oc delete -f configmap.yaml --ignore-not-found=true

# Remove PVC (with confirmation)
echo -e "${YELLOW}Removing PersistentVolumeClaim...${NC}"
read -p "Do you want to delete the persistent volume claims? This will remove all WhatsApp data! (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    oc delete -f pvc.yaml --ignore-not-found=true
    echo -e "${RED}Persistent volume claims deleted. All WhatsApp data has been removed.${NC}"
else
    echo -e "${YELLOW}Persistent volume claims preserved.${NC}"
fi

# Remove ServiceAccount and RBAC
echo -e "${YELLOW}Removing ServiceAccount and RBAC...${NC}"
oc delete serviceaccount whatsapp-mcp --ignore-not-found=true
oc delete role whatsapp-mcp-role --ignore-not-found=true
oc delete rolebinding whatsapp-mcp-rolebinding --ignore-not-found=true

# Remove BuildConfigs and Images
echo -e "${YELLOW}Removing BuildConfigs and Images...${NC}"
oc delete -f buildconfig.yaml --ignore-not-found=true
oc delete buildconfig whatsapp-bridge --ignore-not-found=true
oc delete buildconfig whatsapp-mcp-server --ignore-not-found=true
oc delete imagestream whatsapp-bridge --ignore-not-found=true
oc delete imagestream whatsapp-mcp-server --ignore-not-found=true

# Remove namespace (optional)
read -p "Do you want to delete the namespace ${NAMESPACE}? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    oc delete namespace ${NAMESPACE}
    echo -e "${GREEN}Namespace ${NAMESPACE} deleted.${NC}"
else
    echo -e "${YELLOW}Namespace ${NAMESPACE} preserved.${NC}"
fi

echo -e "${GREEN}Undeployment completed successfully!${NC}"
