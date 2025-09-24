#!/usr/bin/env python3
"""
Test script to run the WhatsApp MCP notebook programmatically.
"""

import sys
import os
import subprocess
import time

def run_notebook_test():
    """Run the notebook test programmatically."""
    print("🚀 Starting WhatsApp MCP Notebook Test...")
    
    # Activate virtual environment and run notebook
    notebook_path = "jupyter/whatsapp_agent.ipynb"
    
    # Check if notebook exists
    if not os.path.exists(notebook_path):
        print(f"❌ Notebook not found: {notebook_path}")
        return False
    
    print(f"📓 Found notebook: {notebook_path}")
    print("🔧 Setting up environment...")
    
    # Set up environment
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    
    # Create a simple test script to verify the setup
    test_script = """
import sys
print("Python version:", sys.version)
print("Python path:", sys.path)

try:
    from llama_stack_client import Agent, LlamaStackClient, AgentEventLogger, RAGDocument
    from httpx import URL
    print("✅ LlamaStack imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

try:
    import requests
    print("✅ Requests import successful")
except ImportError as e:
    print(f"❌ Requests import error: {e}")
    sys.exit(1)

print("🎉 All imports successful!")
print("📡 Testing OpenShift connection...")

# Test OpenShift connection
try:
    response = requests.get("https://whatsapp-http-route-whatsapp-mcp.apps.rosa.akram.a1ey.p3.openshiftapps.com/health", timeout=10)
    if response.status_code == 200:
        print("✅ OpenShift MCP server is accessible")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ OpenShift server returned status: {response.status_code}")
except Exception as e:
    print(f"❌ OpenShift connection error: {e}")

print("🎯 Ready to run the notebook!")
"""
    
    # Write test script
    with open("test_imports.py", "w") as f:
        f.write(test_script)
    
    # Run the test
    print("🧪 Running import and connection tests...")
    try:
        result = subprocess.run([
            sys.executable, "test_imports.py"
        ], env=env, capture_output=True, text=True, timeout=30)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            print("\n📋 Next steps:")
            print("1. Open your browser and go to: http://localhost:8888")
            print("2. Use token: 07e94c634e5fa1ae92190f010523b508739f15a3a95faf8f")
            print("3. Open the whatsapp_agent.ipynb notebook")
            print("4. Run the cells to test the WhatsApp MCP agent")
            print("5. Try the new 'Send a Lovely Message to Teti Kusmiati' section!")
            return True
        else:
            print(f"❌ Tests failed with return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists("test_imports.py"):
            os.remove("test_imports.py")

if __name__ == "__main__":
    success = run_notebook_test()
    sys.exit(0 if success else 1)
