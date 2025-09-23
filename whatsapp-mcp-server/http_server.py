import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
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
            "health": "/health"
        }
    }

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
