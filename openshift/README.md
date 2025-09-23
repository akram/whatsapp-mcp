# WhatsApp MCP OpenShift Deployment

This directory contains all the necessary files to deploy the WhatsApp MCP server on OpenShift as a containerized application.

## Architecture

The application consists of two containers running in the same pod:

1. **WhatsApp Bridge** (Go application) - Handles WhatsApp connectivity and message processing
2. **MCP Server** (Python application) - Provides the MCP interface for AI assistants

## Prerequisites

- OpenShift cluster with cluster admin access
- `oc` CLI tool installed and configured
- Access to the OpenShift internal registry

## Quick Start

### 1. Build Images from GitHub

The application builds directly from the GitHub repository [https://github.com/akram/whatsapp-mcp.git](https://github.com/akram/whatsapp-mcp.git):

```bash
# Make scripts executable
chmod +x *.sh

# Build container images from GitHub
./build-images.sh
```

This will:
- Clone the repository from GitHub
- Build the WhatsApp Bridge (Go) container from `whatsapp-bridge/` directory
- Build the MCP Server (Python) container from `whatsapp-mcp-server/` directory
- Push images to the OpenShift internal registry

### 2. Deploy Application

```bash
# Deploy the complete application stack
./deploy.sh
```

### Alternative: Build and Deploy in One Step

```bash
# Build and deploy everything
make all
```

### 3. Access the Application

After deployment, you can access the application via the routes:

- MCP Server: `https://whatsapp-mcp.apps.example.com`
- WhatsApp Bridge: `https://whatsapp-bridge.apps.example.com`

**Note**: Replace `apps.example.com` with your OpenShift cluster domain.

## GitHub Integration

### Automatic Builds

The BuildConfigs are configured with GitHub webhook triggers. To enable automatic builds on code changes:

1. **Get the webhook URL**:
   ```bash
   oc describe bc whatsapp-bridge | grep -A 5 "Webhook"
   oc describe bc whatsapp-mcp-server | grep -A 5 "Webhook"
   ```

2. **Add webhook to GitHub repository**:
   - Go to your GitHub repository settings
   - Navigate to "Webhooks" section
   - Add the webhook URLs from step 1
   - Set content type to `application/json`
   - Select "Just the push event"

### Custom Repository

To build from a different repository or branch:

```bash
# Build from a specific branch
GITHUB_REF=develop ./build-images.sh

# Build from a different repository
GITHUB_REPO=https://github.com/your-org/whatsapp-mcp.git ./build-images.sh
```

## Configuration

### Environment Variables

The deployment uses the following key environment variables:

- `BRIDGE_PORT`: Port for the WhatsApp Bridge service (default: 8080)
- `MCP_PORT`: Port for the MCP server (default: 3000)
- `BRIDGE_URL`: URL for the MCP server to connect to the bridge
- `STORE_PATH`: Path for persistent data storage

### Storage

The application uses persistent volumes for:
- WhatsApp session data and message history
- Application logs

### Security

- Both containers run as non-root users (UID 1001)
- Security contexts are configured to drop all capabilities
- TLS termination is handled at the route level

## Monitoring

### Health Checks

Both containers include:
- Liveness probes to detect unhealthy containers
- Readiness probes to ensure containers are ready to serve traffic

### Logs

View logs using:

```bash
# Bridge logs
oc logs -l app=whatsapp-mcp -c whatsapp-bridge -f

# MCP server logs
oc logs -l app=whatsapp-mcp -c whatsapp-mcp-server -f
```

### Status

Check deployment status:

```bash
oc get pods -l app=whatsapp-mcp
oc get services -l app=whatsapp-mcp
oc get routes -l app=whatsapp-mcp
```

## Scaling

To scale the application:

```bash
oc scale deployment whatsapp-mcp --replicas=2
```

**Note**: WhatsApp sessions are stateful, so scaling beyond 1 replica may cause issues unless session sharing is implemented.

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check if you're logged into OpenShift: `oc whoami`
   - Verify namespace exists: `oc get namespace whatsapp-mcp`

2. **Pod Startup Issues**
   - Check pod logs: `oc logs <pod-name> -c <container-name>`
   - Verify PVC is bound: `oc get pvc`

3. **Connectivity Issues**
   - Check service endpoints: `oc get endpoints`
   - Verify routes are accessible: `oc get routes`

### Debug Commands

```bash
# Describe pod for events
oc describe pod -l app=whatsapp-mcp

# Check resource usage
oc top pods -l app=whatsapp-mcp

# Access pod shell
oc exec -it <pod-name> -c <container-name> -- /bin/sh
```

## Cleanup

To remove the application:

```bash
./undeploy.sh
```

This will remove all resources except persistent volume claims (unless confirmed).

## Customization

### Modifying Configuration

Edit the `configmap.yaml` file to modify application configuration, then apply:

```bash
oc apply -f configmap.yaml
oc rollout restart deployment/whatsapp-mcp
```

### Updating Images

To update the application:

1. Build new images with updated tag
2. Update the deployment with new image references
3. Apply the updated deployment

```bash
# Build with new tag
TAG=v2.0.0 ./build-images.sh

# Deploy with new tag
TAG=v2.0.0 ./deploy.sh
```

## Security Considerations

- The application stores WhatsApp session data persistently
- Ensure proper network policies are in place
- Consider using OpenShift's built-in security features
- Regularly update base images for security patches

## Support

For issues and questions:
1. Check the application logs
2. Review OpenShift events
3. Consult the main project documentation
