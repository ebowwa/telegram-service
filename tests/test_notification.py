import pytest
import os
from unittest.mock import AsyncMock, patch
from src.telegram_service.notification import TelegramNotifier

@pytest.fixture
def mock_env_vars(monkeypatch):
    # Use a properly formatted test token (format: numbers:alphanumeric)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-123456789")

@pytest.fixture
async def notifier(mock_env_vars):
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock()
    
    with patch('aiogram.Bot', return_value=mock_bot) as _:
        notifier = TelegramNotifier()
        notifier.bot = mock_bot  # Override the bot instance with our mock
        yield notifier
        await notifier.close()

@pytest.mark.asyncio
async def test_send_message(notifier):
    test_message = "Test message"
    await notifier.send_message(test_message)
    notifier.bot.send_message.assert_called_once_with(
        chat_id=notifier.TELEGRAM_CHAT_ID,
        text=test_message,
        parse_mode="Markdown"
    )

@pytest.mark.asyncio
async def test_send_new_waitlist_entry(notifier):
    await notifier.send_new_waitlist_entry(
        name="Test User",
        email="test@example.com",
        comment="Test comment",
        referral_source="Test source"
    )
    assert notifier.bot.send_message.called

@pytest.mark.asyncio
async def test_send_updated_waitlist_entry(notifier):
    await notifier.send_updated_waitlist_entry(
        name="Test User",
        email="test@example.com",
        comment="Test comment",
        referral_source="Test source"
    )
    assert notifier.bot.send_message.called
