#!/usr/bin/env python3
"""
LlamaStack URL Configuration Helper

This script helps you configure the correct LlamaStack URL for the auto-reply system.
"""

import os
import sys
import requests
import json

def check_llamastack_url(url):
    """Check if a LlamaStack URL is accessible."""
    try:
        # Try to connect to the URL
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, "✅ LlamaStack service is accessible"
        else:
            return False, f"❌ LlamaStack returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "❌ Cannot connect to LlamaStack service"
    except requests.exceptions.Timeout:
        return False, "❌ LlamaStack service timeout"
    except Exception as e:
        return False, f"❌ Error checking LlamaStack: {e}"

def test_mcp_server():
    """Test if MCP server is running."""
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            return True, "✅ MCP server is running"
        else:
            return False, f"❌ MCP server returned status {response.status_code}"
    except Exception as e:
        return False, f"❌ MCP server not accessible: {e}"

def main():
    """Main configuration helper."""
    print("🔧 LlamaStack URL Configuration Helper")
    print("=" * 50)
    
    # Check current configuration
    current_url = os.getenv("LLAMASTACK_URL", "http://localhost:3000/sse")
    print(f"Current LLAMASTACK_URL: {current_url}")
    
    # Test MCP server
    print("\n📡 Testing MCP server...")
    mcp_ok, mcp_msg = test_mcp_server()
    print(mcp_msg)
    
    # Test LlamaStack URL
    print(f"\n🔗 Testing LlamaStack URL: {current_url}")
    llamastack_ok, llamastack_msg = check_llamastack_url(current_url)
    print(llamastack_msg)
    
    # Provide configuration options
    print("\n📋 Configuration Options:")
    print("")
    print("1. **Default Configuration (Self-referencing - NOT RECOMMENDED)**")
    print("   export LLAMASTACK_URL='http://localhost:3000/sse'")
    print("   # This points to the MCP server itself - may cause issues")
    print("")
    print("2. **External LlamaStack Service**")
    print("   export LLAMASTACK_URL='http://llamastack.example.com:8080/sse'")
    print("   # Point to a separate LlamaStack service")
    print("")
    print("3. **Local LlamaStack Service**")
    print("   export LLAMASTACK_URL='http://localhost:8080/sse'")
    print("   # If LlamaStack is running on a different port")
    print("")
    print("4. **Disable Auto-Reply**")
    print("   export LLAMASTACK_URL=''")
    print("   # Empty URL disables auto-reply functionality")
    print("")
    
    # Recommendations
    print("💡 Recommendations:")
    if not llamastack_ok:
        print("   ❌ Current LlamaStack URL is not accessible")
        print("   🔧 Consider using an external LlamaStack service")
        print("   🔧 Or disable auto-reply if not needed")
    else:
        print("   ✅ Current configuration appears to be working")
    
    print("")
    print("🚀 To apply new configuration:")
    print("   1. Set environment variables")
    print("   2. Restart the MCP server")
    print("   3. Test with a WhatsApp message")
    
    # Interactive configuration
    print("\n" + "=" * 50)
    new_url = input("Enter new LLAMASTACK_URL (or press Enter to keep current): ").strip()
    
    if new_url:
        print(f"\n🔗 Testing new URL: {new_url}")
        new_ok, new_msg = check_llamastack_url(new_url)
        print(new_msg)
        
        if new_ok:
            print(f"\n✅ New URL is accessible!")
            print(f"🔧 Set this environment variable:")
            print(f"   export LLAMASTACK_URL='{new_url}'")
        else:
            print(f"\n❌ New URL is not accessible")
            print("🔧 Please check the URL and try again")
    
    return llamastack_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
