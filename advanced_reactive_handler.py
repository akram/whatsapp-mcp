#!/usr/bin/env python3
"""
Advanced reactive message handler that integrates directly with the MCP server.

This script demonstrates:
1. Direct integration with the MCP server's message handling system
2. Real-time message processing and auto-responses
3. Message filtering and routing
4. Integration with external services
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Callable

# Add the MCP server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'whatsapp-mcp-server'))

from main import add_message_handler, remove_message_handler
from whatsapp import send_message, get_chat

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedMessageHandler:
    """Advanced reactive message handler with multiple processing capabilities."""
    
    def __init__(self):
        self.message_count = 0
        self.processed_messages = []
        self.blocked_senders = set()
        self.auto_reply_enabled = True
        self.keyword_responses = {
            'help': 'I can help you with various tasks. Try asking me about the weather, time, or just say hello!',
            'time': f'The current time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'status': 'I am online and ready to help!',
            'ping': 'Pong! 🏓',
        }
        self.important_contacts = set()
        self.forward_rules = {}
        
    async def handle_message(self, message_data: Dict[str, Any]):
        """Main message handler that processes incoming messages."""
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
        logger.info(f"📨 Processing message #{self.message_count}")
        logger.info(f"   From: {sender} ({chat_name})")
        logger.info(f"   Content: {content[:50]}{'...' if len(content) > 50 else ''}")
        
        # Store message for analysis
        self.processed_messages.append({
            'timestamp': datetime.now(),
            'sender': sender,
            'content': content,
            'chat_jid': chat_jid,
            'media_type': media_type
        })
        
        # Check if sender is blocked
        if sender in self.blocked_senders:
            logger.info(f"🚫 Message from blocked sender {sender} ignored")
            return
        
        # Process different types of messages
        if media_type:
            await self.handle_media_message(message_data)
        else:
            await self.handle_text_message(message_data)
        
        # Check for important contacts
        if sender in self.important_contacts:
            await self.handle_important_contact_message(message_data)
        
        # Apply forwarding rules
        await self.apply_forwarding_rules(message_data)
    
    async def handle_text_message(self, message_data: Dict[str, Any]):
        """Handle text messages with various processing options."""
        content = message_data.get('content', '').lower().strip()
        sender = message_data.get('sender', '')
        chat_jid = message_data.get('chat_jid', '')
        
        # Check for keyword responses
        for keyword, response in self.keyword_responses.items():
            if keyword in content:
                await self.send_reply(chat_jid, response)
                logger.info(f"🤖 Sent keyword response for '{keyword}'")
                return
        
        # Auto-reply for greetings
        if any(greeting in content for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            greeting_response = f"Hello! Thanks for your message. I received: '{message_data.get('content', '')}'"
            await self.send_reply(chat_jid, greeting_response)
            logger.info(f"🤖 Sent greeting response")
        
        # Handle commands
        if content.startswith('/'):
            await self.handle_command(message_data)
    
    async def handle_media_message(self, message_data: Dict[str, Any]):
        """Handle media messages (images, videos, audio, documents)."""
        media_type = message_data.get('media_type', '')
        filename = message_data.get('filename', '')
        sender = message_data.get('sender', '')
        chat_jid = message_data.get('chat_jid', '')
        
        logger.info(f"📎 Processing {media_type} message: {filename}")
        
        # Auto-acknowledge media messages
        if self.auto_reply_enabled:
            media_response = f"Thanks for the {media_type}! I received your file: {filename}"
            await self.send_reply(chat_jid, media_response)
            logger.info(f"🤖 Sent media acknowledgment")
    
    async def handle_command(self, message_data: Dict[str, Any]):
        """Handle command messages starting with '/'."""
        content = message_data.get('content', '').lower().strip()
        sender = message_data.get('sender', '')
        chat_jid = message_data.get('chat_jid', '')
        
        if content == '/help':
            help_text = """
