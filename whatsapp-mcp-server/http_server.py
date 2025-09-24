import asyncio
import json
import logging
import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sse_starlette import EventSourceResponse
import uvicorn
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

# Create FastAPI app
app = FastAPI(title="WhatsApp MCP HTTP Server", version="1.0.0")

# Store for SSE connections
sse_connections: List[asyncio.Queue] = []

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "WhatsApp MCP HTTP Server",
        "version": "1.0.0",
        "endpoints": {
            "sse": "/sse/events",
            "api": "/api/",
            "health": "/health",
            "tools": "/tools"
        }
    }

@app.get("/tools")
async def list_tools():
    """List all available MCP tools with their descriptions and parameters."""
    tools = [
        {
            "name": "search_contacts",
            "description": "Search WhatsApp contacts by name or phone number",
            "parameters": {
                "query": {"type": "string", "description": "Search term to match against contact names or phone numbers"}
            }
        },
        {
            "name": "list_messages",
            "description": "Get WhatsApp messages matching specified criteria with optional context",
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
            "description": "Get WhatsApp chats matching specified criteria",
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
            "description": "Get WhatsApp chat metadata by JID",
            "parameters": {
                "chat_jid": {"type": "string", "description": "The JID of the chat to retrieve"},
                "include_last_message": {"type": "boolean", "description": "Whether to include the last message (default True)"}
            }
        },
        {
            "name": "get_direct_chat_by_contact",
            "description": "Get WhatsApp chat metadata by sender phone number",
            "parameters": {
                "sender_phone_number": {"type": "string", "description": "The phone number to search for"}
            }
        },
        {
            "name": "get_contact_chats",
            "description": "Get all WhatsApp chats involving the contact",
            "parameters": {
                "jid": {"type": "string", "description": "The contact's JID to search for"},
                "limit": {"type": "integer", "description": "Maximum number of chats to return (default 20)"},
                "page": {"type": "integer", "description": "Page number for pagination (default 0)"}
            }
        },
        {
            "name": "get_last_interaction",
            "description": "Get most recent WhatsApp message involving the contact",
            "parameters": {
                "jid": {"type": "string", "description": "The JID of the contact to search for"}
            }
        },
        {
            "name": "get_message_context",
            "description": "Get context around a specific WhatsApp message",
            "parameters": {
                "message_id": {"type": "string", "description": "The ID of the message to get context for"},
                "before": {"type": "integer", "description": "Number of messages to include before the target message (default 5)"},
                "after": {"type": "integer", "description": "Number of messages to include after the target message (default 5)"}
            }
        },
        {
            "name": "send_message",
            "description": "Send a WhatsApp message to a person or group. For group chats use the JID",
            "parameters": {
                "recipient": {"type": "string", "description": "The recipient - either a phone number with country code but no + or other symbols, or a JID (e.g., '123456789@s.whatsapp.net' or a group JID like '123456789@g.us')"},
                "message": {"type": "string", "description": "The message text to send"}
            }
        },
        {
            "name": "send_file",
            "description": "Send a file such as a picture, raw audio, video or document via WhatsApp to the specified recipient. For group messages use the JID",
            "parameters": {
                "recipient": {"type": "string", "description": "The recipient - either a phone number with country code but no + or other symbols, or a JID (e.g., '123456789@s.whatsapp.net' or a group JID like '123456789@g.us')"},
                "media_path": {"type": "string", "description": "The absolute path to the media file to send (image, video, document)"}
            }
        },
        {
            "name": "send_audio_message",
            "description": "Send any audio file as a WhatsApp audio message to the specified recipient. For group messages use the JID. If it errors due to ffmpeg not being installed, use send_file instead",
            "parameters": {
                "recipient": {"type": "string", "description": "The recipient - either a phone number with country code but no + or other symbols, or a JID (e.g., '123456789@s.whatsapp.net' or a group JID like '123456789@g.us')"},
                "media_path": {"type": "string", "description": "The absolute path to the audio file to send (will be converted to Opus .ogg if it's not a .ogg file)"}
            }
        },
        {
            "name": "download_media",
            "description": "Download media from a WhatsApp message and get the local file path",
            "parameters": {
                "message_id": {"type": "string", "description": "The ID of the message containing the media"},
                "chat_jid": {"type": "string", "description": "The JID of the chat containing the message"}
            }
        }
    ]
    
    await broadcast_event("tools_listed", {"count": len(tools)})
    return {"success": True, "tools": tools}

