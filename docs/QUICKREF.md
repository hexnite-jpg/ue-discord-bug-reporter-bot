# Discord Bug Tracker - Quick Reference

## 🎯 For Bug Reporters

### Submit a Bug
Just type your bug report in the designated channel:
```
The game crashes when I open the inventory on Linux
```

The bot will:
- Create a numbered bug report
- Start a thread for discussion
- Add reaction options

### Rate Limits
- 3 reports per 10 minutes per user
- Prevents spam

---

## 👥 For Bug Triagers/Developers

### Using Reactions (Recommended)

Click reactions on the bug report message:

| Reaction | Effect |
|----------|--------|
| 👀 | Mark as "Acknowledged" (Blue) |
| 🧑‍💻 | Mark as "In Progress" (Orange) + Assigns you |
| ✅ | Mark as "Fixed" (Green) + Locks thread |
| ❌ | Mark as "Won't Fix" (Gray) |
| 🚫 | Block the reporter permanently |
| ⭐ | Mark as "High Priority" (Gold) |

**Priority Order:** 🚫 > ✅ > ❌ > 🧑‍💻 > ⭐ > 👀

### Using Slash Commands

In the bug thread, type:

```/bug_setup #channel              - Configure bug channel (admin, one-time)/bug_status [status]          - Check or set status
/bug_assign @User             - Assign to someone
/bug_close                    - Mark fixed & lock thread
/bug_reopen                   - Unlock thread
/bug_priority high|normal     - Set priority
/bug_unblock <user_id>        - Unblock user (admin only)
```

---

## 🔧 For Administrators

### First-Time Setup

**Step 1: Invite the bot to your server**

Use the bot invite link with proper permissions (permission integer: `277025508416`)

**Step 2: Configure the bug report channel**

In Discord, run this command (admin only):
```
/bug_setup #bug-reports
```

Replace `#bug-reports` with your desired channel. The bot will:
- ✅ Check it has necessary permissions
- ✅ Save the configuration
- ✅ Start monitoring that channel

**That's it!** No server configuration files needed.

### For Bot Hosting (Plugin Developers)

If you're hosting the bot for multiple servers:

1. **Set up the bot token:**
   ```bash
   cd /home/botuser/discord_bot
   nano .env
   ```
   Add: `DISCORD_TOKEN=your_token_here`

2. **Enable intents in Discord Developer Portal:**
   - Message Content Intent ✓
   - Server Members Intent ✓

3. **Start the bot:**
   ```bash
   sudo systemctl start discordbot.service
   ```

4. **Tell server admins to run:**
   ```
   /bug_setup #their-channel
   ```

Each server configures independently!

### Bot Management

**Check status:**
```bash
sudo systemctl status discordbot.service
```

**View logs:**
```bash
sudo journalctl -u discordbot.service -f
```

**Restart bot:**
```bash
sudo systemctl restart discordbot.service
```

**Stop bot:**
```bash
sudo systemctl stop discordbot.service
```

### Unblock a User

```
/bug_unblock 123456789012345678
```

Or delete `blocked_ids.json` and restart the bot.

---

## 📊 Workflow Example

### Typical Bug Lifecycle

1. **User reports:** "Game crashes on startup"
   - Bot creates 🐞 Bug #42 thread

2. **Triager acknowledges:** Clicks 👀
   - Thread title: 👀 Bug #42 – Game crashes...
   - Status: Acknowledged (Blue)

3. **Developer takes it:** Clicks 🧑‍💻
   - Thread title: 🧑‍💻 Bug #42 – Game crashes...
   - Assigned to: @Developer
   - Status: In Progress (Orange)

4. **If urgent:** Clicks ⭐
   - Thread title: ⭐ Bug #42 – Game crashes...
   - Priority: High (Gold)

5. **Developer fixes it:** Clicks ✅
   - Thread title: ✅ Bug #42 – Game crashes...
   - Status: Fixed (Green)
   - Thread automatically locks

6. **If reopened:** Use `/bug_reopen`
   - Thread unlocks
   - Status cleared

---

## 🚫 Handling Abuse

