# Discord Bug Tracker Bot for Unreal Engine

A stateless Discord bot for managing bug reports using reactions and threads. No database required!

**Works seamlessly with Hexnite's Unreal Engine Discord Bug Reporter Plugin for in-game bug reporting.
https://www.fab.com/listings/1b771480-3608-4bf7-b6f7-4ab74211d5a2

## Features

- **Webhook Integration** - Automatically processes bug reports from Hexnite's plugin.
- **Reaction-Based Workflow** - Status updates via emoji reactions (🧑‍💻 In Progress, ✅ Fixed, ❌ Won't Fix)
- **Thread Organization** - Auto-creates threads for each bug with all details
- **Player Blocking** - Block spammers by Player ID
- **Statistics** - Track bug status and completion rates
- **Zero Database** - All state stored in Discord (reactions, threads, embeds)

## Quick Start

```bash
git clone https://github.com/hexnite-jpg/ue-discord-bug-reporter-bot.git
cd ue-discord-bug-reporter-bot
chmod +x install.sh
./install.sh
```

See [INSTALL.md](docs/INSTALL.md) for detailed installation instructions.

## Documentation

- **[Installation Guide](docs/INSTALL.md)** - Complete setup instructions
- **[Plugin Integration](docs/PLUGIN_INTEGRATION.md)** - Connect your Unreal Engine project

## How It Works

1. Player reports bug in-game (via the plugin)
2. Bot receives webhook and creates formatted embed
3. Thread auto-created for discussion
4. Staff uses reactions to update status
5. Embed auto-compacts when resolved
6. Stats available via `/bug_stats`

## Commands

- `/bug_setup` - Configure bug report channel (Admin)
- `/bug_block_reporter` - Block a player ID (Admin)
- `/bug_unblock` - Unblock a player ID (Admin)
- `/bug_stats` - View bug statistics
- `/bug_my_bugs` - List bugs assigned to you (ephemeral)

## Requirements

- Python 3.8+
- Discord Bot with appropriate permissions
- Linux system (for systemd service)

## License

MIT License - Feel free to use and modify for your projects!

## Support

For issues or questions, open an issue on GitHub.
