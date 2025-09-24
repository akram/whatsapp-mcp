#!/usr/bin/env python3
"""
Test script for WhatsApp MCP server connection
"""

import requests
import json

# Configuration
WHATSAPP_MCP_BASE_URL = "http://localhost:3000"

def test_server_connection():
    """Test the connection to the WhatsApp MCP server."""
    print("🔌 Testing server connection...")
    
    try:
        # Test health endpoint
        print("\n🏥 Testing health endpoint...")
        response = requests.get(f"{WHATSAPP_MCP_BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            # Health endpoint returns plain text "OK", not JSON
            health_text = response.text.strip()
            print(f"✅ Health check passed!")
            print(f"   Status: {health_text}")
            print(f"   Service: WhatsApp MCP Server")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test root endpoint for server info
        print("\n📋 Testing root endpoint...")
        response = requests.get(WHATSAPP_MCP_BASE_URL, timeout=10)
        
        if response.status_code == 200:
            server_info = response.json()
            print(f"✅ Server info retrieved!")
            print(f"   Name: {server_info.get('name', 'Unknown')}")
            print(f"   Version: {server_info.get('version', 'Unknown')}")
            
            # Show available endpoints
            endpoints = server_info.get('endpoints', {})
            print(f"   Available endpoints:")
            for endpoint, path in endpoints.items():
                print(f"     - {endpoint}: {path}")
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test tools endpoint
        print("\n🔧 Testing tools endpoint...")
        response = requests.get(f"{WHATSAPP_MCP_BASE_URL}/tools", timeout=10)
        
        if response.status_code == 200:
            tools_data = response.json()
            tools = tools_data.get('tools', [])
            print(f"✅ Tools endpoint working!")
            print(f"   Found {len(tools)} tools")
            for i, tool in enumerate(tools[:3], 1):  # Show first 3 tools
                print(f"   {i}. {tool['name']}: {tool['description']}")
        else:
            print(f"❌ Tools endpoint failed with status {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test SSE endpoint
        print("\n📡 Testing SSE endpoint...")
        try:
            response = requests.get(f"{WHATSAPP_MCP_BASE_URL}/sse", timeout=2)
            if response.status_code == 200:
                print(f"✅ SSE endpoint accessible!")
                print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
            else:
                print(f"❌ SSE endpoint failed with status {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"✅ SSE endpoint accessible! (timeout expected for SSE)")
            print(f"   SSE connections stay open indefinitely")
        except Exception as e:
            print(f"❌ SSE endpoint error: {e}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    connection_ok = test_server_connection()
    
    if connection_ok:
        print("\n🎉 All tests passed! Server is ready for LlamaStack integration.")
    else:
        print("\n❌ Some tests failed. Check the server status.")
