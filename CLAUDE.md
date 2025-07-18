# Telegram Service Project

## Project Overview
This is a Python-based Telegram notification service built for providing a clean interface for sending messages through Telegram. It's designed as both a standalone service and a reusable library using the aiogram v3.0+ framework.

## MCP (Model Context Protocol) Extension for Telegram Service

### What is MCP?
MCP (Model Context Protocol) is a protocol that allows AI assistants like Claude to interact with external services and tools through a standardized interface. For this Telegram service, we need to create an MCP extension that will enable Claude to:

1. **Send and receive Telegram messages** directly through the chat interface
2. **Manage Telegram bot operations** (start/stop bot, configure webhooks)
3. **Access Telegram API features** (user info, chat management, media handling)
4. **Monitor bot analytics** and performance metrics

### MCP Extension Architecture

The Telegram MCP extension should implement the following components:

#### 1. Server Component (`telegram-mcp-server`)
```typescript
// Core MCP server that bridges Claude <-> Telegram
interface TelegramMCPServer {
  // Initialize connection to Telegram Bot API
  initialize(botToken: string): Promise<void>
  
  // Message handling
  sendMessage(chatId: string, text: string, options?: MessageOptions): Promise<Message>
  receiveMessages(limit?: number): Promise<Message[]>
  
  // Bot management
  getBotInfo(): Promise<BotInfo>
  setWebhook(url: string): Promise<boolean>
  deleteWebhook(): Promise<boolean>
  
  // Chat operations
  getChatInfo(chatId: string): Promise<Chat>
  getChatMembers(chatId: string): Promise<ChatMember[]>
  
  // Media handling
  sendPhoto(chatId: string, photo: Buffer | string): Promise<Message>
  sendDocument(chatId: string, document: Buffer | string): Promise<Message>
}
```

#### 2. Tool Definitions
The MCP extension should expose these tools to Claude:

- **telegram_send_message**: Send text messages to Telegram chats
- **telegram_get_updates**: Retrieve recent messages and updates
- **telegram_manage_bot**: Start/stop bot, configure settings
- **telegram_chat_info**: Get information about chats and users
- **telegram_send_media**: Send photos, documents, and other media

#### 3. Resource Providers
Resources that should be accessible:
- Active chats list
- Message history
- Bot configuration
- Webhook status
- User/chat metadata

### Implementation Steps

1. **Set up MCP server structure**:
   ```bash
   telegram-mcp/
   ├── package.json
   ├── src/
   │   ├── index.ts          # MCP server entry point
   │   ├── telegram-client.ts # Telegram Bot API client
   │   ├── tools/            # MCP tool implementations
   │   ├── resources/        # Resource providers
   │   └── types/           # TypeScript definitions
   ```

2. **Configure MCP in Claude settings**:
   ```json
   {
     "mcpServers": {
       "telegram": {
         "command": "node",
         "args": ["path/to/telegram-mcp/dist/index.js"],
         "env": {
           "TELEGRAM_BOT_TOKEN": "your-bot-token-here"
         }
       }
     }
   }
   ```

3. **Environment Variables Required**:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
   - `TELEGRAM_API_URL`: (Optional) Custom API URL if using local Bot API server
   - `MCP_PORT`: (Optional) Port for MCP server

### Use Cases

1. **Customer Support Bot**:
   - Claude can directly respond to customer messages
   - Access chat history for context
   - Send formatted messages with buttons and media

2. **Notification System**:
   - Send alerts to specific channels
   - Schedule messages
   - Monitor delivery status

3. **Interactive Bot Development**:
   - Test bot responses in real-time
   - Debug message handling
   - Analyze user interactions

### Security Considerations

1. **Token Management**: Store bot tokens securely, never commit to repository
2. **Rate Limiting**: Implement rate limiting to prevent API abuse
3. **User Privacy**: Handle user data according to Telegram's privacy policies
4. **Webhook Security**: Use HTTPS and verify webhook signatures

