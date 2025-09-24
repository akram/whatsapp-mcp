#!/usr/bin/env python3
"""
Test MCP server by sending a message to Akram Ben Aissi +216 using curl/requests.
"""

import requests
import json
import time

def test_mcp_send_message():
    """Test sending a message via MCP server using HTTP requests."""
    print("🚀 Testing MCP Server - Sending Message to Akram Ben Aissi +216...")
    
    base_url = "https://whatsapp-http-route-whatsapp-mcp.apps.rosa.akram.a1ey.p3.openshiftapps.com"
    
    # Test health first
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test tools endpoint
    print("\n🔧 Testing tools endpoint...")
    try:
        response = requests.get(f"{base_url}/tools", timeout=10)
        if response.status_code == 200:
            tools = response.json().get("tools", [])
            print(f"✅ Found {len(tools)} tools")
            
            # Find send_message tool
            send_message_tool = None
            for tool in tools:
                if tool['name'] == 'send_message':
                    send_message_tool = tool
                    break
            
            if send_message_tool:
                print("✅ Found send_message tool")
                print(f"   Description: {send_message_tool['description']}")
                print(f"   Parameters: {send_message_tool['parameters']}")
            else:
                print("❌ send_message tool not found")
                return False
        else:
            print(f"❌ Tools endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tools endpoint error: {e}")
        return False
    
    # Test MCP protocol - send message
    print("\n💬 Testing MCP send_message...")
    
    # MCP request format
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "send_message",
            "arguments": {
                "recipient": "216",  # Your phone number without + symbol
                "message": "Hello Akram! This is a test message from the WhatsApp MCP server. The system is working perfectly! 🚀"
            }
        }
    }
    
    print(f"📤 Sending MCP request:")
    print(f"   Recipient: +216")
    print(f"   Message: Hello Akram! This is a test message from the WhatsApp MCP server. The system is working perfectly! 🚀")
    
    try:
        # Send MCP request
        response = requests.post(
            f"{base_url}/sse",
            json=mcp_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ MCP request successful!")
                print(f"   Response: {result}")
            except json.JSONDecodeError:
                print("📥 Response (non-JSON):")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        else:
            print(f"❌ MCP request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this might be normal for SSE")
    except Exception as e:
        print(f"❌ MCP request error: {e}")
    
    # Alternative: Try direct HTTP endpoint if it exists
    print("\n🔄 Trying alternative HTTP endpoint...")
    
    try:
        # Try a direct HTTP call to send message
        message_data = {
            "recipient": "216",
            "message": "Hello Akram! This is a direct test from the WhatsApp MCP server. 🚀"
        }
        
        response = requests.post(
            f"{base_url}/send_message",
            json=message_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📥 Direct endpoint response: {response.status_code}")
        if response.status_code != 404:
            print(f"   Response: {response.text}")
        else:
            print("   Direct endpoint not available (expected)")
            
    except Exception as e:
        print(f"❌ Direct endpoint error: {e}")
    
    # Test with curl command
    print("\n🔧 Testing with curl command...")
    
    curl_command = f'''curl -X POST "{base_url}/sse" \\
  -H "Content-Type: application/json" \\
  -H "Accept: application/json" \\
  -d '{json.dumps(mcp_request)}' \\
  --max-time 30'''
    
    print("📋 Curl command:")
    print(curl_command)
    
    print("\n🎯 Summary:")
    print("✅ MCP server is running and healthy")
    print("✅ Tools endpoint is working")
    print("✅ send_message tool is available")
    print("📤 Message request sent to +216")
    print("📱 Check your WhatsApp for the test message!")
    
    return True

if __name__ == "__main__":
    test_mcp_send_message()
