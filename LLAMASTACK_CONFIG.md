# LlamaStack Auto-Reply Configuration

## Environment Variables

Configure the LlamaStack auto-reply system using these environment variables:

### Required Configuration

```bash
# LlamaStack service URL (external LlamaStack deployment)
export LLAMASTACK_BASE_URL="http://ragathon-team-3-ragathon-team-3.apps.llama-rag-pool-b84hp.aws.rh-ods.com/"

# WhatsApp MCP server endpoint (where MCP server is running)
export WHATSAPP_MCP_SSE_URL="https://whatsapp-mcp-route-whatsapp-mcp.apps.rosa.akram.a1ey.p3.openshiftapps.com/sse"

# AI model to use for responses
export LLAMASTACK_MODEL="claude-3-5-sonnet-20241022"

# Response creativity (0.0 = deterministic, 1.0 = creative)
export LLAMASTACK_TEMPERATURE="0.7"

# Maximum response length
export LLAMASTACK_MAX_TOKENS="200"
```

### Optional Configuration

```bash
# MCP server configuration
export MCP_HOST="0.0.0.0"
export MCP_PORT="3000"
export MCP_TRANSPORT="sse"

# WhatsApp bridge configuration
export MCP_SERVER_URL="http://localhost:3000"
export MESSAGES_DB_PATH="/path/to/messages.db"
```

## Usage Examples

### Basic Setup (Using Default Configuration)
```bash
# Default configuration:
# - LLAMASTACK_BASE_URL: ragathon-team-3 deployment
# - WHATSAPP_MCP_SSE_URL: OpenShift route
# No environment variables needed - uses defaults

# Start MCP server
cd whatsapp-mcp-server
python main.py
```

### Custom LlamaStack Service
```bash
# If LlamaStack is running on a different host/port
export LLAMASTACK_BASE_URL="http://llamastack.example.com:8080/"
export WHATSAPP_MCP_SSE_URL="https://whatsapp-mcp-route-whatsapp-mcp.apps.rosa.akram.a1ey.p3.openshiftapps.com/sse"
export LLAMASTACK_MODEL="gpt-4"
export LLAMASTACK_TEMPERATURE="0.5"

# Start MCP server
python main.py
```

### Docker Environment
```bash
# In docker-compose.yml or Dockerfile
environment:
  - LLAMASTACK_BASE_URL=http://llamastack-service:3000/
  - WHATSAPP_MCP_SSE_URL=https://whatsapp-mcp-route-whatsapp-mcp.apps.rosa.akram.a1ey.p3.openshiftapps.com/sse
  - LLAMASTACK_MODEL=claude-3-5-sonnet-20241022
  - LLAMASTACK_TEMPERATURE=0.7
  - LLAMASTACK_MAX_TOKENS=200
```

## Configuration Notes

1. **LLAMASTACK_BASE_URL**: This should point to where LlamaStack is running
2. **WHATSAPP_MCP_SSE_URL**: This should point to your MCP server's SSE endpoint
3. **LLAMASTACK_MODEL**: Choose the AI model based on your needs and API access
4. **LLAMASTACK_TEMPERATURE**: Lower values (0.1-0.3) for consistent responses, higher values (0.7-1.0) for creative responses
5. **LLAMASTACK_MAX_TOKENS**: Adjust based on desired response length

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check if LlamaStack service is running at the specified URL
2. **Model Not Found**: Verify the model name is correct for your API provider
3. **Authentication Error**: Ensure proper API keys are configured in LlamaStack
4. **Timeout**: Increase timeout values if responses are taking too long

### Debug Mode

Enable debug logging to see configuration values:

```bash
export PYTHONPATH=/path/to/whatsapp-mcp-server
python -c "
import os
print('LLAMASTACK_BASE_URL:', os.getenv('LLAMASTACK_BASE_URL', 'http://ragathon-team-3-ragathon-team-3.apps.llama-rag-pool-b84hp.aws.rh-ods.com/'))
print('WHATSAPP_MCP_SSE_URL:', os.getenv('WHATSAPP_MCP_SSE_URL', 'https://whatsapp-mcp-route-whatsapp-mcp.apps.rosa.akram.a1ey.p3.openshiftapps.com/sse'))
print('LLAMASTACK_MODEL:', os.getenv('LLAMASTACK_MODEL', 'claude-3-5-sonnet-20241022'))
print('LLAMASTACK_TEMPERATURE:', os.getenv('LLAMASTACK_TEMPERATURE', '0.7'))
print('LLAMASTACK_MAX_TOKENS:', os.getenv('LLAMASTACK_MAX_TOKENS', '200'))
"
```
