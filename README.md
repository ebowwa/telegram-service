# Telegram Service

## Overview
A Python-based notification service that provides a clean interface for sending messages through Telegram. This service supports sending regular messages and specialized notifications for waitlist entries.

## Features
- Send plain text messages with Markdown support
- Send formatted waitlist entry notifications
- Async/await support using aiogram
- Comprehensive test suite
- Environment variable configuration

## Prerequisites
- Python 3.11 or higher
- A Telegram Bot Token (obtain from [@BotFather](https://t.me/botfather))
- A Telegram Chat ID

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/telegram-service.git
cd telegram-service
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.template .env
```
Then edit `.env` with your Telegram credentials:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TELEGRAM_PERSONAL_CHAT_ID=your_personal_chat_id_here  # Optional
```

## Usage

### As a standalone service
Run the service using the provided script:
```bash
./run_service.sh
```

### As a library
Import and use in your Python code:
```python
from telegram_service.notification import TelegramNotifier

async def main():
    notifier = TelegramNotifier()
    
    # Send a simple message
    await notifier.send_message("Hello from Telegram Service!")
    
    # Send a waitlist notification
    await notifier.send_new_waitlist_entry(
        name="John Doe",
        email="john@example.com",
        comment="Excited to join!",
        referral_source="Twitter"
    )
    
    await notifier.close()
```

## Development

### Running Tests
The project uses pytest for testing. Run tests using:
```bash
./run_tests.sh
```

Or manually:
```bash
pytest tests/ -v
```

### Scripts
- `run_service.sh`: Starts the notification service
- `run_tests.sh`: Runs the test suite
- `run_all.sh`: Runs tests first, then starts the service if tests pass

### Project Structure
```
telegram-service/
├── src/
│   └── telegram_service/
│       ├── __init__.py
│       └── notification.py
├── tests/
│   └── test_notification.py
├── .env.template
├── requirements.txt
├── pytest.ini
└── README.md
```

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Error Handling
The service includes comprehensive error handling for:
- Invalid Telegram credentials
- Network issues
- Message sending failures
- Invalid message formats

Check the logs for detailed error messages and stack traces.

## License
[Add your license here]

## Support
For support, please [create an issue](https://github.com/yourusername/telegram-service/issues) on the GitHub repository.
