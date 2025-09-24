#!/usr/bin/env python3
"""
Quick auto-reply setup script.

This script quickly registers a simple auto-reply handler with the MCP server.
Run this script to enable automatic replies to WhatsApp messages.
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

async def simple_auto_reply(message_data: Dict[str, Any]):
    """Simple auto-reply function."""
    sender = message_data.get('sender', 'unknown')
    content = message_data.get('content', '').lower().strip()
    chat_jid = message_data.get('chat_jid', 'unknown')
    media_type = message_data.get('media_type', '')
    chat_name = message_data.get('chat_name', 'unknown')
    
    logger.info(f"📨 Message from {sender} ({chat_name}): {content}")
    
    # Handle media messages
    if media_type:
        response = f"Thanks for the {media_type}! I received your message."
        await send_reply(chat_jid, response)
        logger.info(f"🤖 Sent media response to {sender}")
        return
    
    # Handle text messages
    if not content:
        return
    
    # Simple keyword-based responses
    if any(word in content for word in ['hello', 'hi', 'hey']):
        response = "Hello! How can I help you today?"
    elif any(word in content for word in ['how are you', 'how are you?']):
        response = "I'm doing great, thank you! How about you?"
    elif 'help' in content:
        response = "I'm here to help! What do you need assistance with?"
    elif 'time' in content:
        response = f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elif 'thank' in content:
        response = "You're welcome! Is there anything else I can help with?"
    elif content.endswith('?'):
        response = "That's a great question! I'm here to help you find the answer."
    else:
        # Default response for other messages
        response = "Thanks for your message! I'm here to help."
    
    await send_reply(chat_jid, response)
    logger.info(f"🤖 Sent response to {sender}: {response}")

async def send_reply(chat_jid: str, message: str):
    """Send a reply message."""
    try:
        success, status_message = send_message(chat_jid, message)
        if not success:
            logger.error(f"Failed to send reply: {status_message}")
    except Exception as e:
        logger.error(f"Error sending reply: {e}")

def main():
    """Register the auto-reply handler."""
    logger.info("🤖 Registering simple auto-reply handler...")
    
    # Register the handler
    add_message_handler(simple_auto_reply)
    
    logger.info("✅ Auto-reply handler registered!")
    logger.info("📋 Handler will respond to:")
    logger.info("   • Greetings (hello, hi, hey)")
    logger.info("   • Questions (how are you, help)")
    logger.info("   • Time requests")
    logger.info("   • Thank you messages")
    logger.info("   • Media messages")
    logger.info("   • General messages")
    logger.info("")
    logger.info("🔄 Auto-replies are now active!")
    logger.info("   (Keep this script running or the handler will be unregistered)")

if __name__ == "__main__":
    main()
    
    # Keep the script running
    try:
        logger.info("Press Ctrl+C to stop auto-replies...")
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("👋 Auto-reply handler stopped")
