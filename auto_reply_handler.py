#!/usr/bin/env python3
"""
Auto-reply handler for WhatsApp messages.

This script registers an auto-reply handler with the MCP server to automatically
respond to incoming WhatsApp messages.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the MCP server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'whatsapp-mcp-server'))

from main import add_message_handler
from whatsapp import send_message

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoReplyHandler:
    """Auto-reply handler for WhatsApp messages."""
    
    def __init__(self):
        self.message_count = 0
        self.reply_count = 0
        self.last_sender = None
        self.last_message_time = None
        
        # Auto-reply rules
        self.auto_reply_rules = {
            # Greeting responses
            'hello': 'Hello! How can I help you today?',
            'hi': 'Hi there! What can I do for you?',
            'hey': 'Hey! How are you doing?',
            'good morning': 'Good morning! Have a great day!',
            'good afternoon': 'Good afternoon! How can I assist you?',
            'good evening': 'Good evening! What do you need help with?',
            
            # Question responses
            'how are you': 'I\'m doing great, thank you for asking! How about you?',
            'how are you?': 'I\'m doing great, thank you for asking! How about you?',
            'what\'s up': 'Not much! Just here to help. What\'s up with you?',
            'whats up': 'Not much! Just here to help. What\'s up with you?',
            
            # Help responses
            'help': 'I can help you with various tasks! Try asking me about the weather, time, or just chat with me.',
            'what can you do': 'I can help you with information, answer questions, and have conversations. What would you like to know?',
            
            # Status responses
            'status': f'I am online and ready to help! Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'ping': 'Pong! 🏓',
            
            # Time responses
            'time': f'The current time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'what time': f'The current time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            
            # Thank you responses
            'thank you': 'You\'re welcome! Is there anything else I can help you with?',
            'thanks': 'You\'re welcome! Is there anything else I can help you with?',
        }
        
        # Default responses for when no specific rule matches
        self.default_responses = [
            "Thanks for your message! I'm here to help.",
            "I received your message. How can I assist you?",
            "Hello! I'm ready to help you with anything you need.",
            "Thanks for reaching out! What can I do for you?",
            "I'm here and ready to help! What do you need?"
        ]
        
        # Responses for media messages
        self.media_responses = {
            'image': 'Thanks for the image! I can see you sent me a picture.',
            'video': 'Thanks for the video! I received your video message.',
            'audio': 'Thanks for the audio message! I can hear you.',
            'document': 'Thanks for the document! I received your file.',
        }
    
    async def handle_message(self, message_data: Dict[str, Any]):
        """Handle incoming WhatsApp messages and send auto-replies."""
        self.message_count += 1
        
        # Extract message information
        message_id = message_data.get('message_id', 'unknown')
        chat_jid = message_data.get('chat_jid', 'unknown')
        sender = message_data.get('sender', 'unknown')
        content = message_data.get('content', '').strip()
        media_type = message_data.get('media_type', '')
        chat_name = message_data.get('chat_name', 'unknown')
        
        # Log the message
        logger.info(f"📨 Message #{self.message_count} from {sender} ({chat_name})")
        if media_type:
            logger.info(f"   Media: {media_type}")
        else:
            logger.info(f"   Text: {content}")
        
        # Skip if it's from the same sender within 30 seconds (prevent spam)
        current_time = datetime.now()
        if (self.last_sender == sender and 
            self.last_message_time and 
            (current_time - self.last_message_time).seconds < 30):
            logger.info(f"⏭️ Skipping auto-reply to {sender} (too soon after last message)")
            return
        
        self.last_sender = sender
        self.last_message_time = current_time
        
        # Determine response
        response = await self.get_response(content, media_type, sender, chat_name)
        
        if response:
            # Send the reply
            success = await self.send_reply(chat_jid, response)
            if success:
                self.reply_count += 1
                logger.info(f"🤖 Auto-reply sent to {sender}: {response}")
            else:
                logger.error(f"❌ Failed to send auto-reply to {sender}")
        else:
            logger.info(f"⏭️ No auto-reply needed for message from {sender}")
    
    async def get_response(self, content: str, media_type: str, sender: str, chat_name: str) -> str:
        """Determine the appropriate response for a message."""
        
        # Handle media messages
        if media_type and media_type in self.media_responses:
            return self.media_responses[media_type]
        
        # Handle text messages
        if not content:
            return None
        
        content_lower = content.lower().strip()
        
        # Check for exact matches first
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
        greeting_words = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(word in content_lower for word in greeting_words):
            return "Hello! How can I help you today?"
        
        # Default response for unrecognized messages (but not too often)
        if self.message_count % 3 == 0:  # Reply to every 3rd unrecognized message
            import random
            return random.choice(self.default_responses)
        
        return None
    
    async def send_reply(self, chat_jid: str, message: str) -> bool:
        """Send a reply message."""
        try:
            success, status_message = send_message(chat_jid, message)
            return success
        except Exception as e:
            logger.error(f"Error sending reply: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics."""
        return {
            'total_messages': self.message_count,
            'total_replies': self.reply_count,
            'reply_rate': f"{(self.reply_count / self.message_count * 100):.1f}%" if self.message_count > 0 else "0%",
            'last_sender': self.last_sender,
            'last_message_time': self.last_message_time.isoformat() if self.last_message_time else None
        }

async def main():
    """Main function to start the auto-reply handler."""
    logger.info("🤖 Starting WhatsApp Auto-Reply Handler")
    
    # Create handler instance
    handler = AutoReplyHandler()
    
    # Register the handler with the MCP server
    add_message_handler(handler.handle_message)
    logger.info("✅ Auto-reply handler registered with MCP server")
    
    logger.info("📋 Auto-reply features:")
    logger.info("   ✅ Greeting responses (hello, hi, hey, etc.)")
    logger.info("   ✅ Question responses (how are you, what's up, etc.)")
    logger.info("   ✅ Help responses")
    logger.info("   ✅ Time and status responses")
    logger.info("   ✅ Media message acknowledgments")
    logger.info("   ✅ Spam prevention (30-second cooldown)")
    logger.info("   ✅ Smart default responses")
    logger.info("")
    logger.info("🔄 Auto-reply handler is now active!")
    logger.info("   (Make sure the WhatsApp bridge and MCP server are running)")
    
    # Keep the handler running and show stats periodically
    try:
        while True:
            await asyncio.sleep(30)  # Show stats every 30 seconds
            
            stats = handler.get_stats()
            logger.info(f"📊 Stats: {stats['total_messages']} messages, {stats['total_replies']} replies ({stats['reply_rate']})")
            
    except KeyboardInterrupt:
        logger.info("👋 Shutting down auto-reply handler...")
        logger.info("✅ Auto-reply handler stopped")

if __name__ == "__main__":
    asyncio.run(main())
