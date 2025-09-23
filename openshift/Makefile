# Makefile for WhatsApp MCP OpenShift deployment

# Configuration
NAMESPACE ?= whatsapp-mcp
BRIDGE_IMAGE ?= whatsapp-bridge
MCP_IMAGE ?= whatsapp-mcp-server
TAG ?= latest

# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help build deploy undeploy status logs clean

help: ## Show this help message
	@echo "WhatsApp MCP OpenShift Deployment"
	@echo "================================="
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build container images from GitHub
	@echo "$(YELLOW)Building container images from GitHub...$(NC)"
	@./build-images.sh

build-local: ## Build container images from local source (requires local files)
	@echo "$(YELLOW)Building container images from local source...$(NC)"
	@echo "$(RED)Note: This requires local source files. Use 'make build' for GitHub-based builds.$(NC)"
	@cd ../whatsapp-bridge && oc new-build --name=whatsapp-bridge --strategy=docker --binary=true --to=whatsapp-bridge:latest
	@cd ../whatsapp-bridge && oc start-build whatsapp-bridge --from-dir=. --follow
	@cd ../whatsapp-mcp-server && oc new-build --name=whatsapp-mcp-server --strategy=docker --binary=true --to=whatsapp-mcp-server:latest
	@cd ../whatsapp-mcp-server && oc start-build whatsapp-mcp-server --from-dir=. --follow

deploy: ## Deploy the application
	@echo "$(YELLOW)Deploying application...$(NC)"
	@./deploy.sh

undeploy: ## Remove the application
	@echo "$(YELLOW)Undeploying application...$(NC)"
	@./undeploy.sh

status: ## Show deployment status
	@echo "$(YELLOW)Deployment Status:$(NC)"
	@oc get pods -l app=whatsapp-mcp -n $(NAMESPACE) 2>/dev/null || echo "No pods found"
	@echo ""
	@echo "$(YELLOW)Services:$(NC)"
	@oc get services -l app=whatsapp-mcp -n $(NAMESPACE) 2>/dev/null || echo "No services found"
	@echo ""
	@echo "$(YELLOW)Routes:$(NC)"
	@oc get routes -l app=whatsapp-mcp -n $(NAMESPACE) 2>/dev/null || echo "No routes found"

logs: ## Show application logs
	@echo "$(YELLOW)WhatsApp Bridge logs:$(NC)"
	@oc logs -l app=whatsapp-mcp -c whatsapp-bridge -n $(NAMESPACE) --tail=20 2>/dev/null || echo "No logs found"
	@echo ""
	@echo "$(YELLOW)MCP Server logs:$(NC)"
	@oc logs -l app=whatsapp-mcp -c whatsapp-mcp-server -n $(NAMESPACE) --tail=20 2>/dev/null || echo "No logs found"

logs-follow: ## Follow application logs
	@echo "$(YELLOW)Following logs (Ctrl+C to stop)...$(NC)"
	@oc logs -l app=whatsapp-mcp -n $(NAMESPACE) -f

clean: ## Clean up build artifacts
	@echo "$(YELLOW)Cleaning up...$(NC)"
	@oc delete buildconfig --all -n $(NAMESPACE) 2>/dev/null || true
	@oc delete imagestream --all -n $(NAMESPACE) 2>/dev/null || true

restart: ## Restart the deployment
	@echo "$(YELLOW)Restarting deployment...$(NC)"
	@oc rollout restart deployment/whatsapp-mcp -n $(NAMESPACE)

scale: ## Scale the deployment (usage: make scale REPLICAS=2)
	@echo "$(YELLOW)Scaling deployment to $(REPLICAS) replicas...$(NC)"
	@oc scale deployment/whatsapp-mcp --replicas=$(REPLICAS) -n $(NAMESPACE)

port-forward: ## Port forward to the services
	@echo "$(YELLOW)Port forwarding (Ctrl+C to stop)...$(NC)"
	@echo "Bridge: http://localhost:8080"
	@echo "MCP: http://localhost:3000"
	@oc port-forward -n $(NAMESPACE) service/whatsapp-mcp-service 8080:8080 3000:3000

all: build deploy ## Build and deploy everything

# Development targets
dev-build: ## Build images for development
	@echo "$(YELLOW)Building development images...$(NC)"
	@TAG=dev ./build-images.sh

dev-deploy: ## Deploy development version
	@echo "$(YELLOW)Deploying development version...$(NC)"
	@TAG=dev ./deploy.sh

# Production targets
prod-build: ## Build images for production
	@echo "$(YELLOW)Building production images...$(NC)"
	@TAG=prod ./build-images.sh

prod-deploy: ## Deploy production version
	@echo "$(YELLOW)Deploying production version...$(NC)"
	@TAG=prod ./deploy.sh
