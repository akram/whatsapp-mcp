# WhatsApp MCP Reactive Message Handling

This document describes the reactive message handling functionality added to the WhatsApp MCP server, allowing it to automatically respond to incoming WhatsApp messages in real-time.

## Overview

The reactive message handling system consists of:

1. **WhatsApp Bridge Enhancement**: Modified to send notifications to the MCP server when new messages arrive
2. **MCP Server Enhancement**: Added notification endpoint and handler registration system
3. **Handler System**: Allows registration of custom message processing functions
4. **Example Implementations**: Sample handlers demonstrating various use cases

## Architecture

```
WhatsApp → Go Bridge → SQLite Database
                ↓
         HTTP Notification
                ↓
    MCP Server → Registered Handlers
```

### Components

- **Go WhatsApp Bridge** (`whatsapp-bridge/main.go`): Sends HTTP notifications to MCP server
- **MCP Server** (`whatsapp-mcp-server/main.py`): Receives notifications and calls registered handlers
- **Handler Functions**: Custom functions that process incoming messages
- **Notification Endpoint**: `/api/message-notification` for receiving message notifications

## Features

### ✅ Real-time Message Processing
- Automatic notification when new messages arrive
- Support for both text and media messages
- Message metadata including sender, chat, timestamp, etc.

### ✅ Handler Registration System
- Register multiple handlers for different processing needs
- Support for both sync and async handlers
- Easy handler management (add/remove)

### ✅ Message Filtering
- Block/unblock specific senders
- Process messages from important contacts differently
- Content-based filtering and routing

### ✅ Auto-Response Capabilities
- Keyword-based responses
- Greeting detection and responses
- Command processing (e.g., `/help`, `/status`)
- Media message acknowledgments

### ✅ Advanced Features
- Message forwarding rules
- Statistics tracking
- Integration with external services
- Customizable response logic

## Usage

### Basic Setup

1. **Start the WhatsApp Bridge**:
   ```bash
   cd whatsapp-bridge
   go run main.go
   ```

2. **Start the MCP Server**:
   ```bash
   cd whatsapp-mcp-server
   python main.py
   ```

3. **Register Message Handlers**:
   ```python
   from main import add_message_handler
   
   async def my_handler(message_data):
       print(f"New message from {message_data['sender']}: {message_data['content']}")
   
   add_message_handler(my_handler)
   ```

### Example Handlers

#### Simple Handler
```python
def simple_handler(message_data):
    """Basic synchronous handler."""
    print(f"Message from {message_data['sender']}: {message_data['content']}")

add_message_handler(simple_handler)
```

#### Advanced Handler
```python
class AdvancedHandler:
    async def handle_message(self, message_data):
        sender = message_data['sender']
        content = message_data['content']
        
        # Auto-reply to greetings
        if 'hello' in content.lower():
            await self.send_reply(message_data['chat_jid'], "Hello! How can I help?")
        
        # Process commands
        if content.startswith('/'):
            await self.process_command(message_data)

handler = AdvancedHandler()
add_message_handler(handler.handle_message)
```

### Message Data Structure

Each handler receives a dictionary with the following structure:

```python
{
    "type": "new_message",
    "message_id": "unique_message_id",
    "chat_jid": "1234567890@s.whatsapp.net",
    "sender": "1234567890",
    "content": "Message text content",
    "timestamp": "2024-01-01T12:00:00Z",
    "media_type": "image",  # or "video", "audio", "document", ""
    "filename": "image.jpg",
    "chat_name": "Contact Name"
}
```

## API Endpoints

### Notification Endpoint
- **URL**: `POST /api/message-notification`
- **Purpose**: Receive message notifications from WhatsApp bridge
- **Body**: JSON message data
- **Response**: Success/failure status

### Handler Management
- **Function**: `add_message_handler(handler_function)`
- **Function**: `remove_message_handler(handler_function)`
- **Purpose**: Register/unregister message processing functions

## Configuration

### Environment Variables

