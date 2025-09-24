#!/usr/bin/env python3
"""
Setup script for LlamaStack auto-reply integration.

This script installs LlamaStack and tests the integration.
"""

import subprocess
import sys
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_llamastack():
    """Install LlamaStack package."""
    try:
        logger.info("📦 Installing LlamaStack...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "llamastack"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ LlamaStack installed successfully")
            return True
        else:
            logger.error(f"❌ Failed to install LlamaStack: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error installing LlamaStack: {e}")
        return False

def test_llamastack_import():
    """Test if LlamaStack can be imported."""
    try:
        import llamastack
        logger.info("✅ LlamaStack import successful")
        return True
    except ImportError as e:
        logger.error(f"❌ LlamaStack import failed: {e}")
        return False

async def test_llamastack_client():
    """Test creating a LlamaStack client."""
    try:
        from llamastack import LlamaStackClient
        
        # Create client
        client = LlamaStackClient(
            mcp_server_url="http://localhost:3000/sse",
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=200
        )
        
        # Initialize client
        await client.initialize()
        
        logger.info("✅ LlamaStack client created and initialized successfully")
        
        # Test a simple response
        test_response = await client.generate_response("Hello, how are you?")
        logger.info(f"✅ Test response generated: {test_response}")
        
        # Close client
        await client.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ LlamaStack client test failed: {e}")
        return False

def check_mcp_server():
    """Check if MCP server is running."""
    try:
        import requests
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ MCP server is running")
            return True
        else:
            logger.error(f"❌ MCP server returned status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ MCP server check failed: {e}")
        return False

def main():
    """Main setup function."""
    logger.info("🚀 Setting up LlamaStack auto-reply integration...")
    
    # Check if MCP server is running
    if not check_mcp_server():
        logger.error("❌ MCP server is not running. Please start it first.")
        return False
    
    # Install LlamaStack
    if not install_llamastack():
        logger.error("❌ Failed to install LlamaStack")
        return False
    
    # Test import
    if not test_llamastack_import():
        logger.error("❌ LlamaStack import failed")
        return False
    
    # Test client creation
    try:
        result = asyncio.run(test_llamastack_client())
        if not result:
            logger.error("❌ LlamaStack client test failed")
            return False
    except Exception as e:
        logger.error(f"❌ LlamaStack client test error: {e}")
        return False
    
    logger.info("🎉 LlamaStack auto-reply integration setup complete!")
    logger.info("")
    logger.info("📋 Next steps:")
    logger.info("   1. Restart the MCP server to load the new auto-reply functionality")
    logger.info("   2. Send a WhatsApp message to test the AI-powered responses")
    logger.info("   3. The system will now use LlamaStack to generate intelligent replies")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
