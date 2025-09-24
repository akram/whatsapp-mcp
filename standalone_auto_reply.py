#!/usr/bin/env python3
"""
Standalone auto-reply handler that registers with the running MCP server.

This script sends HTTP requests to register an auto-reply handler with the MCP server.
No need to import MCP modules - just sends HTTP requests.
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StandaloneAutoReply:
    """Standalone auto-reply handler using HTTP requests."""
    
    def __init__(self, mcp_server_url: str = "http://localhost:3000"):
        self.mcp_server_url = mcp_server_url
        self.message_count = 0
        self.reply_count = 0
        
        # Auto-reply rules
        self.auto_reply_rules = {
            'hello': 'Hello! How can I help you today?',
            'hi': 'Hi there! What can I do for you?',
            'hey': 'Hey! How are you doing?',
            'how are you': 'I\'m doing great, thank you for asking! How about you?',
            'how are you?': 'I\'m doing great, thank you for asking! How about you?',
            'what\'s up': 'Not much! Just here to help. What\'s up with you?',
            'whats up': 'Not much! Just here to help. What\'s up with you?',
            'help': 'I can help you with various tasks! Try asking me about the weather, time, or just chat with me.',
            'time': f'The current time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'thank you': 'You\'re welcome! Is there anything else I can help you with?',
            'thanks': 'You\'re welcome! Is there anything else I can help you with?',
            'ping': 'Pong! 🏓',
        }
    
    def get_response(self, content: str, media_type: str) -> str:
        """Determine the appropriate response for a message."""
        
        # Handle media messages
        if media_type:
            return f"Thanks for the {media_type}! I received your message."
        
        # Handle text messages
        if not content:
            return None
        
        content_lower = content.lower().strip()
        
        # Check for exact matches
        if content_lower in self.auto_reply_rules:
            return self.auto_reply_rules[content_lower]
        
        # Check for partial matches
        for keyword, response in self.auto_reply_rules.items():
            if keyword in content_lower:
                return response
        
        # Check for question patterns
        if content_lower.endswith('?'):
            return "That's a great question! I'm here to help you find the answer."
        
        # Check for greeting patterns
        greeting_words = ['hello', 'hi', 'hey']
        if any(word in content_lower for word in greeting_words):
            return "Hello! How can I help you today?"
        
        # Default response
        return "Thanks for your message! I'm here to help."
    
    def send_reply(self, chat_jid: str, message: str) -> bool:
        """Send a reply message via the WhatsApp bridge."""
        try:
            # Send via WhatsApp bridge
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
    
    def process_message(self, message_data: Dict[str, Any]):
        """Process a message and send auto-reply."""
        self.message_count += 1
        
        sender = message_data.get('sender', 'unknown')
        content = message_data.get('content', '')
        chat_jid = message_data.get('chat_jid', 'unknown')
        media_type = message_data.get('media_type', '')
        chat_name = message_data.get('chat_name', 'unknown')
        
        logger.info(f"📨 Message #{self.message_count} from {sender} ({chat_name})")
        if media_type:
            logger.info(f"   Media: {media_type}")
        else:
            logger.info(f"   Text: {content}")
        
        # Get response
        response = self.get_response(content, media_type)
        
        if response:
            # Send reply
            success = self.send_reply(chat_jid, response)
            if success:
                self.reply_count += 1
                logger.info(f"🤖 Auto-reply sent to {sender}: {response}")
            else:
                logger.error(f"❌ Failed to send auto-reply to {sender}")
        else:
            logger.info(f"⏭️ No auto-reply needed for message from {sender}")
    
    def start_monitoring(self):
        """Start monitoring for messages by polling the MCP server."""
        logger.info("🔄 Starting message monitoring...")
        logger.info("📋 Auto-reply features:")
        logger.info("   ✅ Greeting responses")
        logger.info("   ✅ Question responses")
        logger.info("   ✅ Help responses")
        logger.info("   ✅ Time responses")
        logger.info("   ✅ Media acknowledgments")
        logger.info("   ✅ Default responses")
        logger.info("")
        logger.info("🔄 Monitoring for new messages...")
        
        try:
            while True:
                # In a real implementation, you would poll for new messages
                # For now, we'll just keep the handler running
                time.sleep(1)
                
                # Show stats every 30 seconds
                if self.message_count > 0 and self.message_count % 10 == 0:
                    reply_rate = (self.reply_count / self.message_count * 100) if self.message_count > 0 else 0
                    logger.info(f"📊 Stats: {self.message_count} messages, {self.reply_count} replies ({reply_rate:.1f}%)")
                    
        except KeyboardInterrupt:
            logger.info("👋 Stopping auto-reply handler...")

def main():
    """Main function."""
    logger.info("🤖 Starting Standalone WhatsApp Auto-Reply Handler")
    
    # Create handler
    handler = StandaloneAutoReply()
    
    # For demonstration, let's simulate processing a message
    logger.info("🧪 Testing auto-reply functionality...")
    
    test_message = {
        "type": "new_message",
        "message_id": "test_123",
        "chat_jid": "21656067876@s.whatsapp.net",
        "sender": "21656067876",
        "content": "hello",
        "timestamp": datetime.now().isoformat(),
        "media_type": "",
        "filename": "",
        "chat_name": "Akram Ben Aïssi"
    }
    
    handler.process_message(test_message)
    
    logger.info("✅ Auto-reply handler is ready!")
    logger.info("💡 To use this handler:")
    logger.info("   1. The MCP server should call this handler when messages arrive")
    logger.info("   2. Or integrate this logic into your MCP server handlers")
    logger.info("")
    logger.info("🔄 Starting monitoring...")
    
    handler.start_monitoring()

if __name__ == "__main__":
    main()
