# Server Admin Quick Start Guide

## 🚀 Setting Up the Bug Tracker Bot

Hey! Thanks for adding the bug tracker bot to your server. Setup is super easy - just one command!

---

## Step 1: Run the Setup Command

In any channel on your Discord server, type:

```
/bug_setup #bug-reports
```

**Replace `#bug-reports` with your desired channel name.**

---

## Step 2: That's It!

The bot will:
- ✅ Check that it has the right permissions
- ✅ Configure your server
- ✅ Send a confirmation message
- ✅ Start monitoring that channel

---

## What Your Users Do

Your users simply post bug reports in that channel:

```
Game crashes when I open inventory
```

The bot automatically:
- Creates a numbered bug report
- Starts a thread for discussion
- Adds reaction buttons for status tracking

---

## Managing Bugs

### Using Reactions (Easiest)

Click on the bug report message:

- 👀 = Acknowledged
- 🧑‍💻 = In Progress (assigns to you)
- ✅ = Fixed (locks the thread)
- ❌ = Won't Fix
- 🚫 = Block that user
- ⭐ = High Priority

### Using Commands

In the bug thread:

```
/bug_assign @Developer    - Assign to someone
/bug_close                - Mark as fixed
/bug_priority high        - Set priority
/bug_reopen               - Unlock a closed bug
```

---

## Common Questions

### Can I change the channel later?

Yes! Just run `/bug_setup #new-channel` again.

### What permissions does the bot need?

The bot auto-checks, but it needs:
- Read/Send messages
- Manage messages
- Add reactions
- Create/manage threads

### Is my data stored somewhere?

Nope! The bot is "stateless":
- Bug status = stored in Discord reactions
- No database
- No logs
- Only blocked user IDs are saved

### Can I unblock a user?

Yes, use:
```
/bug_unblock <user_id>
```

---

## Need Help?

Check the full documentation: `README.md`

Or the quick reference: `QUICKREF.md`

---

**Pro Tip:** Pin the `/bug_setup` confirmation message in your channel so everyone knows how to use the tracker!

---

Made with ❤️ for game developers