@app.post("/tools/{tool_name}/execute")
async def execute_tool(tool_name: str, parameters: dict):
    """Execute a specific MCP tool with the provided parameters."""
    try:
        # Map tool names to their corresponding functions
        tool_functions = {
            "search_contacts": whatsapp_search_contacts,
            "list_messages": whatsapp_list_messages,
            "list_chats": whatsapp_list_chats,
            "get_chat": whatsapp_get_chat,
            "get_direct_chat_by_contact": whatsapp_get_direct_chat_by_contact,
            "get_contact_chats": whatsapp_get_contact_chats,
            "get_last_interaction": whatsapp_get_last_interaction,
            "get_message_context": whatsapp_get_message_context,
            "send_message": whatsapp_send_message,
            "send_file": whatsapp_send_file,
            "send_audio_message": whatsapp_audio_voice_message,
            "download_media": whatsapp_download_media
        }
        
        if tool_name not in tool_functions:
            await broadcast_event("tool_error", {
                "tool_name": tool_name,
                "error": f"Tool '{tool_name}' not found"
            })
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        # Execute the tool
        tool_func = tool_functions[tool_name]
        result = tool_func(**parameters)
        
        # Broadcast the result
        await broadcast_event("tool_executed", {
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result
        })
        
        return {"success": True, "tool_name": tool_name, "result": result}
        
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        await broadcast_event("tool_error", {
            "tool_name": tool_name,
            "parameters": parameters,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "whatsapp-mcp-http"}

@app.get("/sse/events")
async def sse_events():
    """Server-Sent Events endpoint for real-time WhatsApp events."""
    async def event_generator():
        # Create a queue for this connection
        queue = asyncio.Queue()
        sse_connections.append(queue)
        
        try:
            # Send initial connection event
            yield {
                "event": "connected",
                "data": json.dumps({
                    "message": "Connected to WhatsApp MCP SSE",
                    "timestamp": asyncio.get_event_loop().time()
                })
            }
            
            # Keep connection alive and send events
            while True:
                try:
                    # Wait for events with timeout
                    event_data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield event_data
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield {
                        "event": "keepalive",
                        "data": json.dumps({
                            "timestamp": asyncio.get_event_loop().time()
                        })
                    }
        except Exception as e:
            logger.error(f"SSE connection error: {e}")
        finally:
            # Remove connection from list
            if queue in sse_connections:
                sse_connections.remove(queue)
    
    return EventSourceResponse(event_generator())

async def broadcast_event(event_type: str, data: Dict[str, Any]):
    """Broadcast an event to all SSE connections."""
    event_data = {
        "event": event_type,
        "data": json.dumps(data)
    }
    
    # Send to all connected clients
    for queue in sse_connections.copy():
        try:
            await queue.put(event_data)
        except Exception as e:
            logger.error(f"Error broadcasting to SSE client: {e}")
            # Remove failed connection
            if queue in sse_connections:
                sse_connections.remove(queue)

# API Endpoints (mirroring MCP tools)
@app.get("/api/contacts/search")
async def search_contacts_api(query: str):
    """Search WhatsApp contacts by name or phone number."""
    try:
        contacts = whatsapp_search_contacts(query)
        await broadcast_event("contacts_searched", {"query": query, "count": len(contacts)})
        return {"success": True, "contacts": contacts}
    except Exception as e:
        logger.error(f"Error searching contacts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages")
async def list_messages_api(
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
):
    """Get WhatsApp messages matching specified criteria."""
    try:
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
        await broadcast_event("messages_listed", {"count": len(messages), "filters": {
            "after": after, "before": before, "sender": sender_phone_number,
            "chat_jid": chat_jid, "query": query
        }})
        return {"success": True, "messages": messages}
    except Exception as e:
        logger.error(f"Error listing messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chats")
async def list_chats_api(
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_last_message: bool = True,
    sort_by: str = "last_active"
):
    """Get WhatsApp chats matching specified criteria."""
    try:
        chats = whatsapp_list_chats(
            query=query,
            limit=limit,
            page=page,
            include_last_message=include_last_message,
            sort_by=sort_by
        )
        await broadcast_event("chats_listed", {"count": len(chats), "filters": {
            "query": query, "sort_by": sort_by
        }})
        return {"success": True, "chats": chats}
    except Exception as e:
        logger.error(f"Error listing chats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chats/{chat_jid}")
async def get_chat_api(chat_jid: str, include_last_message: bool = True):
    """Get WhatsApp chat metadata by JID."""
    try:
        chat = whatsapp_get_chat(chat_jid, include_last_message)
        await broadcast_event("chat_retrieved", {"chat_jid": chat_jid})
        return {"success": True, "chat": chat}
    except Exception as e:
        logger.error(f"Error getting chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts/{sender_phone_number}/chat")
async def get_direct_chat_by_contact_api(sender_phone_number: str):
    """Get WhatsApp chat metadata by sender phone number."""
    try:
        chat = whatsapp_get_direct_chat_by_contact(sender_phone_number)
        await broadcast_event("direct_chat_retrieved", {"sender": sender_phone_number})
        return {"success": True, "chat": chat}
    except Exception as e:
        logger.error(f"Error getting direct chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts/{jid}/chats")
async def get_contact_chats_api(jid: str, limit: int = 20, page: int = 0):
    """Get all WhatsApp chats involving the contact."""
    try:
        chats = whatsapp_get_contact_chats(jid, limit, page)
        await broadcast_event("contact_chats_retrieved", {"jid": jid, "count": len(chats)})
        return {"success": True, "chats": chats}
    except Exception as e:
        logger.error(f"Error getting contact chats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts/{jid}/last-interaction")
async def get_last_interaction_api(jid: str):
    """Get most recent WhatsApp message involving the contact."""
    try:
        message = whatsapp_get_last_interaction(jid)
        await broadcast_event("last_interaction_retrieved", {"jid": jid})
        return {"success": True, "message": message}
    except Exception as e:
        logger.error(f"Error getting last interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages/{message_id}/context")
async def get_message_context_api(message_id: str, before: int = 5, after: int = 5):
    """Get context around a specific WhatsApp message."""
    try:
        context = whatsapp_get_message_context(message_id, before, after)
        await broadcast_event("message_context_retrieved", {"message_id": message_id})
        return {"success": True, "context": context}
    except Exception as e:
        logger.error(f"Error getting message context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/messages/send")
async def send_message_api(recipient: str, message: str):
    """Send a WhatsApp message to a person or group."""
    try:
        success, status_message = whatsapp_send_message(recipient, message)
        await broadcast_event("message_sent", {
            "recipient": recipient,
            "success": success,
            "message": status_message
        })
        return {"success": success, "message": status_message}
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/send")
async def send_file_api(recipient: str, media_path: str):
    """Send a file via WhatsApp."""
    try:
        success, status_message = whatsapp_send_file(recipient, media_path)
        await broadcast_event("file_sent", {
            "recipient": recipient,
            "media_path": media_path,
            "success": success,
            "message": status_message
        })
        return {"success": success, "message": status_message}
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audio/send")
async def send_audio_message_api(recipient: str, media_path: str):
    """Send an audio message via WhatsApp."""
    try:
        success, status_message = whatsapp_audio_voice_message(recipient, media_path)
        await broadcast_event("audio_sent", {
            "recipient": recipient,
            "media_path": media_path,
            "success": success,
            "message": status_message
        })
        return {"success": success, "message": status_message}
    except Exception as e:
        logger.error(f"Error sending audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audio/upload")
async def upload_and_send_audio(
    recipient: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload an audio file and send it as a WhatsApp audio message."""
    temp_file_path = None
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Create temporary file with proper extension
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'tmp'
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            temp_file_path = temp_file.name
            
            # Copy uploaded file to temporary location
            shutil.copyfileobj(file.file, temp_file)
            temp_file.flush()  # Ensure data is written to disk
        
        # Verify the file exists and has content
        if not os.path.exists(temp_file_path):
            raise HTTPException(status_code=500, detail="Temporary file was not created")
        
        file_size = os.path.getsize(temp_file_path)
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        logger.info(f"Created temporary file: {temp_file_path} (size: {file_size} bytes)")
        
        # Send the audio message
        success, status_message = whatsapp_audio_voice_message(recipient, temp_file_path)
        
        await broadcast_event("audio_uploaded_and_sent", {
            "recipient": recipient,
            "filename": file.filename,
            "content_type": file.content_type,
            "success": success,
            "message": status_message
        })
        
        return {
            "success": success, 
            "message": status_message,
            "filename": file.filename,
            "content_type": file.content_type
        }
        
    except Exception as e:
        logger.error(f"Error uploading and sending audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Note: We don't clean up the temporary file here because it might be used by the WhatsApp bridge
        # The WhatsApp bridge or the audio conversion function should handle cleanup
        # TODO: Implement proper cleanup mechanism
        pass

@app.post("/api/files/upload")
async def upload_and_send_file(
    recipient: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload a file and send it via WhatsApp."""
    temp_file_path = None
    try:
        # Create temporary file with proper extension
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'tmp'
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            temp_file_path = temp_file.name
            
            # Copy uploaded file to temporary location
            shutil.copyfileobj(file.file, temp_file)
            temp_file.flush()  # Ensure data is written to disk
        
        # Verify the file exists and has content
        if not os.path.exists(temp_file_path):
            raise HTTPException(status_code=500, detail="Temporary file was not created")
        
        file_size = os.path.getsize(temp_file_path)
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        logger.info(f"Created temporary file: {temp_file_path} (size: {file_size} bytes)")
        
        # Send the file
        success, status_message = whatsapp_send_file(recipient, temp_file_path)
        
        await broadcast_event("file_uploaded_and_sent", {
            "recipient": recipient,
            "filename": file.filename,
            "content_type": file.content_type,
            "success": success,
            "message": status_message
        })
        
        return {
            "success": success, 
            "message": status_message,
            "filename": file.filename,
            "content_type": file.content_type
        }
        
    except Exception as e:
        logger.error(f"Error uploading and sending file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_file_path}: {e}")

@app.post("/api/media/download")
async def download_media_api(message_id: str, chat_jid: str):
    """Download media from a WhatsApp message."""
    try:
        file_path = whatsapp_download_media(message_id, chat_jid)
        if file_path:
            await broadcast_event("media_downloaded", {
                "message_id": message_id,
                "chat_jid": chat_jid,
                "file_path": file_path
            })
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
    except Exception as e:
        logger.error(f"Error downloading media: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def run_http_server(host: str = "0.0.0.0", port: int = 3000):
    """Run the HTTP server with SSE support."""
    logger.info(f"Starting WhatsApp MCP HTTP server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    run_http_server()
