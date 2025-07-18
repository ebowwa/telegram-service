#!/bin/bash

# Script to run the Telegram MCP Server
# This script ensures the environment is set up correctly before launching

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with your Telegram credentials:"
    echo "  TELEGRAM_BOT_TOKEN=your_bot_token_here"
    echo "  TELEGRAM_CHAT_ID=your_default_chat_id_here"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Install/update dependencies
echo "Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet

# Run the MCP server
echo "Starting Telegram MCP Server..."
python3 "$SCRIPT_DIR/telegram_mcp_server.py"