- `MCP_SERVER_URL`: URL of the MCP server (default: `http://localhost:3000`)
- `MESSAGES_DB_PATH`: Path to the SQLite database
- `MCP_HOST`: MCP server host (default: `0.0.0.0`)
- `MCP_PORT`: MCP server port (default: `3000`)

### Handler Configuration

Handlers can be configured with various options:

```python
class ConfigurableHandler:
    def __init__(self):
        self.auto_reply_enabled = True
        self.blocked_senders = set()
        self.important_contacts = set()
        self.keyword_responses = {
            'help': 'I can help you with...',
            'time': 'Current time is...'
        }
```

## Testing

Run the test suite to verify functionality:

```bash
python test_reactive_functionality.py
```

The test suite checks:
- Server endpoint accessibility
- WhatsApp bridge connection
- Notification endpoint functionality
- Handler registration and processing
- Media message handling

## Examples

### Example 1: Basic Auto-Reply
```python
async def auto_reply_handler(message_data):
    content = message_data['content'].lower()
    chat_jid = message_data['chat_jid']
    
    if 'hello' in content:
        await send_reply(chat_jid, "Hello! How can I help you?")
    elif 'help' in content:
        await send_reply(chat_jid, "I can help you with various tasks...")

add_message_handler(auto_reply_handler)
```

### Example 2: Message Forwarding
```python
async def forwarding_handler(message_data):
    sender = message_data['sender']
    content = message_data['content']
    
    # Forward urgent messages
    if 'urgent' in content.lower():
        forward_message = f"URGENT from {sender}: {content}"
        await send_reply("admin_chat_jid@g.us", forward_message)

add_message_handler(forwarding_handler)
```

### Example 3: Statistics Tracking
```python
class StatsHandler:
    def __init__(self):
        self.message_count = 0
        self.sender_stats = {}
    
    async def handle_message(self, message_data):
        self.message_count += 1
        sender = message_data['sender']
        self.sender_stats[sender] = self.sender_stats.get(sender, 0) + 1
        
        print(f"Total messages: {self.message_count}")
        print(f"Messages from {sender}: {self.sender_stats[sender]}")

stats_handler = StatsHandler()
add_message_handler(stats_handler.handle_message)
```

## Troubleshooting

### Common Issues

1. **Notifications not received**:
   - Check if WhatsApp bridge is running on port 8080
   - Verify MCP server is running on port 3000
   - Check network connectivity between services

2. **Handlers not called**:
   - Ensure handlers are registered with `add_message_handler()`
   - Check handler function signatures (should accept message_data parameter)
   - Verify no exceptions in handler functions

3. **Auto-replies not working**:
   - Check if `send_message()` function is working
   - Verify chat JID format is correct
   - Ensure WhatsApp bridge can send messages

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks

Check service status:

```bash
# MCP Server health
curl http://localhost:3000/health

# WhatsApp Bridge (should return 405 Method Not Allowed for GET)
curl http://localhost:8080/api/send
```

## Security Considerations

- **Input Validation**: Always validate message content before processing
- **Rate Limiting**: Implement rate limiting to prevent spam
- **Access Control**: Restrict handler registration to trusted code
- **Data Privacy**: Be careful with message content logging and storage

## Performance

- **Async Handlers**: Use async handlers for better performance
- **Handler Efficiency**: Keep handlers lightweight and fast
- **Error Handling**: Implement proper error handling to prevent crashes
- **Resource Management**: Clean up resources in long-running handlers

## Future Enhancements

- **Message Queuing**: Implement message queuing for high-volume scenarios
- **Handler Priorities**: Add priority system for handler execution order
- **Conditional Handlers**: Support conditional handler registration
- **Webhook Integration**: Add webhook support for external integrations
- **Message Templates**: Support for message templates and formatting
- **Analytics**: Built-in analytics and reporting capabilities

## Contributing

When adding new features:

1. Update the handler registration system if needed
2. Add comprehensive tests
3. Update documentation
4. Consider backward compatibility
5. Add example implementations

## License

This reactive message handling system is part of the WhatsApp MCP project and follows the same license terms.
