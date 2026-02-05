# Unreal Engine Plugin Integration Guide

This bot is designed to work seamlessly with the Discord Bug Reporter plugin for Unreal Engine.

## How It Works

### 1. Bug Reports

When a player submits a bug report via the Discord Bug Reporter plugin:

**The plugin sends:**
- Discord embed with fields:
  - Response Type (e.g., "Error / Bug Report")
  - Map name
  - Optional: User ID (Player GUID)
  - Location (BugItGo coordinates)
  - Screenshot (attached to embed)
- Optional: Log file as a second message

**The bot processes it:**
- Detects the webhook embed automatically
- Parses all fields from your plugin
- Creates a thread with format: `Bug – [Type] – [Map]`
- Preserves the screenshot in the embed
- Adds reaction-based status tracking
- Waits for log file attachment (30-second window)

### 2. Log File Association

If you enabled logs in the project settings:

- Bot detects it within 30 seconds
- Automatically moves it to the correct bug thread
- Deletes the standalone log message
- Keeps everything organized

## Embed Format Expected

The bot parses embeds with these field names:

```
Response Type: Error / Bug Report
Map: YourMapName
User ID: B7D73DA4-81E8-58B53C35
BugItGo: -200.00 0.00 92.00 352.65 174.85 0.00
```

**Field Matching (case-insensitive):**
- "Response Type" → Bug type
- "Map" → Map name
- "User ID" → Player ID
- "BugItGo" or "Location" → Coordinates

### 1. Configure the Bot

Run once in your Discord server:
```
/bug_setup #bug-reports
```

Replace `#bug-reports` with the channel where your webhook posts.

## Example Flow

**Plugin sends embed:**
```
Response Type: Error / Bug Report
Map: Untitled_1
User ID: B7D73DA4-81E8-58B53C35
BugItGo: -200.00 0.00 92.00 352.65 174.85 0.00
[Screenshot attached]
```

**Bot creates:**
```
Bug – Error / Bug Report – Untitled_1
├─ Embed with all data
├─ Screenshot preserved
├─ Status: New
├─ Assigned to: Unassigned
└─ Reactions: 🧑‍💻 ✅ ❌ ⭐
```

**If log file follows within 30 seconds:**
```
Thread receives:
📎 Log File: GameLog_2026-01-08.txt
[File attached]
```

## Features

### Automatic Parsing
- ✅ Response Type → Displayed in bug thread title
- ✅ Map name → Shown in title and embed
- ✅ User/Player ID → Preserved in embed
- ✅ Location coords → Formatted in code block
- ✅ Screenshot → Preserved in embed image
- ✅ Log files → Auto-moved to thread

### Status Tracking
- 🧑‍💻 In Progress (auto-assigns)
- ✅ Fixed (locks thread)
- ❌ Won't Fix
- ⭐ High Priority

### Thread Organization
- One thread per bug
- Clean channel (originals deleted)
- All files in correct thread
- Easy to track and manage

## Compatibility

**Works with:**
- Webhook messages from Unreal Engine
- Multiple Discord servers simultaneously

**Per-server isolation:**
- Each game server has independent bug tracking
- Separate block lists
- No cross-contamination

## Testing

To test the integration:

1. **Send a test bug report**
2. **Check that:**
   - Bot creates thread
   - Fields are parsed correctly
   - Screenshot appears in embed
   - Reactions are added

3. **Test log file:**
   - Send attachment within 30 seconds
   - Verify it appears in the thread

## Customization

### Field Name Variations

If you set the plugin to use different field names (User ID), update the parser in [bot.py](bot.py):

```python
def parse_plugin_embed(embed):
    # Add your custom field names here
    if 'YourFieldName' in field_name:
        data['your_key'] = field_value
```

### Thread Title Format

Current format: `Bug – [Type] – [Map]`

To change, edit in [bot.py](bot.py):
```python
thread_title_parts = [f'Bug']
# Customize what goes in the title
```

### Log File Timeout

Default: 30 seconds

To change:
```python
if (datetime.now() - timestamp).total_seconds() < 30:
```

## Troubleshooting

### Webhook messages not detected
- Ensure webhook posts to configured channel
- Check that embed has fields (not just description)
- Verify bot has permissions

### Log files not moving to threads
- Check timing (must be within 30 seconds)
- Ensure log file message is from same webhook
- Check bot has "Manage Messages" permission

### Fields not parsing
- Check exact field names in your embed
- Case-insensitive matching is enabled
- Add custom field names to parser if needed

### Screenshot not appearing
- Ensure image is embedded (not attached as file)
- Check webhook properly embeds image
- Verify image URL is accessible

## Plugin Code Integration

**Share:**
- Webhook embed creation code
- Any custom fields
- Log file attachment logic

## Trello Integration (Self-Hosted Only)

If you're running a self-hosted instance of this bot, you can enable Trello integration to send bug reports to a Trello board.

### Enabling Trello Support

Add to your `.env` file:
```
SELF_HOSTED=true
```

This unlocks the following commands:
- `/trello_setup` - Configure Trello credentials
- `/trello_remove` - Remove Trello configuration
- `/trello_status` - Check if Trello is configured
- `/trello_help` - Step-by-step setup guide

### Setup Steps

#### 1. Create a Power-Up
1. Go to https://trello.com/power-ups/admin
2. Click **New** to create a new Power-Up
3. Fill in a name (e.g., "Bug Tracker") and select a Workspace
4. Click **Create**

#### 2. Get Your API Key
1. In your new Power-Up, go to the **API Key** tab
2. Click **Generate a new API Key**
3. Copy the **API Key**

#### 3. Generate a Token
1. On the same page, click the **Token** link (on the right side of the API key)
2. Click **Allow** to authorize access to your Trello account
3. Copy the **Token** shown

#### 3. Get Your List ID
1. Open your Trello board in a browser
2. Add `.json` to the end of the URL
   - Example: `https://trello.com/b/abc123/my-board.json`
3. Press Ctrl+F and search for your list name (e.g., "Bugs")
4. Copy the `"id"` value next to it (looks like `"id":"60a1b2c3d4e5f6g7"`)

#### 4. Run the Setup Command
```
/trello_setup api_key:<your-key> token:<your-token> list_id:<your-list-id>
```

### Trello-Only Mode

Add `trello_only:true` to the setup command to disable normal bot features:

```
/trello_setup api_key:<key> token:<token> list_id:<id> trello_only:true
```

**In Trello-Only mode:**
- Bug reports only show the 📋 reaction
- Status reactions (🧑‍💻, ✅, ❌, ⭐) are disabled
- No embed updates when reactions change
- Only the Trello integration is active

### Usage

Once configured, react with 📋 on any bug report to send it to Trello as a card.

The card will include:
- Bug title
- Description and all parsed fields
- Link back to the Discord thread

### Security Notes

- Credentials are stored in `trello_config.json` on the server
- Only available for self-hosted instances
- Credentials are automatically deleted when the bot is removed from a server