### Block a Reporter

Click 🚫 on their bug report:
- User blocked immediately **in your server only**
- Future reports auto-deleted in your server
- Stored in `blocked_ids.json` per-server
- Persists across restarts
- **Does NOT affect other servers** using the bot

### What Happens to Blocked Users

- Reports are deleted instantly in your server
- They receive a DM notification (if DMs open)
- No records kept except user ID
- Can still report bugs in other servers

---

## 🔐 Privacy & Storage

**What the bot stores:**
- ✅ Blocked user IDs per server (`blocked_ids.json`)
- ✅ Channel configs per server (`guild_config.json`)
- ✅ Rate limits (in memory, resets on restart)

**What the bot DOESN'T store:**
- ❌ Message content/logs
- ❌ Analytics/metrics
- ❌ User behavior history
- ❌ Cross-server data or tracking

**Server Isolation:**
- ✅ Each server has independent block lists
- ✅ Each server has independent channel config
- ✅ No data shared between servers
- ✅ Complete privacy per server

**Where state lives:**
- Status → Discord reactions
- Assignments → Embed fields
- History → Discord threads

---

## ⚙️ Customization

### Change Rate Limits

Edit `bot.py`:
```python
RATE_LIMIT_REPORTS = 5  # Reports per window
RATE_LIMIT_WINDOW = timedelta(minutes=15)  # Time window
```

### Change Colors

Edit `bot.py`:
```python
REACTIONS = {
    '👀': {'status': 'Acknowledged', 'color': 0x3498db},
    # 0xRRGGBB format
}
```

### Add Custom Reactions

Edit `bot.py`:
```python
REACTIONS = {
    '🔥': {'status': 'Critical', 'color': 0xff0000},
    # Add more...
}
```

Then update in `on_message`:
```python
for emoji in ['👀', '🧑‍💻', '✅', '❌', '🚫', '⭐', '🔥']:
    await bug_message.add_reaction(emoji)
```

---

## 🐛 Troubleshooting

### Bot doesn't respond to messages
- ✓ Check `BUG_REPORT_CHANNEL_ID` in `.env`
- ✓ Verify Message Content Intent enabled
- ✓ Check bot can read the channel

### Slash commands not showing
- Wait 5 minutes after bot restart
- Check bot has `applications.commands` scope
- Try re-inviting the bot

### Reactions don't update
- ✓ Bot needs "Add Reactions" permission
- ✓ Bot needs "Manage Messages" permission
- ✓ Check reactions intent enabled

### Thread creation fails
- ✓ Bot needs "Create Public Threads"
- ✓ Channel must support threads
- ✓ Not rate-limited by Discord

### User not getting blocked
- ✓ Check `blocked_ids.json` created
- ✓ Check file permissions
- ✓ View logs for errors

---

## 📝 Files Overview

```
discord_bot/
├── bot.py              # Main bot code
├── .env                # Bot token only (KEEP SECRET!)
├── .env.example        # Template
├── guild_config.json   # Per-server channel configs (auto-created)
├── blocked_ids.json    # Blocked users (created on first block)
├── README.md           # Full documentation
├── QUICKREF.md         # This file
└── setup.sh            # Setup helper script
```

---

## 🎓 Best Practices

### For Triagers
- React 👀 to acknowledge you've seen it
- React 🧑‍💻 when starting work (claims it)
- React ⭐ for urgent bugs
- React ✅ only when truly fixed
- Use 🚫 sparingly for abuse

### For Developers
- Use threads to discuss
- Update status as you progress
- Link to commits/PRs in thread
- Use `/bug_assign` to delegate

### For Admins
- Monitor `blocked_ids.json` size
- Review blocked users periodically
- Watch logs for errors
- Keep backups of `.env`

---

## 📞 Support

Check logs:
```bash
sudo journalctl -u discordbot.service -n 100
```

Test in terminal:
```bash
cd /home/botuser/discord_bot
source .venv/bin/activate
python bot.py
# Press Ctrl+C to stop
```

---

**Version:** 1.0.0 (Stateless Edition)
**Last Updated:** 2026-01-08
