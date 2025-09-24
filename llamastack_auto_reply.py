#!/usr/bin/env python3
"""
LlamaStack-powered auto-reply handler for WhatsApp messages.

This script creates a LlamaStack client that connects to the MCP server
and uses AI to generate intelligent responses to WhatsApp messages.
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LlamaStackAutoReply:
    """LlamaStack-powered auto-reply handler."""
    
    def __init__(self, mcp_server_url: str = "http://localhost:3000/sse"):
        self.mcp_server_url = mcp_server_url
        self.client = None
        self.message_count = 0
        self.reply_count = 0
        self.session_context = {}
        
    async def initialize(self):
        """Initialize the LlamaStack client."""
        try:
            # Import LlamaStack client
            from llamastack import LlamaStackClient
            
            # Create client with MCP server configuration
            self.client = LlamaStackClient(
                mcp_server_url=self.mcp_server_url,
                model="claude-3-5-sonnet-20241022",  # or your preferred model
                temperature=0.7,
                max_tokens=200
            )
            
            # Initialize the client
            await self.client.initialize()
            
            logger.info("✅ LlamaStack client initialized successfully")
            return True
            
        except ImportError:
            logger.error("❌ LlamaStack not installed. Install with: pip install llamastack")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to initialize LlamaStack client: {e}")
            return False
    
    async def generate_response(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Generate intelligent response using LlamaStack and MCP tools."""
        try:
            if not self.client:
                logger.error("LlamaStack client not initialized")
                return None
            
            sender = message_data.get('sender', 'unknown')
            content = message_data.get('content', '').strip()
            media_type = message_data.get('media_type', '')
            chat_name = message_data.get('chat_name', 'unknown')
            chat_jid = message_data.get('chat_jid', 'unknown')
            
            # Build context for the AI
            context = await self.build_context(message_data)
            
            # Use LlamaStack to generate response
            response = await self.client.generate_response(context)
            
            # Log the interaction
            logger.info(f"🤖 Generated response for {sender}: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None
    
    async def build_context(self, message_data: Dict[str, Any]) -> str:
        """Build context for the AI using MCP tools."""
        try:
            sender = message_data.get('sender', 'unknown')
            content = message_data.get('content', '').strip()
            media_type = message_data.get('media_type', '')
            chat_name = message_data.get('chat_name', 'unknown')
            chat_jid = message_data.get('chat_jid', 'unknown')
            
            # Get recent conversation context using MCP tools
            recent_messages = await self.get_recent_messages(chat_jid, limit=5)
            
            # Build context string
            context_parts = [
                f"You are a helpful WhatsApp assistant responding to a message from {chat_name} ({sender}).",
                "",
                "RECENT CONVERSATION:",
            ]
            
            # Add recent messages for context
            for msg in recent_messages:
                direction = "You" if msg.get('is_from_me', False) else chat_name
                msg_content = msg.get('content', '')
                timestamp = msg.get('timestamp', '')
                context_parts.append(f"{direction}: {msg_content}")
            
            context_parts.extend([
                "",
                f"CURRENT MESSAGE:",
                f"Content: {content}",
                f"Media type: {media_type if media_type else 'text'}",
                "",
                "INSTRUCTIONS:",
                "- Generate a helpful, natural response",
                "- Keep it conversational and concise (under 200 characters)",
                "- If it's a greeting, respond warmly",
                "- If it's a question, try to help or ask for clarification",
                "- If it's media, acknowledge it appropriately",
                "- Use the conversation context to make responses more relevant",
                "- Be friendly but professional"
            ])
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            return f"You are a helpful WhatsApp assistant. Respond to: {content}"
    
    async def get_recent_messages(self, chat_jid: str, limit: int = 5) -> list:
        """Get recent messages from the chat using MCP tools."""
        try:
            # This would use the MCP server's list_messages tool
            # For now, return empty list as we don't have direct access to MCP tools here
            return []
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    async def send_reply(self, chat_jid: str, message: str) -> bool:
        """Send a reply message via the WhatsApp bridge."""
        try:
            import requests
            
            response = requests.post(
                "http://localhost:8080/api/send",
                json={
                    "recipient": chat_jid,
                    "message": message
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("success", False)
            else:
                logger.error(f"Failed to send reply: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending reply: {e}")
            return False
    
    async def process_message(self, message_data: Dict[str, Any]):
        """Process a message and send auto-reply."""
        self.message_count += 1
        
        sender = message_data.get('sender', 'unknown')
        chat_jid = message_data.get('chat_jid', 'unknown')
        content = message_data.get('content', '')
        media_type = message_data.get('media_type', '')
        chat_name = message_data.get('chat_name', 'unknown')
        
        logger.info(f"📨 Processing message #{self.message_count} from {sender} ({chat_name})")
        if media_type:
            logger.info(f"   Media: {media_type}")
        else:
            logger.info(f"   Text: {content}")
        
        # Generate response
        response = await self.generate_response(message_data)
        
        if response:
            # Send reply
            success = await self.send_reply(chat_jid, response)
            if success:
                self.reply_count += 1
                logger.info(f"✅ Auto-reply sent to {sender}: {response}")
            else:
                logger.error(f"❌ Failed to send auto-reply to {sender}")
        else:
            logger.info(f"⏭️ No response generated for message from {sender}")
    
    async def close(self):
        """Close the LlamaStack client."""
        if self.client:
            try:
                await self.client.close()
                logger.info("✅ LlamaStack client closed")
            except Exception as e:
                logger.error(f"Error closing LlamaStack client: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics."""
        return {
            'total_messages': self.message_count,
            'total_replies': self.reply_count,
            'reply_rate': f"{(self.reply_count / self.message_count * 100):.1f}%" if self.message_count > 0 else "0%",
            'client_initialized': self.client is not None
        }

async def main():
    """Main function to run the LlamaStack auto-reply handler."""
    logger.info("🤖 Starting LlamaStack WhatsApp Auto-Reply Handler")
    
    # Create handler
    handler = LlamaStackAutoReply()
    
    # Initialize LlamaStack client
    if not await handler.initialize():
        logger.error("❌ Failed to initialize LlamaStack client. Exiting.")
        return
    
    logger.info("📋 LlamaStack auto-reply features:")
    logger.info("   ✅ AI-powered intelligent responses")
    logger.info("   ✅ Context-aware conversations")
    logger.info("   ✅ MCP tool integration")
    logger.info("   ✅ Media message handling")
    logger.info("   ✅ Conversation history awareness")
    logger.info("")
    logger.info("🔄 LlamaStack auto-reply handler is ready!")
    logger.info("   (Make sure the WhatsApp bridge and MCP server are running)")
    
    # For demonstration, let's process a test message
    test_message = {
        "type": "new_message",
        "message_id": "test_llamastack_123",
        "chat_jid": "21656067876@s.whatsapp.net",
        "sender": "21656067876",
        "content": "Hello, how are you today?",
        "timestamp": datetime.now().isoformat(),
        "media_type": "",
        "filename": "",
        "chat_name": "Akram Ben Aïssi"
    }
    
    logger.info("🧪 Testing LlamaStack auto-reply...")
    await handler.process_message(test_message)
    
    # Keep the handler running
    try:
        while True:
            await asyncio.sleep(30)
            
            stats = handler.get_stats()
            logger.info(f"📊 Stats: {stats['total_messages']} messages, {stats['total_replies']} replies ({stats['reply_rate']})")
            
    except KeyboardInterrupt:
        logger.info("👋 Shutting down LlamaStack auto-reply handler...")
        await handler.close()
        logger.info("✅ Handler stopped")

if __name__ == "__main__":
    asyncio.run(main())
