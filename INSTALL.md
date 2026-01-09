# Quick Installation Guide

## Prerequisites
- Linux system (Ubuntu/Debian recommended)
- Python 3.8 or higher
- Discord account with permissions to create bots

## Quick Install

1. **Download/Clone the bot:**
```bash
git clone <your-repo-url> discord-bug-tracker
cd discord-bug-tracker
```

2. **Run the installer:**
```bash
chmod +x install.sh
./install.sh
```

The installer will:
- Check Python dependencies
- Create a virtual environment
- Install required packages
- Set up your Discord token
- Optionally install as a systemd service

3. **Invite the bot to your server:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Select your application → OAuth2 → URL Generator
   - Scopes: `bot` and `applications.commands`
   - Bot Permissions: `397284598848` (or select: Send Messages, Manage Messages, Embed Links, Attach Files, Read Message History, Add Reactions, Create Public Threads, Manage Threads, Use Slash Commands)
   - Open the generated URL and invite the bot

4. **Configure the bot in your server:**
```
/bug_setup #your-bug-channel
```

## Manual Installation

If you prefer manual installation:

1. **Create virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
nano .env  # Add your Discord bot token
```

4. **Run the bot:**
```bash
python bot.py
```

## Systemd Service (Optional)

To run the bot as a service that starts on boot:

```bash
sudo nano /etc/systemd/system/discordbot.service
```

Add this content (adjust paths):
```ini
[Unit]
Description=Discord Bug Tracker Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/discord_bot
ExecStart=/path/to/discord_bot/.venv/bin/python /path/to/discord_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable discordbot.service
sudo systemctl start discordbot.service
```

## Post-Installation

1. **Test the bot:** Send a message in your configured channel
2. **Configure reactions:** React to bug reports to change status
3. **View statistics:** Run `/bug_stats` to see bug metrics
4. **Check your bugs:** Run `/bug_my_bugs` to see your assignments

## Updating the Bot

```bash
cd discord-bug-tracker
git pull
source .venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart discordbot.service  # if using systemd
```

## Troubleshooting

**Bot doesn't start:**
- Check logs: `sudo journalctl -u discordbot.service -n 50`
- Verify token in `.env` file
- Ensure intents are enabled in Discord Developer Portal

**Bot doesn't respond:**
- Make sure bot has proper permissions in the channel
- Run `/bug_setup` again to reconfigure
- Check bot is online in Discord

**Reactions don't work:**
- Bot needs "Add Reactions" permission
- Reactions are persistent across restarts

For more help, see README.md or the documentation files.
