"""
Generic Telegram client wrapper for sending messages and interacting with Telegram Bot API
"""

import os
import logging
from typing import Optional, List, Dict, Any, Union
from aiogram import Bot, types
from aiogram.enums import ParseMode
from aiogram.types import Message, Update, User, Chat, File
import asyncio
from dotenv import load_dotenv

load_dotenv()


class TelegramClient:
    """Generic Telegram client for bot operations"""
    
    def __init__(self, bot_token: Optional[str] = None, default_chat_id: Optional[str] = None):
        # Initialize logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)

        # Load credentials
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.default_chat_id = default_chat_id or os.getenv("TELEGRAM_CHAT_ID")

        # Validate bot token
        if not self.bot_token:
            self.logger.error("Telegram bot token is not provided.")
            raise ValueError("Missing Telegram bot token.")

        # Initialize the bot
        self.bot = Bot(token=self.bot_token)
        self.logger.info("TelegramClient initialized successfully.")

    async def send_message(
        self, 
        text: str, 
        chat_id: Optional[Union[str, int]] = None,
        parse_mode: Optional[str] = "Markdown",
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Any] = None
    ) -> Message:
        """
        Send a text message to a Telegram chat
        
        Args:
            text: The message text to send
            chat_id: Target chat ID (uses default if not provided)
            parse_mode: Message parse mode (Markdown, HTML, or None)
            disable_notification: Send message silently
            reply_to_message_id: ID of message to reply to
            reply_markup: Additional interface options (keyboard, buttons, etc)
            
        Returns:
            Message object from Telegram
        """
        target_chat_id = chat_id or self.default_chat_id
        if not target_chat_id:
            raise ValueError("No chat_id provided and no default chat_id set")
        
        self.logger.debug(f"Sending message to chat {target_chat_id}: {text[:50]}...")
        
        try:
            # Convert parse_mode string to enum
            parse_mode_enum = None
            if parse_mode:
                if parse_mode.upper() == "MARKDOWN":
                    parse_mode_enum = ParseMode.MARKDOWN
                elif parse_mode.upper() == "HTML":
                    parse_mode_enum = ParseMode.HTML
            
            message = await self.bot.send_message(
                chat_id=target_chat_id,
                text=text,
                parse_mode=parse_mode_enum,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup
            )
            self.logger.info(f"Message sent successfully. Message ID: {message.message_id}")
            return message
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            raise

    async def send_photo(
        self,
        photo: Union[str, bytes],
        chat_id: Optional[Union[str, int]] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = "Markdown",
        disable_notification: bool = False
    ) -> Message:
        """Send a photo to a Telegram chat"""
        target_chat_id = chat_id or self.default_chat_id
        if not target_chat_id:
            raise ValueError("No chat_id provided and no default chat_id set")
        
        try:
            # Convert parse_mode string to enum
            parse_mode_enum = None
            if parse_mode and caption:
                if parse_mode.upper() == "MARKDOWN":
                    parse_mode_enum = ParseMode.MARKDOWN
                elif parse_mode.upper() == "HTML":
                    parse_mode_enum = ParseMode.HTML
            
            message = await self.bot.send_photo(
                chat_id=target_chat_id,
                photo=photo,
                caption=caption,
                parse_mode=parse_mode_enum,
                disable_notification=disable_notification
            )
            self.logger.info(f"Photo sent successfully. Message ID: {message.message_id}")
            return message
            
        except Exception as e:
            self.logger.error(f"Failed to send photo: {e}")
            raise

    async def send_document(
        self,
        document: Union[str, bytes],
        chat_id: Optional[Union[str, int]] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = "Markdown",
        disable_notification: bool = False
    ) -> Message:
        """Send a document to a Telegram chat"""
        target_chat_id = chat_id or self.default_chat_id
        if not target_chat_id:
            raise ValueError("No chat_id provided and no default chat_id set")
        
        try:
            # Convert parse_mode string to enum
            parse_mode_enum = None
            if parse_mode and caption:
                if parse_mode.upper() == "MARKDOWN":
                    parse_mode_enum = ParseMode.MARKDOWN
                elif parse_mode.upper() == "HTML":
                    parse_mode_enum = ParseMode.HTML
            
            message = await self.bot.send_document(
                chat_id=target_chat_id,
                document=document,
                caption=caption,
                parse_mode=parse_mode_enum,
                disable_notification=disable_notification
            )
            self.logger.info(f"Document sent successfully. Message ID: {message.message_id}")
            return message
            
        except Exception as e:
            self.logger.error(f"Failed to send document: {e}")
            raise

    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: int = 10,
        timeout: int = 0,
        allowed_updates: Optional[List[str]] = None
    ) -> List[Update]:
        """
        Get updates from Telegram (messages, callbacks, etc)
        
        Args:
            offset: Identifier of the first update to be returned
            limit: Limits the number of updates to be retrieved (1-100)
            timeout: Timeout in seconds for long polling
            allowed_updates: List of update types to receive
            
        Returns:
            List of Update objects
        """
        try:
            updates = await self.bot.get_updates(
                offset=offset,
                limit=limit,
                timeout=timeout,
                allowed_updates=allowed_updates
            )
            self.logger.info(f"Retrieved {len(updates)} updates")
            return updates
            
        except Exception as e:
            self.logger.error(f"Failed to get updates: {e}")
            raise

    async def get_me(self) -> User:
        """Get information about the bot"""
        try:
            bot_info = await self.bot.get_me()
            self.logger.info(f"Bot info retrieved: @{bot_info.username}")
            return bot_info
            
        except Exception as e:
            self.logger.error(f"Failed to get bot info: {e}")
            raise

    async def get_chat(self, chat_id: Union[str, int]) -> Chat:
        """Get information about a chat"""
        try:
            chat_info = await self.bot.get_chat(chat_id)
            self.logger.info(f"Chat info retrieved for {chat_id}")
            return chat_info
            
        except Exception as e:
            self.logger.error(f"Failed to get chat info: {e}")
            raise

    async def get_chat_member_count(self, chat_id: Union[str, int]) -> int:
        """Get the number of members in a chat"""
        try:
            count = await self.bot.get_chat_member_count(chat_id)
            self.logger.info(f"Chat {chat_id} has {count} members")
            return count
            
        except Exception as e:
            self.logger.error(f"Failed to get chat member count: {e}")
            raise

    async def set_webhook(
        self,
        url: str,
        certificate: Optional[str] = None,
        ip_address: Optional[str] = None,
        max_connections: Optional[int] = None,
        allowed_updates: Optional[List[str]] = None
    ) -> bool:
        """Set webhook for the bot"""
        try:
            result = await self.bot.set_webhook(
                url=url,
                certificate=certificate,
                ip_address=ip_address,
                max_connections=max_connections,
                allowed_updates=allowed_updates
            )
            self.logger.info(f"Webhook set to {url}: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to set webhook: {e}")
            raise

    async def delete_webhook(self) -> bool:
        """Delete webhook"""
        try:
            result = await self.bot.delete_webhook()
            self.logger.info(f"Webhook deleted: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to delete webhook: {e}")
            raise

    async def get_webhook_info(self) -> Dict[str, Any]:
        """Get current webhook info"""
        try:
            info = await self.bot.get_webhook_info()
            return {
                "url": info.url,
                "has_custom_certificate": info.has_custom_certificate,
                "pending_update_count": info.pending_update_count,
                "ip_address": info.ip_address,
                "last_error_date": info.last_error_date,
                "last_error_message": info.last_error_message,
                "max_connections": info.max_connections,
                "allowed_updates": info.allowed_updates
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get webhook info: {e}")
            raise

    async def close(self) -> None:
        """Close the bot session"""
        await self.bot.session.close()
        self.logger.info("Bot session closed")


# Example usage
if __name__ == "__main__":
    async def main():
        client = TelegramClient()
        
        # Send a simple message
        await client.send_message("Hello from the generic Telegram client!")
        
        # Get bot info
        bot_info = await client.get_me()
        print(f"Bot username: @{bot_info.username}")
        
        # Get recent updates
        updates = await client.get_updates(limit=5)
        print(f"Got {len(updates)} updates")
        
        await client.close()

    asyncio.run(main())