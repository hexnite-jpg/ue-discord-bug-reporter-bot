#!/bin/bash

# Quick Setup Script for Discord Bug Tracker Bot

echo "==================================="
echo "Discord Bug Tracker Bot - Setup"
echo "==================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "IMPORTANT: You need to configure your bug report channel ID"
echo ""
echo "Steps to get your channel ID:"
echo "1. Enable Developer Mode in Discord:"
echo "   User Settings → Advanced → Developer Mode (toggle ON)"
echo ""
echo "2. Right-click the channel where bug reports should go"
echo "3. Click 'Copy ID'"
echo "4. Edit .env and set BUG_REPORT_CHANNEL_ID=<your_channel_id>"
echo ""

# Check current channel ID
CHANNEL_ID=$(grep BUG_REPORT_CHANNEL_ID .env | cut -d'=' -f2)

if [ "$CHANNEL_ID" == "1234567890123456789" ] || [ "$CHANNEL_ID" == "" ]; then
    echo "⚠️  WARNING: BUG_REPORT_CHANNEL_ID not configured!"
    echo ""
    echo "Would you like to set it now? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Enter your channel ID:"
        read -r new_channel_id
        sed -i "s/BUG_REPORT_CHANNEL_ID=.*/BUG_REPORT_CHANNEL_ID=$new_channel_id/" .env
        echo "✓ Channel ID updated!"
    fi
else
    echo "✓ Current channel ID: $CHANNEL_ID"
fi

echo ""
echo "==================================="
echo "Bot Permissions Required:"
echo "==================================="
echo "• Read Messages/View Channels"
echo "• Send Messages"
echo "• Manage Messages (edit embeds, pin)"
echo "• Add Reactions"
echo "• Create Public Threads"
echo "• Manage Threads"
echo ""
echo "Permission Integer: 277025508416"
echo ""

echo "==================================="
echo "Required Intents (Developer Portal):"
echo "==================================="
echo "• Message Content Intent"
echo "• Server Members Intent"
echo ""

echo "==================================="
echo "To start/restart the bot:"
echo "==================================="
echo "sudo systemctl restart discordbot.service"
echo "sudo systemctl status discordbot.service"
echo ""

echo "==================================="
echo "To view logs:"
echo "==================================="
echo "sudo journalctl -u discordbot.service -f"
echo ""

echo "Setup complete! Don't forget to:"
echo "1. Set BUG_REPORT_CHANNEL_ID in .env"
echo "2. Enable required intents in Discord Developer Portal"
echo "3. Restart the bot"
echo ""
