#!/usr/bin/env python3
"""
Telegram MCP (Model Context Protocol) Server
Provides tools for Claude to interact with Telegram via the telegram-service
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server import Server
from mcp.types import (
    Tool, 
    TextContent,
    ImageContent,
    EmbeddedResource,
    BlobResourceContents,
    TextResourceContents
)
import mcp.server.stdio

# Add the src directory to the path so we can import telegram_service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from telegram_service import TelegramClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramMCPServer:
    """MCP Server for Telegram integration"""
    
    def __init__(self):
        self.server = Server("telegram-service")
        self.client: Optional[TelegramClient] = None
        self.last_update_id: Optional[int] = None
        self._setup_tools()
        self._setup_resources()
    
    async def initialize(self):
        """Initialize the Telegram client"""
        try:
            self.client = TelegramClient()
            logger.info("Telegram client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram client: {e}")
            raise
    
    def _setup_tools(self):
        """Register all available tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="telegram_send_message",
                    description="Send a message to a Telegram chat",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The message text to send (supports Markdown)"
                            },
                            "chat_id": {
                                "type": "string",
                                "description": "Target chat ID (uses default if not provided)"
                            },
                            "parse_mode": {
                                "type": "string",
                                "description": "Parse mode for the message",
                                "enum": ["Markdown", "HTML", "None"],
                                "default": "Markdown"
                            },
                            "disable_notification": {
                                "type": "boolean",
                                "description": "Send message silently",
                                "default": False
                            }
                        },
                        "required": ["text"]
                    }
                ),
                Tool(
                    name="telegram_send_photo",
                    description="Send a photo to a Telegram chat",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "photo_url": {
                                "type": "string",
                                "description": "URL or file path of the photo to send"
                            },
                            "caption": {
                                "type": "string",
                                "description": "Optional caption for the photo"
                            },
                            "chat_id": {
                                "type": "string",
                                "description": "Target chat ID (uses default if not provided)"
                            },
                            "parse_mode": {
                                "type": "string",
                                "description": "Parse mode for the caption",
                                "enum": ["Markdown", "HTML", "None"],
                                "default": "Markdown"
                            }
                        },
                        "required": ["photo_url"]
                    }
                ),
                Tool(
                    name="telegram_send_document",
                    description="Send a document/file to a Telegram chat",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_url": {
                                "type": "string",
                                "description": "URL or file path of the document to send"
                            },
                            "caption": {
                                "type": "string",
                                "description": "Optional caption for the document"
                            },
                            "chat_id": {
                                "type": "string",
                                "description": "Target chat ID (uses default if not provided)"
                            }
                        },
                        "required": ["document_url"]
                    }
                ),
                Tool(
                    name="telegram_get_updates",
                    description="Get recent updates/messages from the Telegram bot",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of updates to retrieve",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds for long polling",
                                "default": 0
                            }
                        }
                    }
                ),
                Tool(
                    name="telegram_get_bot_info",
                    description="Get information about the Telegram bot",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="telegram_get_chat_info",
                    description="Get information about a specific chat",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "chat_id": {
                                "type": "string",
                                "description": "The chat ID to get information about"
                            }
                        },
                        "required": ["chat_id"]
                    }
                ),
                Tool(
                    name="telegram_set_webhook",
                    description="Set webhook URL for the bot",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "HTTPS URL to send updates to"
                            },
                            "allowed_updates": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of update types to receive"
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="telegram_delete_webhook",
                    description="Remove webhook and switch back to getUpdates",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="telegram_get_webhook_info",
                    description="Get current webhook status and configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if not self.client:
                    await self.initialize()
                
                if name == "telegram_send_message":
                    return await self._send_message(arguments)
                elif name == "telegram_send_photo":
                    return await self._send_photo(arguments)
                elif name == "telegram_send_document":
                    return await self._send_document(arguments)
                elif name == "telegram_get_updates":
                    return await self._get_updates(arguments)
                elif name == "telegram_get_bot_info":
                    return await self._get_bot_info(arguments)
                elif name == "telegram_get_chat_info":
                    return await self._get_chat_info(arguments)
                elif name == "telegram_set_webhook":
                    return await self._set_webhook(arguments)
                elif name == "telegram_delete_webhook":
                    return await self._delete_webhook(arguments)
                elif name == "telegram_get_webhook_info":
                    return await self._get_webhook_info(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    def _setup_resources(self):
        """Register available resources"""
        
        @self.server.list_resources()
        async def list_resources() -> List[EmbeddedResource]:
            resources = []
            
            # Configuration status
            config_status = {
                "bot_token_configured": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
                "default_chat_id_configured": bool(os.getenv("TELEGRAM_CHAT_ID")),
                "environment": os.getenv("ENVIRONMENT", "production")
            }
            
            resources.append(
                EmbeddedResource(
                    type="resource",
                    resource=TextResourceContents(
                        type="text",
                        text=json.dumps(config_status, indent=2)
                    ),
                    uri="telegram://config/status",
                    name="Telegram Configuration Status",
                    description="Current configuration status of the Telegram bot",
                    mimeType="application/json"
                )
            )
            
            # Bot info if available
            if self.client:
                try:
                    bot_info = await self.client.get_me()
                    resources.append(
                        EmbeddedResource(
                            type="resource",
                            resource=TextResourceContents(
                                type="text",
                                text=json.dumps({
                                    "id": bot_info.id,
                                    "username": bot_info.username,
                                    "first_name": bot_info.first_name,
                                    "is_bot": bot_info.is_bot
                                }, indent=2)
                            ),
                            uri="telegram://bot/info",
                            name="Bot Information",
                            description="Current bot information",
                            mimeType="application/json"
                        )
                    )
                except:
                    pass
            
            return resources
    
    async def _send_message(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Send a message to Telegram"""
        text = arguments.get("text")
        chat_id = arguments.get("chat_id")
        parse_mode = arguments.get("parse_mode", "Markdown")
        disable_notification = arguments.get("disable_notification", False)
        
        try:
            message = await self.client.send_message(
                text=text,
                chat_id=chat_id,
                parse_mode=parse_mode,
                disable_notification=disable_notification
            )
            
            result = {
                "success": True,
                "message_id": message.message_id,
                "chat_id": message.chat.id,
                "date": message.date.isoformat() if message.date else None
            }
            
            logger.info(f"Message sent successfully: {result}")
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            error_msg = f"Failed to send message: {str(e)}"
            logger.error(error_msg)
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": str(e)}, indent=2)
            )]
    
    async def _send_photo(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Send a photo to Telegram"""
        photo_url = arguments.get("photo_url")
        caption = arguments.get("caption")
        chat_id = arguments.get("chat_id")
        parse_mode = arguments.get("parse_mode", "Markdown")
        
        try:
            message = await self.client.send_photo(
                photo=photo_url,
                caption=caption,
                chat_id=chat_id,
                parse_mode=parse_mode
            )
            
            result = {
                "success": True,
                "message_id": message.message_id,
                "chat_id": message.chat.id,
                "has_caption": bool(caption)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": str(e)}, indent=2)
            )]
    
    async def _send_document(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Send a document to Telegram"""
        document_url = arguments.get("document_url")
        caption = arguments.get("caption")
        chat_id = arguments.get("chat_id")
        
        try:
            message = await self.client.send_document(
                document=document_url,
                caption=caption,
                chat_id=chat_id
            )
            
            result = {
                "success": True,
                "message_id": message.message_id,
                "chat_id": message.chat.id,
                "has_caption": bool(caption)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": str(e)}, indent=2)
            )]
    
    async def _get_updates(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get recent updates from Telegram"""
        limit = arguments.get("limit", 10)
        timeout = arguments.get("timeout", 0)
        
        try:
            updates = await self.client.get_updates(
                offset=self.last_update_id + 1 if self.last_update_id else None,
                limit=limit,
                timeout=timeout
            )
            
            if not updates:
                return [TextContent(
                    type="text",
                    text=json.dumps({"updates": [], "count": 0}, indent=2)
                )]
            
            # Update the last update ID
            if updates:
                self.last_update_id = updates[-1].update_id
            
            # Format updates for display
            formatted_updates = []
            for update in updates:
                update_info = {
                    "update_id": update.update_id,
                    "type": update.update_type
                }
                
                if update.message:
                    update_info["message"] = {
                        "id": update.message.message_id,
                        "date": update.message.date.isoformat() if update.message.date else None,
                        "text": update.message.text,
                        "from": {
                            "id": update.message.from_user.id if update.message.from_user else None,
                            "username": update.message.from_user.username if update.message.from_user else None,
                            "first_name": update.message.from_user.first_name if update.message.from_user else None,
                        },
                        "chat": {
                            "id": update.message.chat.id,
                            "type": update.message.chat.type,
                            "title": getattr(update.message.chat, 'title', None)
                        }
                    }
                
                formatted_updates.append(update_info)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "updates": formatted_updates,
                    "count": len(formatted_updates)
                }, indent=2, default=str)
            )]
            
        except Exception as e:
            error_msg = f"Failed to get updates: {str(e)}"
            logger.error(error_msg)
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": str(e)}, indent=2)
            )]
    
    async def _get_bot_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get information about the bot"""
        try:
            bot_info = await self.client.get_me()
            
            info = {
                "id": bot_info.id,
                "is_bot": bot_info.is_bot,
                "first_name": bot_info.first_name,
                "username": bot_info.username,
                "can_join_groups": bot_info.can_join_groups,
                "can_read_all_group_messages": bot_info.can_read_all_group_messages,
                "supports_inline_queries": bot_info.supports_inline_queries,
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(info, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": str(e)}, indent=2)
            )]
    
    async def _get_chat_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get information about a chat"""
        chat_id = arguments.get("chat_id")
        
        try:
            chat_info = await self.client.get_chat(chat_id)
            
            info = {
                "id": chat_info.id,
                "type": chat_info.type,
                "title": getattr(chat_info, 'title', None),
                "username": getattr(chat_info, 'username', None),
                "first_name": getattr(chat_info, 'first_name', None),
                "last_name": getattr(chat_info, 'last_name', None),
                "description": getattr(chat_info, 'description', None),
            }
            
            # Try to get member count for groups/channels
            try:
                member_count = await self.client.get_chat_member_count(chat_id)
                info["member_count"] = member_count
            except:
                pass
            
            return [TextContent(
                type="text",
                text=json.dumps(info, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": str(e)}, indent=2)
            )]
    
    async def _set_webhook(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Set webhook for the bot"""
        url = arguments.get("url")
        allowed_updates = arguments.get("allowed_updates")
        
        try:
            result = await self.client.set_webhook(
                url=url,
                allowed_updates=allowed_updates
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result,
                    "webhook_url": url,
                    "message": "Webhook set successfully" if result else "Failed to set webhook"
                }, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": str(e)}, indent=2)
            )]
    
    async def _delete_webhook(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Delete webhook"""
        try:
            result = await self.client.delete_webhook()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": result,
                    "message": "Webhook deleted successfully" if result else "Failed to delete webhook"
                }, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": str(e)}, indent=2)
            )]
    
    async def _get_webhook_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get webhook info"""
        try:
            info = await self.client.get_webhook_info()
            
            return [TextContent(
                type="text",
                text=json.dumps(info, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": str(e)}, indent=2)
            )]
    
    async def run(self):
        """Run the MCP server"""
        try:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                logger.info("Starting Telegram MCP server...")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            if self.client:
                await self.client.close()


async def main():
    """Main entry point"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        sys.exit(1)
    
    # Create and run server
    server = TelegramMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())