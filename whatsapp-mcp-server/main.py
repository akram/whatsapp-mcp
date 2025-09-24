from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.requests import Request
import asyncio
import json
import logging
from whatsapp import (
    search_contacts as whatsapp_search_contacts,
    list_messages as whatsapp_list_messages,
    list_chats as whatsapp_list_chats,
    get_chat as whatsapp_get_chat,
    get_direct_chat_by_contact as whatsapp_get_direct_chat_by_contact,
    get_contact_chats as whatsapp_get_contact_chats,
    get_last_interaction as whatsapp_get_last_interaction,
    get_message_context as whatsapp_get_message_context,
    send_message as whatsapp_send_message,
    send_file as whatsapp_send_file,
    send_audio_message as whatsapp_audio_voice_message,
    download_media as whatsapp_download_media
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store for message notification handlers
message_handlers = []

# Initialize FastMCP server
mcp = FastMCP("whatsapp")

def add_message_handler(handler):
    """Add a message handler function that will be called when new messages arrive."""
    message_handlers.append(handler)
    logger.info(f"Added message handler. Total handlers: {len(message_handlers)}")

def remove_message_handler(handler):
    """Remove a message handler."""
    if handler in message_handlers:
        message_handlers.remove(handler)
        logger.info(f"Removed message handler. Total handlers: {len(message_handlers)}")

async def notify_message_handlers(message_data: Dict[str, Any]):
    """Notify all registered message handlers about a new message."""
    logger.info(f"Notifying {len(message_handlers)} handlers about new message from {message_data.get('sender', 'unknown')}")
    
    for handler in message_handlers:
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(message_data)
            else:
                handler(message_data)
        except Exception as e:
            logger.error(f"Error in message handler: {e}")

@mcp.tool(
    name="search_contacts",
    description="Search WhatsApp contacts by name or phone number."
)
def search_contacts(query: str) -> List[Dict[str, Any]]:
    """Search WhatsApp contacts by name or phone number.
    
    Args:
        query: Search term to match against contact names or phone numbers
    """
    contacts = whatsapp_search_contacts(query)
    
    # Convert Contact objects to dictionaries for proper serialization
    result = []
    for contact in contacts:
        contact_dict = {
            "phone_number": contact.phone_number,
            "name": contact.name,
            "jid": contact.jid
        }
        result.append(contact_dict)
    
    return result

@mcp.tool(
    name="list_messages",
    description="Get WhatsApp messages matching specified criteria with optional context.",
    
)
def list_messages(
    after: Optional[str] = None,
    before: Optional[str] = None,
    sender_phone_number: Optional[str] = None,
    chat_jid: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_context: bool = True,
    context_before: Optional[int] = 1,
    context_after: Optional[int] = 1
) -> List[Dict[str, Any]]:
    """Get WhatsApp messages matching specified criteria with optional context.
    
    Args:
        after: Optional ISO-8601 formatted string to only return messages after this date
        before: Optional ISO-8601 formatted string to only return messages before this date
        sender_phone_number: Optional phone number to filter messages by sender
        chat_jid: Optional chat JID to filter messages by chat
        query: Optional search term to filter messages by content
        limit: Maximum number of messages to return (default 20)
        page: Page number for pagination (default 0)
        include_context: Whether to include messages before and after matches (default True)
        context_before: Number of messages to include before each match (default 1)
        context_after: Number of messages to include after each match (default 1)
    """
    # Handle string "None" values from MCP client
    if isinstance(after, str) and after.lower() == "none":
        after = None
    if isinstance(before, str) and before.lower() == "none":
        before = None
    if isinstance(sender_phone_number, str) and sender_phone_number.lower() == "none":
        sender_phone_number = None
    if isinstance(chat_jid, str) and chat_jid.lower() == "none":
        chat_jid = None
    if isinstance(query, str) and query.lower() == "none":
        query = None
    if isinstance(context_before, str) and context_before.lower() == "none":
        context_before = 1
    if isinstance(context_after, str) and context_after.lower() == "none":
        context_after = 1
    
    messages = whatsapp_list_messages(
        after=after,
        before=before,
        sender_phone_number=sender_phone_number,
        chat_jid=chat_jid,
        query=query,
        limit=limit,
        page=page,
        include_context=include_context,
        context_before=context_before,
        context_after=context_after
    )
    
    # Handle case where whatsapp_list_messages returns a string
    if isinstance(messages, str):
        # If it's a string, return it as a single message entry
        return [{
            "id": "formatted_output",
            "chat_jid": chat_jid or "unknown",
            "sender": sender_phone_number or "unknown",
            "content": messages,
            "timestamp": None,
            "is_from_me": False,
            "chat_name": "Formatted Output",
            "media_type": None
        }]
    
    # Convert Message objects to dictionaries for proper serialization
    result = []
    for message in messages:
        message_dict = {
            "id": message.id,
            "chat_jid": message.chat_jid,
            "sender": message.sender,
            "content": message.content,
            "timestamp": message.timestamp.isoformat() if message.timestamp else None,
            "is_from_me": message.is_from_me,
            "message_type": message.message_type,
            "media_path": message.media_path
        }
        result.append(message_dict)
    
    return result

@mcp.tool(
    name="list_chats",
    description="Get WhatsApp chats matching specified criteria.",
    
)
def list_chats(
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_last_message: bool = True,
    sort_by: str = "last_active"
) -> List[Dict[str, Any]]:
    """Get WhatsApp chats matching specified criteria.
    
    Args:
        query: Optional search term to filter chats by name or JID
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
        include_last_message: Whether to include the last message in each chat (default True)
        sort_by: Field to sort results by, either "last_active" or "name" (default "last_active")
    """
    # Handle string "None" values from MCP client
    if isinstance(query, str) and query.lower() == "none":
        query = None
    
    chats = whatsapp_list_chats(
        query=query,
        limit=limit,
        page=page,
        include_last_message=include_last_message,
        sort_by=sort_by
    )
    
    # Convert Chat objects to dictionaries for proper serialization
    result = []
    for chat in chats:
        chat_dict = {
            "jid": chat.jid,
            "name": chat.name,
            "last_message_time": chat.last_message_time.isoformat() if chat.last_message_time else None,
            "last_message": chat.last_message,
            "last_sender": chat.last_sender,
            "last_is_from_me": chat.last_is_from_me
        }
        result.append(chat_dict)
    
    return result

@mcp.tool(
    name="get_chat",
    description="Get WhatsApp chat metadata by JID.",
    
)
def get_chat(chat_jid: str, include_last_message: bool = True) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by JID.
    
    Args:
        chat_jid: The JID of the chat to retrieve
        include_last_message: Whether to include the last message (default True)
    """
    chat = whatsapp_get_chat(chat_jid, include_last_message)
    
    if chat is None:
        return None
    
    # Convert Chat object to dictionary for proper serialization
    chat_dict = {
        "jid": chat.jid,
        "name": chat.name,
        "last_message_time": chat.last_message_time.isoformat() if chat.last_message_time else None,
        "last_message": chat.last_message,
        "last_sender": chat.last_sender,
        "last_is_from_me": chat.last_is_from_me
    }
    
    return chat_dict

@mcp.tool(
    name="get_direct_chat_by_contact",
    description="Get WhatsApp chat metadata by sender phone number.",
    
)
def get_direct_chat_by_contact(sender_phone_number: str) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by sender phone number.
    
    Args:
        sender_phone_number: The phone number to search for
    """
    chat = whatsapp_get_direct_chat_by_contact(sender_phone_number)
    
    if chat is None:
        return None
    
    # Convert Chat object to dictionary for proper serialization
    chat_dict = {
        "jid": chat.jid,
        "name": chat.name,
        "last_message_time": chat.last_message_time.isoformat() if chat.last_message_time else None,
        "last_message": chat.last_message,
        "last_sender": chat.last_sender,
        "last_is_from_me": chat.last_is_from_me
    }
    
    return chat_dict

@mcp.tool(
    name="get_contact_chats",
    description="Get all WhatsApp chats involving the contact.",
    
)
def get_contact_chats(jid: str, limit: int = 20, page: int = 0) -> List[Dict[str, Any]]:
    """Get all WhatsApp chats involving the contact.
    
    Args:
        jid: The contact's JID to search for
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
    """
    chats = whatsapp_get_contact_chats(jid, limit, page)
    
    # Convert Chat objects to dictionaries for proper serialization
    result = []
    for chat in chats:
        chat_dict = {
            "jid": chat.jid,
            "name": chat.name,
            "last_message_time": chat.last_message_time.isoformat() if chat.last_message_time else None,
            "last_message": chat.last_message,
            "last_sender": chat.last_sender,
            "last_is_from_me": chat.last_is_from_me
        }
        result.append(chat_dict)
    
    return result

@mcp.tool(
    name="get_last_interaction",
    description="Get most recent WhatsApp message involving the contact.",
    
)
def get_last_interaction(jid: str) -> str:
    """Get most recent WhatsApp message involving the contact.
    
    Args:
        jid: The JID of the contact to search for
    """
    message = whatsapp_get_last_interaction(jid)
    return message

@mcp.tool(
    name="get_message_context",
    description="Get context around a specific WhatsApp message.",
    
)
def get_message_context(
    message_id: str,
    before: int = 5,
    after: int = 5
) -> Dict[str, Any]:
    """Get context around a specific WhatsApp message.
    
    Args:
        message_id: The ID of the message to get context for
        before: Number of messages to include before the target message (default 5)
        after: Number of messages to include after the target message (default 5)
    """
    context = whatsapp_get_message_context(message_id, before, after)
    
    if context is None:
        return None
    
    # Convert MessageContext object to dictionary for proper serialization
    context_dict = {
        "message": {
            "id": context.message.id,
            "chat_jid": context.message.chat_jid,
            "sender": context.message.sender,
            "content": context.message.content,
            "timestamp": context.message.timestamp.isoformat() if context.message.timestamp else None,
            "is_from_me": context.message.is_from_me,
            "message_type": context.message.message_type,
            "media_path": context.message.media_path
        },
        "before": [
            {
                "id": msg.id,
                "chat_jid": msg.chat_jid,
                "sender": msg.sender,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "is_from_me": msg.is_from_me,
                "message_type": msg.message_type,
                "media_path": msg.media_path
            }
            for msg in context.before
        ],
        "after": [
            {
                "id": msg.id,
                "chat_jid": msg.chat_jid,
                "sender": msg.sender,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "is_from_me": msg.is_from_me,
                "message_type": msg.message_type,
                "media_path": msg.media_path
            }
            for msg in context.after
        ]
    }
    
    return context_dict

@mcp.tool(
    name="send_message",
    description="Send a WhatsApp message to a person or group.",
    
)
def send_message(
    recipient: str,
    message: str
) -> Dict[str, Any]:
    """Send a WhatsApp message to a person or group. For group chats use the JID.

    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        message: The message text to send
    
    Returns:
        A dictionary containing success status and a status message
    """
    # Validate input
    if not recipient:
        return {
            "success": False,
            "message": "Recipient must be provided"
        }
    
    # Call the whatsapp_send_message function with the unified recipient parameter
    success, status_message = whatsapp_send_message(recipient, message)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool(
    name="send_file",
    description="Send a file such as a picture, raw audio, video or document via WhatsApp.",
    
)
def send_file(recipient: str, media_path: str) -> Dict[str, Any]:
    """Send a file such as a picture, raw audio, video or document via WhatsApp to the specified recipient. For group messages use the JID.
    
    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        media_path: The absolute path to the media file to send (image, video, document)
    
    Returns:
        A dictionary containing success status and a status message
    """
    
    # Call the whatsapp_send_file function
    success, status_message = whatsapp_send_file(recipient, media_path)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool(
    name="send_audio_message",
    description="Send any audio file as a WhatsApp audio message.",
    
)
def send_audio_message(recipient: str, media_path: str) -> Dict[str, Any]:
    """Send any audio file as a WhatsApp audio message to the specified recipient. For group messages use the JID. If it errors due to ffmpeg not being installed, use send_file instead.
    
    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        media_path: The absolute path to the audio file to send (will be converted to Opus .ogg if it's not a .ogg file)
    
    Returns:
        A dictionary containing success status and a status message
    """
    success, status_message = whatsapp_audio_voice_message(recipient, media_path)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool(
    name="download_media",
    description="Download media from a WhatsApp message and get the local file path.",
    
)
def download_media(message_id: str, chat_jid: str) -> Dict[str, Any]:
    """Download media from a WhatsApp message and get the local file path.
    
    Args:
        message_id: The ID of the message containing the media
        chat_jid: The JID of the chat containing the message
    
    Returns:
        A dictionary containing success status, a status message, and the file path if successful
    """
    file_path = whatsapp_download_media(message_id, chat_jid)
    
    if file_path:
        return {
            "success": True,
            "message": "Media downloaded successfully",
            "file_path": file_path
        }
    else:
        return {
            "success": False,
            "message": "Failed to download media"
        }

# Custom HTTP routes for health check and tools listing
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for monitoring."""
    return PlainTextResponse("OK")

@mcp.custom_route("/tools", methods=["GET"])
async def list_tools(request):
    """List all available MCP tools with their descriptions and parameters."""
    # For now, return a simple list of our WhatsApp tools
    tools = [
        {
            "name": "search_contacts",
            "description": "Search WhatsApp contacts by name or phone number.",
            "parameters": {
                "query": {"type": "string", "description": "Search term to match against contact names or phone numbers"}
            }
        },
        {
            "name": "list_messages", 
            "description": "Get WhatsApp messages matching specified criteria with optional context.",
            "parameters": {
                "after": {"type": "string", "description": "Optional ISO-8601 formatted string to only return messages after this date"},
                "before": {"type": "string", "description": "Optional ISO-8601 formatted string to only return messages before this date"},
                "sender_phone_number": {"type": "string", "description": "Optional phone number to filter messages by sender"},
                "chat_jid": {"type": "string", "description": "Optional chat JID to filter messages by chat"},
                "query": {"type": "string", "description": "Optional search term to filter messages by content"},
                "limit": {"type": "integer", "description": "Maximum number of messages to return (default 20)"},
                "page": {"type": "integer", "description": "Page number for pagination (default 0)"},
                "include_context": {"type": "boolean", "description": "Whether to include messages before and after matches (default True)"},
                "context_before": {"type": "integer", "description": "Number of messages to include before each match (default 1)"},
                "context_after": {"type": "integer", "description": "Number of messages to include after each match (default 1)"}
            }
        },
        {
            "name": "list_chats",
            "description": "Get WhatsApp chats matching specified criteria.",
            "parameters": {
                "query": {"type": "string", "description": "Optional search term to filter chats by name or JID"},
                "limit": {"type": "integer", "description": "Maximum number of chats to return (default 20)"},
                "page": {"type": "integer", "description": "Page number for pagination (default 0)"},
                "include_last_message": {"type": "boolean", "description": "Whether to include the last message in each chat (default True)"},
                "sort_by": {"type": "string", "description": "Field to sort results by, either 'last_active' or 'name' (default 'last_active')"}
            }
        },
        {
            "name": "get_chat",
            "description": "Get WhatsApp chat metadata by JID.",
            "parameters": {
                "chat_jid": {"type": "string", "description": "The JID of the chat to retrieve"},
                "include_last_message": {"type": "boolean", "description": "Whether to include the last message (default True)"}
            }
        },
        {
            "name": "get_direct_chat_by_contact",
            "description": "Get WhatsApp chat metadata by sender phone number.",
            "parameters": {
                "sender_phone_number": {"type": "string", "description": "The phone number to search for"}
            }
        },
        {
            "name": "get_contact_chats",
            "description": "Get all WhatsApp chats involving the contact.",
            "parameters": {
                "jid": {"type": "string", "description": "The contact's JID to search for"},
                "limit": {"type": "integer", "description": "Maximum number of chats to return (default 20)"},
                "page": {"type": "integer", "description": "Page number for pagination (default 0)"}
            }
        },
        {
            "name": "get_last_interaction",
            "description": "Get most recent WhatsApp message involving the contact.",
            "parameters": {
                "jid": {"type": "string", "description": "The JID of the contact to search for"}
            }
        },
        {
            "name": "get_message_context",
            "description": "Get context around a specific WhatsApp message.",
            "parameters": {
                "message_id": {"type": "string", "description": "The ID of the message to get context for"},
                "before": {"type": "integer", "description": "Number of messages to include before the target message (default 5)"},
                "after": {"type": "integer", "description": "Number of messages to include after the target message (default 5)"}
            }
        },
        {
            "name": "send_message",
            "description": "Send a WhatsApp message to a person or group.",
            "parameters": {
                "recipient": {"type": "string", "description": "The recipient - either a phone number with country code but no + or other symbols, or a JID"},
                "message": {"type": "string", "description": "The message text to send"}
            }
        },
        {
            "name": "send_file",
            "description": "Send a file such as a picture, raw audio, video or document via WhatsApp.",
            "parameters": {
                "recipient": {"type": "string", "description": "The recipient - either a phone number with country code but no + or other symbols, or a JID"},
                "media_path": {"type": "string", "description": "The absolute path to the media file to send (image, video, document)"}
            }
        },
        {
            "name": "send_audio_message",
            "description": "Send any audio file as a WhatsApp audio message.",
            "parameters": {
                "recipient": {"type": "string", "description": "The recipient - either a phone number with country code but no + or other symbols, or a JID"},
                "media_path": {"type": "string", "description": "The absolute path to the audio file to send (will be converted to Opus .ogg if it's not a .ogg file)"}
            }
        },
        {
            "name": "download_media",
            "description": "Download media from a WhatsApp message and get the local file path.",
            "parameters": {
                "message_id": {"type": "string", "description": "The ID of the message containing the media"},
                "chat_jid": {"type": "string", "description": "The JID of the chat containing the message"}
            }
        }
    ]
    
    return JSONResponse({"tools": tools})

@mcp.custom_route("/api/message-notification", methods=["POST"])
async def message_notification(request: Request):
    """Endpoint to receive message notifications from WhatsApp bridge."""
    try:
        # Parse the notification data
        notification_data = await request.json()
        
        logger.info(f"Received message notification: {notification_data.get('type', 'unknown')} from {notification_data.get('sender', 'unknown')}")
        
        # Notify all registered handlers
        await notify_message_handlers(notification_data)
        
        return JSONResponse({
            "success": True,
            "message": "Notification processed successfully"
        })
        
    except Exception as e:
        logger.error(f"Error processing message notification: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error processing notification: {str(e)}"
        }, status_code=500)

@mcp.custom_route("/", methods=["GET"])
async def root_info(request):
    """Root endpoint with API information."""
    return JSONResponse({
        "name": "WhatsApp MCP Server",
        "version": "1.0.0",
        "transport": "FastMCP SSE",
        "endpoints": {
            "mcp_sse": "/sse",
            "health": "/health",
            "tools": "/tools",
            "message_notification": "/api/message-notification"
        }
    })

if __name__ == "__main__":
    import os
    
    # Get configuration from environment variables
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "3000"))
    transport = os.getenv("MCP_TRANSPORT", "sse")  # Default to SSE for LlamaStack compatibility
    
    print(f"🚀 Starting WhatsApp MCP server...")
    print(f"   Transport: {transport}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    
    if transport == "sse":
        print(f"   SSE Endpoint: http://{host}:{port}/sse")
        print(f"   Custom HTTP Endpoints:")
        print(f"     - Root: http://{host}:{port}/")
        print(f"     - Health: http://{host}:{port}/health")
        print(f"     - Tools: http://{host}:{port}/tools")
        print(f"   This provides both MCP protocol over SSE and HTTP API endpoints")
    elif transport == "http":
        print(f"   HTTP Endpoints:")
        print(f"     - Root: http://{host}:{port}/")
        print(f"     - Health: http://{host}:{port}/health")
        print(f"     - Tools: http://{host}:{port}/tools")
        print(f"     - MCP: http://{host}:{port}/mcp")
        print(f"   This provides both MCP protocol and HTTP API endpoints")
    
    # Initialize and run the MCP server
    mcp.settings.host = host
    mcp.settings.port = port    
    mcp.run(transport=transport)