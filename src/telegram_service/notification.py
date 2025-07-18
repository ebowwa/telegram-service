"""
TelegramNotifier - Example application using TelegramClient
This is an example of how to build specific notification services on top of the generic TelegramClient
"""

import os
import logging
from typing import Optional, Dict, Any
from .telegram_client import TelegramClient
import asyncio
from dotenv import load_dotenv

load_dotenv()


class TelegramNotifier:
    """
    Example notification service built on top of TelegramClient
    This shows how to create specialized notification apps
    """
    
    def __init__(self):
        # Initialize the generic Telegram client
        self.client = TelegramClient()
        self.logger = self.client.logger
        
    async def send_message(self, message: str, **kwargs) -> bool:
        """Send a message using the underlying client"""
        try:
            await self.client.send_message(message, **kwargs)
            return True
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            return False

# TODO: make waitlist an enum allow other enums

    async def send_new_waitlist_entry(
        self, 
        name: str, 
        email: str, 
        comment: Optional[str] = None, 
        referral_source: Optional[str] = None
    ) -> None:
        message = f"🆕 *New Waitlist Entry:*\n\n*Name:* {name}\n*Email:* {email}"
        if comment:
            message += f"\n*Comment:* {comment}"
        if referral_source:
            message += f"\n*Referral Source:* {referral_source}"

        self.logger.debug("Formatted message for new waitlist entry.")
        await self.send_message(message)

    async def send_updated_waitlist_entry(
        self, 
        name: str, 
        email: str, 
        comment: Optional[str] = None, 
        referral_source: Optional[str] = None
    ) -> None:
        message = f"🔄 *Waitlist Entry Updated*\n\n*Name:* {name}\n*Email:* {email}"
        if comment:
            message += f"\n*Comment:* {comment}"
        if referral_source:
            message += f"\n*Referral Source:* {referral_source}"

        self.logger.debug("Formatted message for updated waitlist entry.")
        await self.send_message(message)

    async def close(self) -> None:
        """Close the underlying client"""
        await self.client.close()

if __name__ == "__main__":
    async def main():
        notifier = TelegramNotifier()
        await notifier.send_new_waitlist_entry("John Doe", "john@example.com", "Looking forward!", "referral:google")
        await notifier.close()

    asyncio.run(main())
