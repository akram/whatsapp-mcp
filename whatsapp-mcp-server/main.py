from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from starlette.responses import PlainTextResponse, JSONResponse
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

# Initialize FastMCP server
mcp = FastMCP("whatsapp")

@mcp.tool(
    name="search_contacts",
    description="Search WhatsApp contacts by name or phone number.",
    tags={"contacts", "search"},
    meta={"version": "1.0", "category": "contacts"}
)
def search_contacts(query: str) -> List[Dict[str, Any]]:
    """Search WhatsApp contacts by name or phone number.
    
    Args:
        query: Search term to match against contact names or phone numbers
    """
    contacts = whatsapp_search_contacts(query)
    return contacts

@mcp.tool(
    name="list_messages",
    description="Get WhatsApp messages matching specified criteria with optional context.",
    tags={"messages", "search", "context"},
    meta={"version": "1.0", "category": "messages"}
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
    context_before: int = 1,
    context_after: int = 1
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
    return messages

@mcp.tool(
    name="list_chats",
    description="Get WhatsApp chats matching specified criteria.",
    tags={"chats", "list"},
    meta={"version": "1.0", "category": "chats"}
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
    chats = whatsapp_list_chats(
        query=query,
        limit=limit,
        page=page,
        include_last_message=include_last_message,
        sort_by=sort_by
    )
    return chats

@mcp.tool(
    name="get_chat",
    description="Get WhatsApp chat metadata by JID.",
    tags={"chats", "metadata"},
    meta={"version": "1.0", "category": "chats"}
)
def get_chat(chat_jid: str, include_last_message: bool = True) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by JID.
    
    Args:
        chat_jid: The JID of the chat to retrieve
        include_last_message: Whether to include the last message (default True)
    """
    chat = whatsapp_get_chat(chat_jid, include_last_message)
    return chat

@mcp.tool(
    name="get_direct_chat_by_contact",
    description="Get WhatsApp chat metadata by sender phone number.",
    tags={"chats", "contacts"},
    meta={"version": "1.0", "category": "chats"}
)
def get_direct_chat_by_contact(sender_phone_number: str) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by sender phone number.
    
    Args:
        sender_phone_number: The phone number to search for
    """
    chat = whatsapp_get_direct_chat_by_contact(sender_phone_number)
    return chat

@mcp.tool(
    name="get_contact_chats",
    description="Get all WhatsApp chats involving the contact.",
    tags={"chats", "contacts"},
    meta={"version": "1.0", "category": "chats"}
)
def get_contact_chats(jid: str, limit: int = 20, page: int = 0) -> List[Dict[str, Any]]:
    """Get all WhatsApp chats involving the contact.
    
    Args:
        jid: The contact's JID to search for
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
    """
    chats = whatsapp_get_contact_chats(jid, limit, page)
    return chats

@mcp.tool(
    name="get_last_interaction",
    description="Get most recent WhatsApp message involving the contact.",
    tags={"messages", "contacts"},
    meta={"version": "1.0", "category": "messages"}
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
    tags={"messages", "context"},
    meta={"version": "1.0", "category": "messages"}
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
    return context

@mcp.tool(
    name="send_message",
    description="Send a WhatsApp message to a person or group.",
    tags={"messages", "send"},
    meta={"version": "1.0", "category": "messaging"}
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
    tags={"files", "send", "media"},
    meta={"version": "1.0", "category": "messaging"}
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
    tags={"audio", "send", "media"},
    meta={"version": "1.0", "category": "messaging"}
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
    tags={"media", "download"},
    meta={"version": "1.0", "category": "media"}
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
    tools = []
    for tool_name, tool_func in mcp.tools.items():
        tool_info = {
            "name": tool_name,
            "description": tool_func.__doc__ or "No description available"
        }
        
        # Try to get parameter information from function signature
        import inspect
        sig = inspect.signature(tool_func)
        if sig.parameters:
            tool_info["parameters"] = {}
            for param_name, param in sig.parameters.items():
                param_info = {
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "string",
                    "description": f"Parameter: {param_name}"
                }
                if param.default != inspect.Parameter.empty:
                    param_info["default"] = param.default
                tool_info["parameters"][param_name] = param_info
        
        tools.append(tool_info)
    
    return JSONResponse({"tools": tools})

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
            "tools": "/tools"
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
    mcp.run(transport=transport, host=host, port=port)