#!/usr/bin/env python3
"""
Test MCP server by sending a message using proper MCP protocol via HTTP.
"""

import requests
import json
import time

def test_mcp_send_message():
    """Test sending a message via MCP server using proper HTTP requests."""
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
    
    # Test direct HTTP endpoint for sending messages
    print("\n💬 Testing direct HTTP send_message endpoint...")
    
    try:
        # Try the direct HTTP endpoint
        response = requests.post(
            f"{base_url}/api/messages/send",
            params={
                "recipient": "216",
                "message": "Hello Akram! This is a direct test message from the WhatsApp MCP server. The system is working perfectly! 🚀"
            },
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Message sent successfully!")
            print(f"   Success: {result.get('success', 'unknown')}")
            print(f"   Message: {result.get('message', 'no message')}")
        else:
            print(f"❌ Message send failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this might indicate the WhatsApp bridge is not responding")
    except Exception as e:
        print(f"❌ Message send error: {e}")
    
    # Test MCP protocol via tools endpoint
    print("\n🔧 Testing MCP protocol via tools endpoint...")
    
    try:
        # Try using the tools endpoint with MCP protocol
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "send_message",
                "arguments": {
                    "recipient": "216",
                    "message": "Hello Akram! This is an MCP protocol test message. 🚀"
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/tools/send_message/execute",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 MCP Response status: {response.status_code}")
        print(f"📥 MCP Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCP message sent successfully!")
            print(f"   Result: {result}")
        else:
            print(f"❌ MCP message send failed: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⏰ MCP request timed out")
    except Exception as e:
        print(f"❌ MCP request error: {e}")
    
    print("\n🎯 Summary:")
    print("✅ MCP server is running and healthy")
    print("✅ Tools endpoint is working")
    print("✅ send_message tool is available")
    print("📤 Message requests sent to +216")
    print("📱 Check your WhatsApp for the test messages!")
    
    return True

if __name__ == "__main__":
    test_mcp_send_message()