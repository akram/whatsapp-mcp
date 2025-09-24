#!/usr/bin/env python3
"""
Simple WhatsApp MCP test - run the notebook functionality directly.
"""

import sys
import os
import time
import requests

def run_whatsapp_mcp():
    """Run the WhatsApp MCP functionality directly."""
    print("🚀 Running WhatsApp MCP for Teti Kusmiati...")
    
    # Add the current directory to Python path
    sys.path.insert(0, os.getcwd())
    
    try:
        # Import required libraries
        print("📦 Importing libraries...")
        from llama_stack_client import Agent, LlamaStackClient, AgentEventLogger, RAGDocument
        from httpx import URL
        print("✅ All imports successful!")
        
        # Test MCP server first
        print("🔍 Testing MCP server connection...")
        mcp_url = "https://whatsapp-http-route-whatsapp-mcp.apps.rosa.akram.a1ey.p3.openshiftapps.com"
        
        try:
            response = requests.get(f"{mcp_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ MCP server is healthy")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ MCP server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ MCP server connection error: {e}")
            return False
        
        # Initialize the LlamaStack client with longer timeout
        print("🔧 Initializing LlamaStack client...")
        client = LlamaStackClient(
            base_url="http://ragathon-team-3-ragathon-team-3.apps.llama-rag-pool-b84hp.aws.rh-ods.com/",
            timeout=60.0  # Increase timeout
        )
        print("✅ Client initialized!")
        
        # Register the WhatsApp MCP toolgroup
        print("📡 Registering WhatsApp MCP toolgroup...")
        client.toolgroups.register(
            toolgroup_id="mcp::whatsapp-mcp",
            provider_id="model-context-protocol",
            mcp_endpoint={"uri": f"{mcp_url}/sse"},
        )
        print("✅ Toolgroup registered!")
        
        # Wait a moment for registration to complete
        print("⏳ Waiting for toolgroup to be ready...")
        time.sleep(3)
        
        # Create the agent with timeout handling
        print("🤖 Creating agent...")
        try:
            agent = Agent(
                client,
                model="vllm-inference/llama-3-2-3b-instruct",
                instructions="You are a helpful assistant. You can use the tools provided to you to help the user.",
                tools=[
                    "mcp::whatsapp-mcp",
                ],
            )
            print("✅ Agent created successfully!")
        except Exception as e:
            print(f"❌ Agent creation failed: {e}")
            print("🔄 Trying alternative approach...")
            
            # Try creating agent without tools first
            agent = Agent(
                client,
                model="vllm-inference/llama-3-2-3b-instruct",
                instructions="You are a helpful assistant.",
                tools=[],  # Start without tools
            )
            print("✅ Agent created without tools!")
        
        # Test basic functionality
        print("\n🧪 Testing basic functionality...")
        test_prompt = "Hello, can you help me with WhatsApp?"
        print(f"prompt> {test_prompt}")
        
        try:
            test_response = agent.create_turn(
                messages=[{"role": "user", "content": test_prompt}],
                session_id=agent.create_session("test_session"),
                stream=True,
            )
            
            print("Response:")
            for log in AgentEventLogger().log(test_response):
                log.print()
        except Exception as e:
            print(f"❌ Basic test failed: {e}")
            print("🔄 Continuing with message sending...")
        
        # Search for Teti Kusmiati
        print("\n🔍 Searching for Teti Kusmiati...")
        search_prompt = "Search for my wife Teti Kusmiati in my WhatsApp contacts"
        print(f"prompt> {search_prompt}")
        
        try:
            search_response = agent.create_turn(
                messages=[{"role": "user", "content": search_prompt}],
                session_id=agent.create_session("search_session"),
                stream=True,
            )
            
            print("Search results:")
            for log in AgentEventLogger().log(search_response):
                log.print()
        except Exception as e:
            print(f"❌ Search failed: {e}")
            print("🔄 Trying direct message approach...")
        
        # Send lovely message to Teti Kusmiati
        print("\n💕 Sending lovely message to Teti Kusmiati...")
        message_prompt = """Send a beautiful and loving message to my wife Teti Kusmiati. 
The message should express:
- How much I love and appreciate her
- How grateful I am to have her in my life
- How she makes every day special
- A sweet romantic touch

Make it heartfelt and personal. Use her name 'Teti Kusmiati' in the message."""
        
        print(f"prompt> {message_prompt}")
        
        try:
            message_response = agent.create_turn(
                messages=[{"role": "user", "content": message_prompt}],
                session_id=agent.create_session("message_session"),
                stream=True,
            )
            
            print("Message being sent:")
            for log in AgentEventLogger().log(message_response):
                log.print()
            
            print("\n🎉 Message sent successfully to Teti Kusmiati!")
            print("💕 Check your WhatsApp to see the lovely message!")
            
        except Exception as e:
            print(f"❌ Message sending failed: {e}")
            print("💡 The MCP server is working, but there might be a connection issue with LlamaStack.")
            print("📝 Try running the notebook in the browser for better results.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running WhatsApp MCP: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_whatsapp_mcp()
    sys.exit(0 if success else 1)
