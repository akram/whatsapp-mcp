#!/usr/bin/env python3
"""
Run the WhatsApp MCP notebook programmatically to send a lovely message to Teti Kusmiati.
"""

import sys
import os
import time

def run_notebook_cells():
    """Run the notebook cells programmatically."""
    print("🚀 Running WhatsApp MCP Notebook...")
    
    # Add the current directory to Python path
    sys.path.insert(0, os.getcwd())
    
    try:
        # Import required libraries
        print("📦 Importing libraries...")
        from llama_stack_client import Agent, LlamaStackClient, AgentEventLogger, RAGDocument
        from httpx import URL
        import requests
        print("✅ All imports successful!")
        
        # Initialize the LlamaStack client
        print("🔧 Initializing LlamaStack client...")
        client = LlamaStackClient(base_url="http://ragathon-team-3-ragathon-team-3.apps.llama-rag-pool-b84hp.aws.rh-ods.com/")
        print("✅ Client initialized!")
        
        # Register the WhatsApp MCP toolgroup
        print("📡 Registering WhatsApp MCP toolgroup...")
        client.toolgroups.register(
            toolgroup_id="mcp::whatsapp-mcp",
            provider_id="model-context-protocol",
            mcp_endpoint={"uri": "https://whatsapp-http-route-whatsapp-mcp.apps.rosa.akram.a1ey.p3.openshiftapps.com/sse"},
        )
        print("✅ Toolgroup registered!")
        
        # Create the agent
        print("🤖 Creating agent...")
        agent = Agent(
            client,
            model="vllm-inference/llama-3-2-3b-instruct",
            instructions="You are a helpful assistant. You can use the tools provided to you to help the user.",
            tools=[
                "mcp::whatsapp-mcp",
            ],
        )
        print("✅ Agent created!")
        
        # Test basic functionality first
        print("\n🧪 Testing basic functionality...")
        test_prompt = "Hi, what was my latest message in whatsapp?"
        print(f"prompt> {test_prompt}")
        
        test_response = agent.create_turn(
            messages=[{"role": "user", "content": test_prompt}],
            session_id=agent.create_session("test_session"),
            stream=True,
        )
        
        print("Response:")
        for log in AgentEventLogger().log(test_response):
            log.print()
        
        # Now search for Teti Kusmiati
        print("\n🔍 Searching for Teti Kusmiati...")
        search_prompt = "Search for my wife Teti Kusmiati in my WhatsApp contacts"
        print(f"prompt> {search_prompt}")
        
        search_response = agent.create_turn(
            messages=[{"role": "user", "content": search_prompt}],
            session_id=agent.create_session("search_session"),
            stream=True,
        )
        
        print("Search results:")
        for log in AgentEventLogger().log(search_response):
            log.print()
        
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
        
        return True
        
    except Exception as e:
        print(f"❌ Error running notebook: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_notebook_cells()
    sys.exit(0 if success else 1)
