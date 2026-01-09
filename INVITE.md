# Bot Invite Information

## Discord Bot Invite Link

To invite this bot to a Discord server, use the following URL format:

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=277025508416&scope=bot%20applications.commands
```

**Replace `YOUR_BOT_CLIENT_ID`** with your bot's actual client ID (found in Discord Developer Portal).

---

## Permissions Breakdown

The permission integer `277025508416` includes:

- ✅ View Channels (Read Messages)
- ✅ Send Messages
- ✅ Manage Messages (for editing embeds, pinning)
- ✅ Read Message History
- ✅ Add Reactions
- ✅ Create Public Threads
- ✅ Send Messages in Threads
- ✅ Manage Threads

These are the **minimum required** permissions for the bot to function properly.

---

## For Plugin Developers

### Getting Your Client ID

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Copy the "Application ID" (this is your client ID)

### Creating the Invite Link

Replace `YOUR_BOT_CLIENT_ID` in the template above with your actual ID:

```
https://discord.com/api/oauth2/authorize?client_id=1458822458588139734&permissions=277025508416&scope=bot%20applications.commands
```

### Sharing with Users

You can:
- Put this link on your plugin's website
- Include it in your plugin documentation
- Share it in your community Discord
- Add it to your game's settings

**Users click the link → Select their server → Bot is added!**

---

## Required Intents (Developer Portal)

Make sure these are enabled for your bot:

1. Go to Discord Developer Portal
2. Select your application
3. Go to "Bot" section
4. Under "Privileged Gateway Intents":
   - ✅ **Message Content Intent** (Required)
   - ✅ **Server Members Intent** (Required)

Without these intents, the bot won't work!

---

## Post-Invite Instructions

After a user invites the bot to their server, they need to run **one command**:

```
/bug_setup #their-channel
```

That's it! No server-side configuration files, no manual setup.

---

## For Your Plugin Documentation

Here's suggested text for your plugin docs:

---

### Setting Up Bug Reports

1. **Add the bot to your Discord server:**
   [Invite Bug Tracker Bot](YOUR_INVITE_LINK_HERE)

2. **Configure the channel:**
   ```
   /bug_setup #bug-reports
   ```

3. **Done!** Users can now submit bugs by posting in that channel.

The bot automatically creates threads, tracks status with reactions, and helps you manage community bug reports without any database or complex setup.

---

## Testing

To test the bot after inviting:

1. Run `/bug_setup #test-channel`
2. Post a test message in that channel
3. Watch the bot create a thread and add reactions
4. Try clicking reactions to change status

---

## Support

Point your users to:
- Full docs: `README.md`
- Quick start: `SERVER_ADMIN_GUIDE.md`
- Command reference: `QUICKREF.md`

---

## Multi-Server Support

This bot is designed to work across **unlimited Discord servers simultaneously**:

- ✅ Each server configures independently
- ✅ No cross-contamination
- ✅ No shared data between servers
- ✅ Scales infinitely

Perfect for plugin developers who want to provide a unified bug tracking solution!
