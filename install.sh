#!/bin/bash

# Discord Bug Tracker Bot - Installation Script
# This script helps you install and configure the bot on Linux systems

set -e

echo "=========================================="
echo "Discord Bug Tracker Bot - Installation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run this script as root/sudo"
    echo "Run it as a regular user. The script will ask for sudo when needed."
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

echo "pip3 is available"
echo ""

# Get installation directory
INSTALL_DIR=$(pwd)
echo "Installation directory: $INSTALL_DIR"
echo ""

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo ""
echo "Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Created .env file"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "REQUIRED: Discord Bot Token"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "You need to create a Discord bot and get its token:"
    echo ""
    echo "1. Go to https://discord.com/developers/applications"
    echo "2. Click 'New Application' and give it a name"
    echo "3. Go to 'Bot' section → Click 'Add Bot'"
    echo "4. Under 'Token' click 'Reset Token' and copy it"
    echo "5. Enable these Privileged Gateway Intents:"
    echo "   - MESSAGE CONTENT INTENT"
    echo "   - SERVER MEMBERS INTENT"
    echo ""
    echo "Enter your Discord Bot Token:"
    read -r DISCORD_TOKEN
    
    if [ -z "$DISCORD_TOKEN" ]; then
        echo "No token provided. You'll need to edit .env manually."
    else
        sed -i "s/your_bot_token_here/$DISCORD_TOKEN/" .env
        echo "Token saved to .env"
    fi
else
    echo ".env file already exists"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Systemd Service Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Would you like to install the bot as a systemd service?"
echo "This will make the bot start automatically on boot. (y/n)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    SERVICE_FILE="/etc/systemd/system/discordbot.service"
    
    echo "Creating systemd service file..."
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Discord Bug Tracker Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    echo "Service file created at $SERVICE_FILE"
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable discordbot.service
    
    echo "Service enabled to start on boot"
    echo ""
    echo "Service management commands:"
    echo "  Start:   sudo systemctl start discordbot.service"
    echo "  Stop:    sudo systemctl stop discordbot.service"
    echo "  Restart: sudo systemctl restart discordbot.service"
    echo "  Status:  sudo systemctl status discordbot.service"
    echo "  Logs:    sudo journalctl -u discordbot.service -f"
else
    echo "Skipping systemd service installation."
    echo "You can run the bot manually with: .venv/bin/python bot.py"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installation Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo ""
echo "1. Invite the bot to your Discord server:"
echo "   Go to Discord Developer Portal → Your App → OAuth2 → URL Generator"
echo "   Select scopes: 'bot' and 'applications.commands'"
echo "   Select permissions: 397284598848 (or use the invite generator)"
echo "   Copy the generated URL and open it in your browser"
echo ""
echo "2. Start the bot:"
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "   sudo systemctl start discordbot.service"
else
    echo "   .venv/bin/python bot.py"
fi
echo ""
echo "3. In your Discord server, run:"
echo "   /bug_setup #your-bug-channel"
echo ""
echo "4. Start reporting bugs! The bot will create threads automatically."
echo ""
echo "For more information, see README.md"
echo ""
