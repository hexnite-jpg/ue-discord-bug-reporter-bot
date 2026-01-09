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
