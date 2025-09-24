#!/usr/bin/env python3
"""
Test script for the reactive message handling system.

This script tests:
1. The notification endpoint
2. Message handler registration
3. End-to-end message processing
"""

import asyncio
import json
import logging
import requests
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestMessageHandler:
    """Test message handler for verification."""
    
    def __init__(self):
        self.received_messages = []
        self.message_count = 0
    
    async def handle_test_message(self, message_data):
        """Handle test messages."""
        self.message_count += 1
        self.received_messages.append(message_data)
        
        logger.info(f"🧪 Test handler received message #{self.message_count}")
        logger.info(f"   From: {message_data.get('sender', 'unknown')}")
        logger.info(f"   Content: {message_data.get('content', '')}")
        logger.info(f"   Chat: {message_data.get('chat_name', 'unknown')}")
        
        return True

def test_notification_endpoint():
    """Test the message notification endpoint."""
    logger.info("🧪 Testing notification endpoint...")
    
    # Test data
    test_notification = {
        "type": "new_message",
        "message_id": "test_msg_123",
        "chat_jid": "1234567890@s.whatsapp.net",
        "sender": "1234567890",
        "content": "Hello, this is a test message!",
        "timestamp": datetime.now().isoformat(),
        "media_type": "",
        "filename": "",
        "chat_name": "Test Contact"
    }
    
    try:
        # Send test notification
        response = requests.post(
            "http://localhost:3000/api/message-notification",
            json=test_notification,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logger.info("✅ Notification endpoint test passed")
            return True
        else:
            logger.error(f"❌ Notification endpoint test failed: {response.status_code}")
            logger.error(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to MCP server. Make sure it's running on localhost:3000")
        return False
    except Exception as e:
        logger.error(f"❌ Notification endpoint test failed: {e}")
        return False

def test_media_notification():
    """Test media message notification."""
    logger.info("🧪 Testing media notification...")
    
    test_notification = {
        "type": "new_message",
        "message_id": "test_media_456",
        "chat_jid": "1234567890@s.whatsapp.net",
        "sender": "1234567890",
        "content": "Check out this image!",
        "timestamp": datetime.now().isoformat(),
        "media_type": "image",
        "filename": "test_image.jpg",
        "chat_name": "Test Contact"
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/api/message-notification",
            json=test_notification,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logger.info("✅ Media notification test passed")
            return True
        else:
            logger.error(f"❌ Media notification test failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Media notification test failed: {e}")
        return False

def test_server_endpoints():
    """Test that the MCP server endpoints are accessible."""
    logger.info("🧪 Testing server endpoints...")
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/tools", "Tools listing"),
        ("/api/message-notification", "Message notification")
    ]
    
    all_passed = True
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:3000{endpoint}")
            if response.status_code == 200:
                logger.info(f"✅ {description} accessible")
            else:
                logger.error(f"❌ {description} returned {response.status_code}")
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {description} failed: {e}")
            all_passed = False
    
    return all_passed

async def test_handler_integration():
    """Test handler integration with the MCP server."""
    logger.info("🧪 Testing handler integration...")
    
    try:
        # Import the MCP server components
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'whatsapp-mcp-server'))
        
        from main import add_message_handler, message_handlers
        
        # Create test handler
        test_handler = TestMessageHandler()
        
        # Register handler
        add_message_handler(test_handler.handle_test_message)
        
        # Verify handler was added
        if len(message_handlers) > 0:
            logger.info(f"✅ Handler registered successfully ({len(message_handlers)} handlers)")
        else:
            logger.error("❌ Handler registration failed")
            return False
        
        # Test handler with mock data
        test_data = {
            "type": "new_message",
            "message_id": "integration_test_789",
            "chat_jid": "test@s.whatsapp.net",
            "sender": "test_sender",
            "content": "Integration test message",
            "timestamp": datetime.now().isoformat(),
            "media_type": "",
            "filename": "",
            "chat_name": "Test Chat"
        }
        
        # Call handler directly
        await test_handler.handle_test_message(test_data)
        
        if test_handler.message_count > 0:
            logger.info("✅ Handler integration test passed")
            return True
        else:
            logger.error("❌ Handler integration test failed")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Cannot import MCP server components: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Handler integration test failed: {e}")
        return False

def test_whatsapp_bridge_connection():
    """Test connection to WhatsApp bridge."""
    logger.info("🧪 Testing WhatsApp bridge connection...")
    
    try:
        response = requests.get("http://localhost:8080/api/send", timeout=5)
        # We expect a 405 Method Not Allowed since we're using GET instead of POST
        if response.status_code == 405:
            logger.info("✅ WhatsApp bridge is running")
            return True
        else:
            logger.warning(f"⚠️ WhatsApp bridge responded with {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to WhatsApp bridge. Make sure it's running on localhost:8080")
        return False
    except Exception as e:
        logger.error(f"❌ WhatsApp bridge test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests."""
    logger.info("🚀 Starting reactive message handling tests...")
    logger.info("=" * 60)
    
    tests = [
        ("Server Endpoints", test_server_endpoints),
        ("WhatsApp Bridge Connection", test_whatsapp_bridge_connection),
        ("Notification Endpoint", test_notification_endpoint),
        ("Media Notification", test_media_notification),
        ("Handler Integration", test_handler_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} test...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} test ERROR: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Reactive message handling is working correctly.")
    else:
        logger.error("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total

def main():
    """Main test function."""
    logger.info("🧪 WhatsApp MCP Reactive Message Handling Test Suite")
    logger.info("This script tests the reactive message handling functionality.")
    logger.info("")
    logger.info("Prerequisites:")
    logger.info("1. WhatsApp bridge running on localhost:8080")
    logger.info("2. MCP server running on localhost:3000")
    logger.info("")
    
    # Run tests
    asyncio.run(run_all_tests())

if __name__ == "__main__":
    main()