### Development Workflow

1. First, analyze the existing telegram-service codebase
2. Identify integration points for MCP
3. Build the MCP server following the protocol specification
4. Test with Claude Code locally
5. Deploy and configure for production use

## Current Project Structure
```
telegram-service/
├── src/
│   └── telegram_service/
│       ├── __init__.py              # Package initialization
│       └── notification.py          # TelegramNotifier class implementation
├── tests/
│   └── test_notification.py         # Unit tests with mocked Telegram API
├── .env.template                    # Environment variable template
├── README.md                        # Project documentation
├── requirements.txt                 # Python dependencies (aiogram>=3.0)
├── setup.py                         # Package setup configuration
└── pytest.ini                       # Pytest configuration
```

## Key Features
- **TelegramNotifier Class**: Main interface for sending Telegram messages
- **Message Types**: Plain text with Markdown, waitlist notifications
- **Async Support**: Built on aiogram v3.0+ for async operations
- **Error Handling**: Comprehensive logging and credential validation
- **Testing**: Full test coverage with mocked Telegram API

## Development Setup
1. **Python Requirements**: Python 3.11+ required
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables** (create `.env` from `.env.template`):
   - `TELEGRAM_BOT_TOKEN`: Bot token from @BotFather
   - `TELEGRAM_CHAT_ID`: Target chat/channel ID
   - `TELEGRAM_PERSONAL_CHAT_ID`: Optional personal chat ID

## MCP Extension Integration Plan

### Bridging Python Service with TypeScript MCP Server

Since the existing service is Python-based and MCP servers are typically TypeScript/JavaScript, we need a bridge approach:

1. **Option 1: Python MCP Server** (Recommended)
   - Create a Python-based MCP server using the `mcp` Python SDK
   - Directly integrate with existing `TelegramNotifier` class
   - Minimal changes to existing codebase

2. **Option 2: TypeScript Wrapper**
   - Build TypeScript MCP server that spawns Python subprocess
   - Communicate via JSON-RPC or REST API
   - More complex but allows TypeScript tooling

### Proposed Python MCP Implementation

```python
# telegram_mcp_server.py
from mcp.server import Server
from mcp.types import Tool, Resource
from telegram_service import TelegramNotifier

class TelegramMCPServer:
    def __init__(self):
        self.server = Server("telegram-service")
        self.notifier = TelegramNotifier()
        self._register_tools()
    
    def _register_tools(self):
        # Tool: Send message
        self.server.add_tool(
            Tool(
                name="telegram_send_message",
                description="Send a message to Telegram",
                parameters={
                    "chat_id": {"type": "string"},
                    "message": {"type": "string"},
                    "parse_mode": {"type": "string", "default": "Markdown"}
                }
            ),
            self._send_message
        )
        
        # Tool: Send waitlist notification
        self.server.add_tool(
            Tool(
                name="telegram_waitlist_notify",
                description="Send waitlist entry notification",
                parameters={
                    "entry": {"type": "object"},
                    "is_update": {"type": "boolean", "default": False}
                }
            ),
            self._send_waitlist_notification
        )
```

### MCP Configuration for Claude

```json
{
  "mcpServers": {
    "telegram": {
      "command": "python",
      "args": ["/Users/ebowwa/apps/telegram-service/telegram_mcp_server.py"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "${TELEGRAM_BOT_TOKEN}",
        "TELEGRAM_CHAT_ID": "${TELEGRAM_CHAT_ID}"
      }
    }
  }
}
```

## Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Install as package
pip install -e .

# Use in Python code
from telegram_service import TelegramNotifier
notifier = TelegramNotifier()
await notifier.send_message("Hello from Claude!")
```

## Next Steps for MCP Extension
1. Install Python MCP SDK: `pip install mcp`
2. Create `telegram_mcp_server.py` implementing MCP protocol
3. Add MCP-specific dependencies to requirements.txt
4. Test with Claude Code locally
5. Package and deploy MCP extension
