# Fixed health endpoint test for WhatsApp MCP server
# Copy this code into your notebook cell

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
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# Test the connection
connection_ok = test_server_connection()