Available commands:
/help - Show this help message
/status - Check bot status
/time - Get current time
/block - Block this sender
/unblock - Unblock this sender
/stats - Show message statistics
"""
            await self.send_reply(chat_jid, help_text)
            logger.info(f"🤖 Sent help message")
        
        elif content == '/status':
            status_response = f"Bot Status: Online\nMessages processed: {self.message_count}\nAuto-reply: {'Enabled' if self.auto_reply_enabled else 'Disabled'}"
            await self.send_reply(chat_jid, status_response)
            logger.info(f"🤖 Sent status response")
        
        elif content == '/stats':
            stats_response = f"Message Statistics:\nTotal processed: {self.message_count}\nBlocked senders: {len(self.blocked_senders)}\nImportant contacts: {len(self.important_contacts)}"
            await self.send_reply(chat_jid, stats_response)
            logger.info(f"🤖 Sent stats response")
        
        elif content == '/block':
            self.blocked_senders.add(sender)
            await self.send_reply(chat_jid, f"Sender {sender} has been blocked.")
            logger.info(f"🚫 Blocked sender: {sender}")
        
        elif content == '/unblock':
            self.blocked_senders.discard(sender)
            await self.send_reply(chat_jid, f"Sender {sender} has been unblocked.")
            logger.info(f"✅ Unblocked sender: {sender}")
    
    async def handle_important_contact_message(self, message_data: Dict[str, Any]):
        """Handle messages from important contacts with special processing."""
        sender = message_data.get('sender', '')
        content = message_data.get('content', '')
        
        logger.info(f"⭐ IMPORTANT MESSAGE from {sender}")
        
        # You could implement special handling here:
        # - Save to special log
        # - Send notifications
        # - Forward to other systems
        # - etc.
    
    async def apply_forwarding_rules(self, message_data: Dict[str, Any]):
        """Apply forwarding rules based on sender or content."""
        sender = message_data.get('sender', '')
        content = message_data.get('content', '')
        
        # Example: Forward messages containing "urgent" to a specific chat
        if 'urgent' in content.lower():
            # You would specify the destination chat JID here
            # forward_message = f"URGENT from {sender}: {content}"
            # await self.send_reply("destination_chat_jid@g.us", forward_message)
            logger.info(f"📤 Would forward urgent message from {sender}")
    
    async def send_reply(self, chat_jid: str, message: str):
        """Send a reply message."""
        try:
            success, status_message = send_message(chat_jid, message)
            if success:
                logger.info(f"✅ Reply sent: {message[:50]}...")
            else:
                logger.error(f"❌ Failed to send reply: {status_message}")
        except Exception as e:
            logger.error(f"❌ Error sending reply: {e}")
    
    def add_important_contact(self, phone_number: str):
        """Add a contact to the important contacts list."""
        self.important_contacts.add(phone_number)
        logger.info(f"⭐ Added important contact: {phone_number}")
    
    def remove_important_contact(self, phone_number: str):
        """Remove a contact from the important contacts list."""
        self.important_contacts.discard(phone_number)
        logger.info(f"⭐ Removed important contact: {phone_number}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get handler statistics."""
        return {
            'total_messages': self.message_count,
            'blocked_senders': len(self.blocked_senders),
            'important_contacts': len(self.important_contacts),
            'auto_reply_enabled': self.auto_reply_enabled,
            'recent_messages': len(self.processed_messages)
        }

async def main():
    """Main function to run the advanced message handler."""
    logger.info("🚀 Starting Advanced WhatsApp Reactive Message Handler")
    
    # Create handler instance
    handler = AdvancedMessageHandler()
    
    # Add some example important contacts
    handler.add_important_contact('1234567890')  # Replace with actual phone numbers
    handler.add_important_contact('0987654321')
    
    # Register the handler with the MCP server
    add_message_handler(handler.handle_message)
    logger.info("🔗 Handler registered with MCP server")
    
    logger.info("📋 Handler capabilities:")
    logger.info("   ✅ Auto-reply to greetings and keywords")
    logger.info("   ✅ Media message acknowledgment")
    logger.info("   ✅ Command processing (/help, /status, etc.)")
    logger.info("   ✅ Sender blocking/unblocking")
    logger.info("   ✅ Important contact handling")
    logger.info("   ✅ Message forwarding rules")
    logger.info("")
    logger.info("🔄 Handler is now active and processing messages...")
    logger.info("   (Make sure the WhatsApp bridge and MCP server are running)")
    
    # Keep the handler running
    try:
        while True:
            await asyncio.sleep(1)
            
            # Print statistics every 30 seconds
            if handler.message_count > 0 and handler.message_count % 10 == 0:
                stats = handler.get_statistics()
                logger.info(f"📊 Statistics: {stats}")
                
    except KeyboardInterrupt:
        logger.info("👋 Shutting down handler...")
        remove_message_handler(handler.handle_message)
        logger.info("✅ Handler unregistered successfully")

if __name__ == "__main__":
    asyncio.run(main())
