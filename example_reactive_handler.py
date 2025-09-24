#!/usr/bin/env python3
"""
Example script demonstrating reactive message handling with the WhatsApp MCP server.

This script shows how to:
1. Register a message handler with the MCP server
2. React to incoming WhatsApp messages in real-time
3. Process different types of messages (text, media, etc.)
"""

import asyncio
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReactiveMessageHandler:
    """Example reactive message handler for WhatsApp messages."""
    
    def __init__(self, mcp_server_url: str = "http://localhost:3000"):
        self.mcp_server_url = mcp_server_url
        self.message_count = 0
        
    async def handle_new_message(self, message_data: Dict[str, Any]):
        """Handle incoming WhatsApp messages."""
        self.message_count += 1
        
        # Extract message information
        message_id = message_data.get('message_id', 'unknown')
        chat_jid = message_data.get('chat_jid', 'unknown')
        sender = message_data.get('sender', 'unknown')
        content = message_data.get('content', '')
        timestamp = message_data.get('timestamp', '')
        media_type = message_data.get('media_type', '')
        filename = message_data.get('filename', '')
        chat_name = message_data.get('chat_name', 'unknown')
        
        # Log the message
        logger.info(f"📨 Message #{self.message_count} received!")
        logger.info(f"   From: {sender} ({chat_name})")
        logger.info(f"   Chat JID: {chat_jid}")
        logger.info(f"   Time: {timestamp}")
        
        if media_type:
            logger.info(f"   Media: {media_type} - {filename}")
            if content:
                logger.info(f"   Caption: {content}")
        else:
            logger.info(f"   Text: {content}")
        
        # Example: Auto-reply to specific messages
        await self.process_auto_reply(message_data)
        
        # Example: Log important messages
        await self.log_important_messages(message_data)
        
        # Example: Forward messages from specific contacts
        await self.forward_from_important_contacts(message_data)
    
    async def process_auto_reply(self, message_data: Dict[str, Any]):
        """Example: Auto-reply to messages containing specific keywords."""
        content = message_data.get('content', '').lower()
        sender = message_data.get('sender', '')
        chat_jid = message_data.get('chat_jid', '')
        
        # Auto-reply to "hello" messages
        if 'hello' in content or 'hi' in content:
            reply_message = f"Hello! I received your message: '{message_data.get('content', '')}'"
            await self.send_reply(chat_jid, reply_message)
            logger.info(f"🤖 Auto-replied to {sender}")
    
    async def log_important_messages(self, message_data: Dict[str, Any]):
        """Example: Log messages from important contacts."""
        sender = message_data.get('sender', '')
        important_contacts = ['1234567890', '0987654321']  # Add important phone numbers
        
        if sender in important_contacts:
            logger.info(f"⭐ IMPORTANT MESSAGE from {sender}")
            # Here you could save to a special log file, database, etc.
    
    async def forward_from_important_contacts(self, message_data: Dict[str, Any]):
        """Example: Forward messages from important contacts to another chat."""
        sender = message_data.get('sender', '')
        content = message_data.get('content', '')
        chat_name = message_data.get('chat_name', '')
        
        # Forward messages from specific contacts
        if sender in ['1234567890']:  # Add phone numbers to forward from
            forward_message = f"Forwarded from {chat_name} ({sender}): {content}"
            # You would specify the destination chat JID here
            # await self.send_reply("destination_chat_jid@g.us", forward_message)
            logger.info(f"📤 Would forward message from {sender}")
    
    async def send_reply(self, chat_jid: str, message: str):
        """Send a reply message using the MCP server."""
        try:
            # Use the MCP server's send_message tool
            response = requests.post(
                f"{self.mcp_server_url}/api/send",
                json={
                    "recipient": chat_jid,
                    "message": message
                }
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Reply sent successfully")
            else:
                logger.error(f"❌ Failed to send reply: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Error sending reply: {e}")
    
    def register_with_mcp_server(self):
        """Register this handler with the MCP server."""
        try:
            # This would be done by importing the MCP server and calling add_message_handler
            # For this example, we'll simulate it
            logger.info("🔗 Handler registered with MCP server")
            logger.info("📡 Waiting for incoming messages...")
            logger.info("   (Make sure the WhatsApp bridge and MCP server are running)")
            
        except Exception as e:
            logger.error(f"❌ Failed to register handler: {e}")

def create_simple_handler():
    """Create a simple message handler function."""
    def simple_handler(message_data: Dict[str, Any]):
        """Simple synchronous handler."""
        print(f"🔔 New message from {message_data.get('sender', 'unknown')}: {message_data.get('content', '')}")
    
    return simple_handler

async def main():
    """Main function demonstrating reactive message handling."""
    logger.info("🚀 Starting WhatsApp Reactive Message Handler Example")
    
    # Create handler instance
    handler = ReactiveMessageHandler()
    
    # Register the handler
    handler.register_with_mcp_server()
    
    # Example: Create a simple handler
    simple_handler = create_simple_handler()
    
    logger.info("📋 Available handler functions:")
    logger.info("   1. handle_new_message - Full async handler with auto-reply")
    logger.info("   2. simple_handler - Basic synchronous handler")
    logger.info("")
    logger.info("💡 To use these handlers in your MCP server:")
    logger.info("   from main import add_message_handler")
    logger.info("   add_message_handler(handler.handle_new_message)")
    logger.info("")
    logger.info("🔄 Keep this script running to see message notifications...")
    
    # Keep the script running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("👋 Shutting down handler...")

if __name__ == "__main__":
    asyncio.run(main())
