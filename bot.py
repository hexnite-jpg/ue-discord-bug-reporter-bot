import discord
import os
import json
import re
import asyncio
import aiohttp
import io
from datetime import datetime, timedelta
from collections import defaultdict
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

# ========================
# CONFIGURATION
# ========================

# Guild configuration file (stores channel IDs per server)
GUILD_CONFIG_FILE = 'guild_config.json'

# Blocked users file (minimal storage for bans)
BLOCKED_USERS_FILE = 'blocked_ids.json'

# Reaction emoji mappings
REACTIONS = {
    '🧑‍💻': {'status': 'In Progress', 'color': 0xe67e22},  # Orange
    '✅': {'status': 'Fixed', 'color': 0x2ecc71},  # Green
    '❌': {'status': "Won't Fix", 'color': 0x95a5a6},  # Gray
    '⭐': {'status': 'High Priority', 'color': 0xf39c12},  # Gold
}

# Thread title emoji mapping
THREAD_EMOJI = {
    'In Progress': '🧑‍💻',
    'Fixed': '✅',
    "Won't Fix": '❌',
    'High Priority': '⭐',
}

# ========================
# BOT SETUP
# ========================

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# In-memory storage (resets on restart)
blocked_users = {}  # Maps guild_id -> set of blocked user IDs
guild_channels = {}  # Maps guild_id -> bug_report_channel_id
recent_bug_reports = {}  # Maps (guild_id, message_id) -> (thread_id, timestamp) for log file association
pending_log_files = {}  # Maps (guild_id, message_id) -> list of (message, timestamp) for delayed log files
recently_blocked_webhooks = {}  # Maps (guild_id, webhook_id) -> timestamp for blocking follow-up messages

# ========================
# UTILITY FUNCTIONS
# ========================

def load_guild_config():
    """Load guild configurations from file"""
    global guild_channels
    try:
        if os.path.exists(GUILD_CONFIG_FILE):
            with open(GUILD_CONFIG_FILE, 'r') as f:
                data = json.load(f)
                # Handle old format (channels nested) or new format (flat)
                if isinstance(data, dict) and 'channels' in data:
                    guild_channels = {int(k): int(v) for k, v in data.get('channels', {}).items()}
                else:
                    # Flat format - just channel IDs
                    guild_channels = {int(k): int(v) for k, v in data.items()}
            print(f'Loaded configuration for {len(guild_channels)} guilds', flush=True)
    except Exception as e:
        print(f'Error loading guild config: {e}', flush=True)
        guild_channels = {}

def save_guild_config():
    """Save guild configurations to file"""
    try:
        with open(GUILD_CONFIG_FILE, 'w') as f:
            # Convert int keys to strings for JSON
            data = {str(k): str(v) for k, v in guild_channels.items()}
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f'Error saving guild config: {e}', flush=True)

def get_bug_channel(guild_id):
    """Get the bug report channel for a guild"""
    return guild_channels.get(guild_id)

def set_bug_channel(guild_id, channel_id):
    """Set the bug report channel for a guild"""
    guild_channels[guild_id] = channel_id
    save_guild_config()

def load_blocked_users():
    """Load blocked user IDs from file (per-guild)"""
    global blocked_users
    try:
        if os.path.exists(BLOCKED_USERS_FILE):
            with open(BLOCKED_USERS_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys back to ints, values to sets
                blocked_users = {int(k): set(v) for k, v in data.items()}
            total_blocked = sum(len(users) for users in blocked_users.values())
            print(f'Loaded {total_blocked} blocked users across {len(blocked_users)} guilds', flush=True)
    except Exception as e:
        print(f'Error loading blocked users: {e}', flush=True)
        blocked_users = {}

def save_blocked_users():
    """Save blocked user IDs to file (per-guild)"""
    try:
        with open(BLOCKED_USERS_FILE, 'w') as f:
            # Convert int keys to strings, sets to lists for JSON
            data = {str(k): list(v) for k, v in blocked_users.items()}
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f'Error saving blocked users: {e}', flush=True)

def is_user_blocked(guild_id, user_id):
    """Check if a Discord user or Player ID is blocked in a specific guild"""
    if guild_id not in blocked_users:
        return False
    return str(user_id) in blocked_users[guild_id]

def block_user(guild_id, user_id):
    """Block a Discord user or Player ID in a specific guild"""
    if guild_id not in blocked_users:
        blocked_users[guild_id] = set()
    blocked_users[guild_id].add(str(user_id))
    save_blocked_users()

def unblock_user(guild_id, user_id):
    """Unblock a Discord user or Player ID in a specific guild"""
    if guild_id in blocked_users and str(user_id) in blocked_users[guild_id]:
        blocked_users[guild_id].remove(str(user_id))
        # Clean up empty sets
        if not blocked_users[guild_id]:
            del blocked_users[guild_id]
        save_blocked_users()
        
        # Also clear any recently blocked webhooks cache
        # (webhooks don't have player IDs, so we clear all for this guild)
        keys_to_remove = [k for k in recently_blocked_webhooks.keys() if k[0] == guild_id]
        for key in keys_to_remove:
            del recently_blocked_webhooks[key]
        print(f'Cleared {len(keys_to_remove)} webhook caches for guild {guild_id}', flush=True)

def parse_plugin_embed(embed):
    """Parse embed from Unreal Engine plugin webhook"""
    data = {
        'response_type': None,
        'map': None,
        'user_id': None,
        'location': None,
        'description': embed.description or 'No description provided'
    }
    
    print(f'Parsing embed with {len(embed.fields)} fields:', flush=True)
    
    for field in embed.fields:
        field_name = field.name.strip()
        field_value = field.value.strip()
        
        print(f'  Field: "{field_name}" = "{field_value[:50]}"', flush=True)
        
        if 'Response Type' in field_name or field_name == 'Response Type':
            data['response_type'] = field_value
        elif 'Map' in field_name or field_name == 'Map':
            data['map'] = field_value
        elif 'User ID' in field_name or field_name == 'User ID':
            data['user_id'] = field_value
        elif 'BugIt' in field_name or 'Location' in field_name:
            data['location'] = field_value
            print(f'  -> Captured location!', flush=True)
    
    print(f'Parsed data: {data}', flush=True)
    return data

def extract_player_id(embed):
    """Extract Player ID from webhook embed"""
    for field in embed.fields:
        if 'Player ID' in field.name or 'User ID' in field.name:
            # Strip backticks and whitespace from the value
            return field.value.strip().strip('`')
    return None

def get_current_status_from_reactions(message):
    """Determine current status from reactions, priority order"""
    priority_order = ['✅', '❌', '🧑‍💻', '⭐']
    
    for emoji in priority_order:
        for reaction in message.reactions:
            if str(reaction.emoji) == emoji and reaction.count > 1:
                # Only count if someone besides the bot reacted
                return emoji
    
    return None

async def get_assignee_from_reactions(message):
    """Get the first user who reacted with 🧑‍💻"""
    for reaction in message.reactions:
        if str(reaction.emoji) == '🧑‍💻':
            users = [user async for user in reaction.users() if not user.bot]
            if users:
                return users[0]
    return None

async def update_embed_from_reactions(message):
    """Update embed based on current reactions"""
    if not message.embeds:
        return
    
    embed = message.embeds[0]
    status_emoji = get_current_status_from_reactions(message)
    
    # Default to New status if no status reaction
    if status_emoji and status_emoji in REACTIONS:
        status_info = REACTIONS[status_emoji]
        embed.color = status_info['color']
        status_text = status_info['status']
    else:
        embed.color = 0x95a5a6  # Gray for New
        status_text = 'New'
    
    # Check if this is a resolved status (Fixed or Won't Fix)
    is_resolved = status_emoji in ['✅', '❌']
    
    # Check if embed is already compacted (only has Status field)
    is_compacted = len(embed.fields) == 1 and embed.fields[0].name == 'Status'
    
    # Get the thread from the message if it exists
    thread = None
    if hasattr(message, 'thread') and message.thread:
        thread = message.thread
    
    if is_resolved and thread and not is_compacted:
        # Only compact once - move detailed info to thread and compact the main embed
        # First check if details already exist in thread to avoid duplicates
        details_exist = False
        try:
            async for msg in thread.history(limit=50):
                if msg.author == bot.user and msg.embeds and msg.embeds[0].title == "Bug Report Details":
                    details_exist = True
                    break
        except Exception as e:
            print(f'Error checking thread history: {e}', flush=True)
        
        # Only send details if they don't already exist
        if not details_exist:
            # Save original embed data
            original_fields = list(embed.fields)
            original_description = embed.description
            original_image = embed.image.url if embed.image else None
            
            # Send detailed info to thread
            detail_embed = discord.Embed(
                title="Bug Report Details",
                description=original_description,
                color=embed.color,
                timestamp=datetime.now()
            )
            
            # Add all non-status fields
            for field in original_fields:
                if field.name not in ['Status', 'Assigned to', 'Priority']:
                    detail_embed.add_field(name=field.name, value=field.value, inline=field.inline)
            
            if original_image:
                detail_embed.set_image(url=original_image)
            
            try:
                await thread.send(embed=detail_embed)
            except Exception as e:
                print(f'Error sending details to thread: {e}', flush=True)
        
        # Create compact embed with just title and status
        compact_embed = discord.Embed(
            title=embed.title,
            color=embed.color,
            timestamp=datetime.now()
        )
        compact_embed.add_field(name='Status', value=status_text, inline=True)
        compact_embed.set_footer(text=embed.footer.text if embed.footer else '')
        
        await message.edit(embed=compact_embed)
    elif is_compacted and not is_resolved and thread:
        # Bug was reopened - restore full embed from thread details
        try:
            # Find the details message in the thread
            details_message = None
            async for msg in thread.history(limit=50):
                if msg.author == bot.user and msg.embeds and msg.embeds[0].title == "Bug Report Details":
                    details_message = msg
                    break
            
            if details_message and details_message.embeds:
                details_embed = details_message.embeds[0]
                
                # Reconstruct full embed
                full_embed = discord.Embed(
                    title=embed.title,
                    description=details_embed.description,
                    color=embed.color,
                    timestamp=datetime.now()
                )
                
                # Restore fields from details
                for field in details_embed.fields:
                    full_embed.add_field(name=field.name, value=field.value, inline=field.inline)
                
                # Add status tracking fields
                full_embed.add_field(name='Status', value=status_text, inline=True)
                
                # Update assignee
                assignee = await get_assignee_from_reactions(message)
                assignee_text = f"<@{assignee.id}>" if assignee else "Unassigned"
                full_embed.add_field(name='Assigned to', value=assignee_text, inline=True)
                
                # Update priority
                has_star = any(str(r.emoji) == '⭐' and r.count > 1 for r in message.reactions)
                priority_text = 'High Priority' if has_star else 'Normal'
                full_embed.add_field(name='Priority', value=priority_text, inline=True)
                
                # Restore image
                if details_embed.image:
                    full_embed.set_image(url=details_embed.image.url)
                
                full_embed.set_footer(text=embed.footer.text if embed.footer else '')
                
                await message.edit(embed=full_embed)
            else:
                # Fallback: just update status in compact view
                embed.color = 0x95a5a6 if status_text == 'New' else (0xffa500 if status_text == 'In Progress' else embed.color)
                embed.set_field_at(0, name='Status', value=status_text, inline=True)
                embed.timestamp = datetime.now()
                await message.edit(embed=embed)
        except Exception as e:
            print(f'Error restoring full embed: {e}', flush=True)
            # Fallback: just update status
            embed.color = 0x95a5a6 if status_text == 'New' else (0xffa500 if status_text == 'In Progress' else embed.color)
            embed.set_field_at(0, name='Status', value=status_text, inline=True)
            embed.timestamp = datetime.now()
            await message.edit(embed=embed)
    elif not is_compacted:
        # Normal embed update for non-resolved statuses
        # Update status field
        for i, field in enumerate(embed.fields):
            if field.name == 'Status':
                embed.set_field_at(i, name='Status', value=status_text, inline=True)
                break
        else:
            embed.add_field(name='Status', value=status_text, inline=True)
        
        # Update assignee
        assignee = await get_assignee_from_reactions(message)
        assignee_text = f"<@{assignee.id}>" if assignee else "Unassigned"
        
        for i, field in enumerate(embed.fields):
            if field.name == 'Assigned to':
                embed.set_field_at(i, name='Assigned to', value=assignee_text, inline=True)
                break
        else:
            embed.add_field(name='Assigned to', value=assignee_text, inline=True)
        
        # Update priority
        has_star = any(str(r.emoji) == '⭐' and r.count > 1 for r in message.reactions)
        priority_text = 'High Priority' if has_star else 'Normal'
        
        for i, field in enumerate(embed.fields):
            if field.name == 'Priority':
                embed.set_field_at(i, name='Priority', value=priority_text, inline=True)
                break
        else:
            embed.add_field(name='Priority', value=priority_text, inline=True)
        
        # Update timestamp
        embed.timestamp = datetime.now()
        
        await message.edit(embed=embed)
    
    # Update thread title if status changed
    if thread and status_emoji:
        await update_thread_title(thread, status_text)

async def update_thread_title(thread, status):
    """Update thread title"""
    bug_num_match = re.search(r'Bug #(\d+)', thread.name)
    bug_num = bug_num_match.group(0) if bug_num_match else 'Bug'
    
    # Extract original description (after the – )
    desc_match = re.search(r'–\s*(.+)', thread.name)
    description = desc_match.group(1) if desc_match else thread.name
    
    # Remove old emoji if present
    for old_emoji in THREAD_EMOJI.values():
        description = description.replace(old_emoji, '').strip()
    
    new_title = f"{bug_num} – {description}"
    
    if thread.name != new_title:
        try:
            await thread.edit(name=new_title[:100])  # Discord limit
        except:
            pass

# ========================
# EVENT HANDLERS
# ========================

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})', flush=True)
    load_guild_config()
    load_blocked_users()
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} slash commands', flush=True)
    except Exception as e:
        print(f'Error syncing commands: {e}', flush=True)
    
    print('------', flush=True)
    print('Bug tracker bot is ready!', flush=True)
    print(f'Configured in {len(guild_channels)} guilds', flush=True)

@bot.event
async def on_guild_remove(guild):
    """Clean up data when bot is removed from a guild"""
    print(f'Bot removed from guild: {guild.name} (ID: {guild.id})', flush=True)
    
    # Remove guild configuration
    if guild.id in guild_channels:
        del guild_channels[guild.id]
        save_guild_config()
        print(f'Removed guild config for {guild.id}', flush=True)
    
    # Remove blocked users for this guild
    if guild.id in blocked_users:
        del blocked_users[guild.id]
        save_blocked_users()
        print(f'Removed blocked users for {guild.id}', flush=True)
    
    # Clean up in-memory data
    keys_to_remove = [k for k in recently_blocked_webhooks.keys() if k[0] == guild.id]
    for key in keys_to_remove:
        del recently_blocked_webhooks[key]
    
    keys_to_remove = [k for k in pending_log_files.keys() if k[0] == guild.id]
    for key in keys_to_remove:
        del pending_log_files[key]
    
    keys_to_remove = [k for k in recent_bug_reports.keys() if k[0] == guild.id]
    for key in keys_to_remove:
        del recent_bug_reports[key]
    
    print(f'Cleanup complete for guild {guild.id}', flush=True)

@bot.event
async def on_message(message):
    """Handle incoming bug reports"""
    global bug_counter
    
    # IMPORTANT: Ignore messages from this bot itself to prevent loops
    if message.author == bot.user:
        return
    
    # Only process messages in guilds (not DMs)
    if not message.guild:
        await bot.process_commands(message)
        return
    
    # Get the configured bug report channel for this guild
    bug_channel_id = get_bug_channel(message.guild.id)
    
    # Debug logging
    print(f'Message from {message.author.name} (bot={message.author.bot}) in channel {message.channel.id}', flush=True)
    print(f'Configured channel: {bug_channel_id}, Has embeds: {len(message.embeds)}, Has attachments: {len(message.attachments)}', flush=True)
    print(f'Message content: {message.content[:100] if message.content else "None"}', flush=True)
    if message.embeds:
        print(f'Embed fields: {[(f.name, f.value[:50]) for f in message.embeds[0].fields]}', flush=True)
    
    # Only process messages in the bug report channel
    if not bug_channel_id or message.channel.id != bug_channel_id:
        await bot.process_commands(message)
        return
    
    # Only process webhook messages - ignore regular user messages
    if not message.author.bot:
        await bot.process_commands(message)
        return
    
    # Check if this is a log file attachment following a bug report
    # Skip if message also has embeds (that's the main bug report)
    if message.attachments and not message.embeds:
        # Check if this webhook was recently blocked (within last 60 seconds)
        webhook_key = (message.guild.id, message.author.id)
        if webhook_key in recently_blocked_webhooks:
            block_time = recently_blocked_webhooks[webhook_key]
            if (datetime.now() - block_time).total_seconds() < 60:
                print(f'Deleting log file from recently blocked webhook', flush=True)
                await message.delete()
                return
        
        # Always store log files as pending - they'll be processed by the next report
        print(f'Log file received, storing as pending', flush=True)
        temp_key = (message.guild.id, message.author.id)
        if temp_key not in pending_log_files:
            pending_log_files[temp_key] = []
        pending_log_files[temp_key].append((message, datetime.now()))
        return
    
    # Handle webhook messages with embeds (from Unreal Engine plugin)
    if message.embeds:
        webhook_key = (message.guild.id, message.author.id)
        
        # Check if Player ID is blocked before processing
        player_id = extract_player_id(message.embeds[0])
        if player_id and is_user_blocked(message.guild.id, player_id):
            print(f'Blocked player {player_id} attempted to submit report, deleting', flush=True)
            # Mark this webhook as recently blocked to catch follow-up log files
            recently_blocked_webhooks[webhook_key] = datetime.now()
            await message.delete()
            return
        
        # Clear recently blocked flag since this is a valid report
        if webhook_key in recently_blocked_webhooks:
            del recently_blocked_webhooks[webhook_key]
        
        await process_webhook_bug_report(message)
        return
    
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    """Handle webhook messages that are edited to add embeds"""
    # Only process if embeds were added
    if not after.embeds or before.embeds:
        return
    
    # Only process webhook bots in configured channels
    if not after.author.bot or after.author == bot.user:
        return
    
    if not after.guild:
        return
    
    bug_channel_id = get_bug_channel(after.guild.id)
    if not bug_channel_id or after.channel.id != bug_channel_id:
        return
    
    print(f'Message edited by {after.author.name}, now has {len(after.embeds)} embeds', flush=True)
    
    # Check if Player ID is blocked before processing
    player_id = extract_player_id(after.embeds[0])
    if player_id and is_user_blocked(after.guild.id, player_id):
        print(f'Blocked player {player_id} attempted to submit report, deleting', flush=True)
        # Mark this webhook as recently blocked to catch follow-up log files
        webhook_key = (after.guild.id, after.author.id)
        recently_blocked_webhooks[webhook_key] = datetime.now()
        await after.delete()
        return
    
    # Clear recently blocked flag since this is a valid report
    webhook_key = (after.guild.id, after.author.id)
    if webhook_key in recently_blocked_webhooks:
        del recently_blocked_webhooks[webhook_key]
    
    # Remove this message from pending log files if it was stored there
    # (This is the main bug report message, not a separate log file)
    if webhook_key in pending_log_files:
        pending_log_files[webhook_key] = [(msg, ts) for msg, ts in pending_log_files[webhook_key] if msg.id != after.id]
        if not pending_log_files[webhook_key]:
            del pending_log_files[webhook_key]
    
    # Process as new bug report
    await process_webhook_bug_report(after)

async def process_webhook_bug_report(message):
    """Process a webhook bug report with embeds"""
    embed = message.embeds[0]
    
    # Double-check player isn't blocked (safety check)
    player_id = extract_player_id(embed)
    if player_id and is_user_blocked(message.guild.id, player_id):
        print(f'Blocked player {player_id} caught in process_webhook_bug_report, aborting', flush=True)
        try:
            await message.delete()
        except:
            pass
        return
    
    # Parse the plugin embed
    plugin_data = parse_plugin_embed(embed)
    
    # Use the original embed title if available, otherwise use first line of description
    title = embed.title if embed.title else (plugin_data['description'].split('\n')[0] if plugin_data['description'] else 'Bug Report')
    
    # Always use the original embed color from the plugin
    embed_color = embed.color if embed.color else 0x95a5a6  # Gray fallback if no color
    
    # Create enhanced embed with parsed data
    bug_embed = discord.Embed(
        title=title,
        description=plugin_data['description'],
        color=embed_color,
        timestamp=datetime.now()
    )
    
    # Add fields from plugin
    if plugin_data['response_type']:
        bug_embed.add_field(name='Type', value=plugin_data['response_type'], inline=True)
    if plugin_data['map']:
        bug_embed.add_field(name='Map', value=plugin_data['map'], inline=True)
    if plugin_data['user_id']:
        bug_embed.add_field(name='Player ID', value=plugin_data['user_id'], inline=True)
    
    # Add status tracking fields
    bug_embed.add_field(name='Status', value='New', inline=True)
    bug_embed.add_field(name='Assigned to', value='Unassigned', inline=True)
    bug_embed.add_field(name='Priority', value='Normal', inline=True)
    
    # Add location if available
    if plugin_data['location']:
        bug_embed.add_field(name='Location', value=plugin_data['location'], inline=False)
    
    bug_embed.set_footer(text=f'Reported via {message.author.name}')
    
    # Download and re-upload screenshot from embed image if available
    screenshot_file = None
    if embed.image:
        try:
            # Download the image from the embed URL
            async with aiohttp.ClientSession() as session:
                async with session.get(embed.image.url) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        # Extract filename from URL or use default
                        filename = embed.image.url.split('/')[-1].split('?')[0]
                        if not filename or '.' not in filename:
                            filename = 'screenshot.png'
                        screenshot_file = discord.File(io.BytesIO(image_data), filename=filename)
                        bug_embed.set_image(url=f"attachment://{filename}")
        except Exception as e:
            print(f'Error downloading screenshot from embed: {e}', flush=True)
            screenshot_file = None
    
    if screenshot_file:
        bug_message = await message.channel.send(embed=bug_embed, file=screenshot_file)
    else:
        bug_message = await message.channel.send(embed=bug_embed)
    
    # Create thread - use title but limit length
    thread = await bug_message.create_thread(
        name=title[:100],  # Discord limit
        auto_archive_duration=1440  # 24 hours
    )
    
    # Track this bug report for log file association
    report_key = (message.guild.id, message.id)
    recent_bug_reports[report_key] = (thread.id, datetime.now(), message.author.id)
    
    # If the original webhook message has attachments (additional files), send them to thread
    if message.attachments:
        for attachment in message.attachments:
            try:
                await thread.send(
                    f"**Attachment:** {attachment.filename}",
                    file=await attachment.to_file()
                )
            except Exception as e:
                print(f'Error copying attachment to thread: {e}', flush=True)
    
    # Wait a moment for any late-arriving log files
    await asyncio.sleep(0.5)
    
    # Check for pending log files that arrived before the thread was ready
    # Look for pending files from this webhook
    webhook_key = (message.guild.id, message.author.id)
    if webhook_key in pending_log_files:
        # Get snapshot of pending files to process (in case new ones arrive during processing)
        files_to_process = pending_log_files[webhook_key][:]
        
        # Only process log files that arrived within 3 seconds of this message
        # This prevents race conditions when multiple players submit reports simultaneously
        message_time = message.created_at
        matched_files = []
        
        for log_message, log_timestamp in files_to_process:
            time_diff = abs((message_time - log_message.created_at).total_seconds())
            if time_diff <= 3.0:
                matched_files.append((log_message, log_timestamp))
            else:
                print(f'Skipping log file (time diff {time_diff:.1f}s too large)', flush=True)
        
        if matched_files:
            print(f'Processing {len(matched_files)} pending log files (out of {len(files_to_process)} total)', flush=True)
        
        for log_message, log_timestamp in matched_files:
            try:
                # Move attachments to thread
                for attachment in log_message.attachments:
                    print(f'Sending log file {attachment.filename} to thread {thread.id}', flush=True)
                    await thread.send(
                        f"**Log File:** {attachment.filename}",
                        file=await attachment.to_file()
                    )
                print(f'Moved pending log file to thread {thread.id}', flush=True)
            except Exception as e:
                print(f'Error moving pending log file: {e}', flush=True)
            
            # Try to delete the original log message
            try:
                await log_message.delete()
            except Exception as e:
                print(f'Could not delete log message (may already be deleted): {e}', flush=True)
            
            # Remove this specific file from pending
            if webhook_key in pending_log_files and (log_message, log_timestamp) in pending_log_files[webhook_key]:
                pending_log_files[webhook_key].remove((log_message, log_timestamp))
        
        # If no more pending files, clean up the key
        if webhook_key in pending_log_files and not pending_log_files[webhook_key]:
            del pending_log_files[webhook_key]
    
    # Add default reactions to our new message
    for emoji in ['🧑‍💻', '✅', '❌', '⭐']:
        await bug_message.add_reaction(emoji)
    
    # Try to delete original webhook message (may fail if already deleted)
    try:
        await message.delete()
    except:
        pass
    
    print(f'Created bug report from webhook in guild {message.guild.id}', flush=True)

@bot.event
async def on_raw_reaction_add(payload):
    """Handle reaction additions (works on uncached messages)"""
    # Ignore bot reactions
    if payload.user_id == bot.user.id:
        return
    
    # Fetch the channel and message
    channel = bot.get_channel(payload.channel_id)
    if not channel:
        return
    
    try:
        message = await channel.fetch_message(payload.message_id)
    except:
        return
    
    # Only process reactions on bot messages with embeds
    if not message.embeds or message.author != bot.user:
        return
    
    # Get the emoji
    emoji = str(payload.emoji)
    
    # Handle resolution (lock thread)
    if emoji == '✅':
        if isinstance(message.channel, discord.Thread):
            try:
                await message.channel.edit(locked=True, archived=False)
            except:
                pass
    
    # Update embed
    await update_embed_from_reactions(message)

@bot.event
async def on_raw_reaction_remove(payload):
    """Handle reaction removals (works on uncached messages)"""
    # Ignore bot reactions
    if payload.user_id == bot.user.id:
        return
    
    # Fetch the channel and message
    channel = bot.get_channel(payload.channel_id)
    if not channel:
        return
    
    try:
        message = await channel.fetch_message(payload.message_id)
    except:
        return
    
    # Only process reactions on bot messages with embeds
    if not message.embeds or message.author != bot.user:
        return
    
    # Update embed
    await update_embed_from_reactions(message)

# ========================
# SLASH COMMANDS
# ========================

@bot.tree.command(name='bug_setup', description='Configure bug report channel (Admin only)')
@app_commands.describe(
    channel='The channel where bug reports will be submitted'
)
@app_commands.default_permissions(administrator=True)
async def bug_setup(interaction: discord.Interaction, channel: discord.TextChannel):
    """Configure the bug report channel for this server"""
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            'You need administrator permissions to configure the bug tracker.',
            ephemeral=True
        )
        return
    
    # Check if bot has necessary permissions in the channel
    bot_permissions = channel.permissions_for(interaction.guild.me)
    required_perms = [
        'view_channel',
        'send_messages',
        'manage_messages',
        'add_reactions',
        'create_public_threads',
        'manage_threads'
    ]
    
    missing_perms = [perm for perm in required_perms if not getattr(bot_permissions, perm)]
    
    if missing_perms:
        await interaction.response.send_message(
            f'I am missing the following permissions in {channel.mention}:\n' +
            '\n'.join(f'• {perm.replace("_", " ").title()}' for perm in missing_perms) +
            '\n\nPlease grant these permissions and try again.',
            ephemeral=True
        )
        return
    
    # Save configuration
    set_bug_channel(interaction.guild.id, channel.id)
    
    # Send confirmation
    embed = discord.Embed(
        title='✅ Bug Tracker Configured!',
        description=f'Bug reports will now be monitored in {channel.mention}',
        color=0x2ecc71
    )
    embed.add_field(
        name='How it works',
        value=(
            '1. Plugin posts bug reports in that channel\n'
            '2. Bot creates a thread for each report\n'
            '3. Use reactions or commands to manage bugs'
        ),
        inline=False
    )
    embed.add_field(
        name='Reactions',
        value=(
            '🧑\u200d💻 In Progress • ✅ Fixed • ❌ Won\'t Fix • ⭐ High Priority'
        ),
        inline=False
    )
    embed.add_field(
        name='Commands',
        value='Use `/bug_` commands in threads to manage bugs',
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)
    
    # Send a test message to the channel
    test_embed = discord.Embed(
        title='Bug Tracker Active',
        description=(
            'This channel is now configured for bug reports!\n\n'
            '**Staff:** Use reactions or `/bug_` commands to manage.'
        ),
        color=0x3498db
    )
    await channel.send(embed=test_embed)

@bot.tree.command(name='bug_block_reporter', description='Block a user/player ID (admin only)')
@app_commands.describe(user_id='The user/player ID to block')
async def bug_block_reporter(interaction: discord.Interaction, user_id: str):
    """Block a user in this server"""
    # Check if user has permission
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message('You need administrator permissions.', ephemeral=True)
        return
    
    if not interaction.guild:
        await interaction.response.send_message('This command must be used in a server.', ephemeral=True)
        return
    
    block_user(interaction.guild.id, user_id)
    await interaction.response.send_message(f'User/Player `{user_id}` has been blocked in this server.')
    print(f'User/Player {user_id} blocked via command in guild {interaction.guild.id}', flush=True)

async def blocked_id_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    """Autocomplete function to show blocked IDs"""
    if not interaction.guild:
        return []
    
    guild_id = interaction.guild.id
    if guild_id not in blocked_users or not blocked_users[guild_id]:
        return [app_commands.Choice(name='No blocked users', value='none')]
    
    # Get all blocked IDs for this guild
    blocked_ids = list(blocked_users[guild_id])
    
    # Filter based on what user is typing
    if current:
        blocked_ids = [bid for bid in blocked_ids if current.lower() in bid.lower()]
    
    # Return up to 25 choices (Discord limit)
    return [
        app_commands.Choice(name=f'{bid}', value=bid)
        for bid in blocked_ids[:25]
    ]

@bot.tree.command(name='bug_unblock', description='Unblock a user (admin only)')
@app_commands.describe(user_id='The user/player ID to unblock')
@app_commands.autocomplete(user_id=blocked_id_autocomplete)
async def bug_unblock(interaction: discord.Interaction, user_id: str):
    """Unblock a user in this server"""
    # Check if user has permission
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message('You need administrator permissions.', ephemeral=True)
        return
    
    if not interaction.guild:
        await interaction.response.send_message('This command must be used in a server.', ephemeral=True)
        return
    
    if user_id == 'none':
        await interaction.response.send_message('No blocked users to unblock.', ephemeral=True)
        return
    
    unblock_user(interaction.guild.id, user_id)
    await interaction.response.send_message(f'User/Player `{user_id}` has been unblocked in this server.')

@bot.tree.command(name='bug_stats', description='Show bug statistics')
async def bug_stats(interaction: discord.Interaction):
    """Show statistics about bugs in the configured channel"""
    if not interaction.guild:
        await interaction.response.send_message('This command must be used in a server.', ephemeral=True)
        return
    
    # Get the configured bug channel
    channel_id = get_bug_channel(interaction.guild.id)
    if not channel_id:
        await interaction.response.send_message('Bug tracker is not configured. Use `/bug_setup` first.', ephemeral=True)
        return
    
    channel = interaction.guild.get_channel(channel_id)
    if not channel:
        await interaction.response.send_message('Configured bug channel not found.', ephemeral=True)
        return
    
    # Defer response since this might take a while
    await interaction.response.defer()
    
    # Count bugs by status
    stats = {
        'total': 0,
        'new': 0,
        'in_progress': 0,
        'fixed': 0,
        'wont_fix': 0,
        'blocked': 0,
        'high_priority': 0
    }
    
    # Scan the channel for bug reports (no limit - scan all messages)
    async for message in channel.history(limit=None):
        # Only count bot messages with embeds (bug reports)
        if message.author != bot.user or not message.embeds:
            continue
        
        stats['total'] += 1
        
        # Check status from reactions
        status_emoji = get_current_status_from_reactions(message)
        
        if status_emoji == '🧑‍💻':
            stats['in_progress'] += 1
        elif status_emoji == '✅':
            stats['fixed'] += 1
        elif status_emoji == '❌':
            stats['wont_fix'] += 1
        else:
            stats['new'] += 1
        
        # Check for high priority
        has_star = any(str(r.emoji) == '⭐' and r.count > 1 for r in message.reactions)
        if has_star:
            stats['high_priority'] += 1
    
    # Build embed
    embed = discord.Embed(
        title='Bug Report Statistics',
        color=0x3498db,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name='Overview',
        value=f"**Total Reports:** {stats['total']}\n**High Priority:** {stats['high_priority']}",
        inline=False
    )
    
    embed.add_field(
        name='🔵 New',
        value=str(stats['new']),
        inline=True
    )
    
    embed.add_field(
        name='🟠 In Progress',
        value=str(stats['in_progress']),
        inline=True
    )
    
    embed.add_field(
        name='🟢 Fixed',
        value=str(stats['fixed']),
        inline=True
    )
    
    embed.add_field(
        name='⚪ Won\'t Fix',
        value=str(stats['wont_fix']),
        inline=True
    )
    
    embed.add_field(
        name='🔴 Blocked',
        value=str(stats['blocked']),
        inline=True
    )
    
    # Calculate completion rate
    if stats['total'] > 0:
        completed = stats['fixed'] + stats['wont_fix']
        completion_rate = (completed / stats['total']) * 100
        embed.add_field(
            name='Completion Rate',
            value=f"{completion_rate:.1f}%",
            inline=True
        )
    
    embed.set_footer(text=f'Scanned all messages in #{channel.name}')
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name='bug_my_bugs', description='Show bugs assigned to you')
async def bug_my_bugs(interaction: discord.Interaction):
    """Show all bugs assigned to the user"""
    if not interaction.guild:
        await interaction.response.send_message('This command must be used in a server.', ephemeral=True)
        return
    
    # Get the configured bug channel
    channel_id = get_bug_channel(interaction.guild.id)
    if not channel_id:
        await interaction.response.send_message('Bug tracker is not configured. Use `/bug_setup` first.', ephemeral=True)
        return
    
    channel = interaction.guild.get_channel(channel_id)
    if not channel:
        await interaction.response.send_message('Configured bug channel not found.', ephemeral=True)
        return
    
    # Defer response since this might take a while (ephemeral)
    await interaction.response.defer(ephemeral=True)
    
    # Find all bugs assigned to this user
    assigned_bugs = []
    
    async for message in channel.history(limit=None):
        # Only check bot messages with embeds (bug reports)
        if message.author != bot.user or not message.embeds:
            continue
        
        # Check if user reacted with 🧑‍💻
        for reaction in message.reactions:
            if str(reaction.emoji) == '🧑‍💻':
                users = [user async for user in reaction.users() if user.id == interaction.user.id]
                if users:
                    # Get the status from reactions
                    status_emoji = get_current_status_from_reactions(message)
                    status_text = REACTIONS.get(status_emoji, {}).get('status', 'New') if status_emoji else 'New'
                    
                    # Get thread link
                    thread_url = f"https://discord.com/channels/{interaction.guild.id}/{message.id}"
                    
                    assigned_bugs.append({
                        'title': message.embeds[0].title,
                        'status': status_text,
                        'url': thread_url,
                        'high_priority': any(str(r.emoji) == '⭐' and r.count > 1 for r in message.reactions)
                    })
                break
    
    # Build response embed
    if not assigned_bugs:
        embed = discord.Embed(
            title='Your Assigned Bugs',
            description='You have no bugs currently assigned to you.',
            color=0x95a5a6,
            timestamp=datetime.now()
        )
    else:
        embed = discord.Embed(
            title=f'Your Assigned Bugs ({len(assigned_bugs)})',
            color=0x3498db,
            timestamp=datetime.now()
        )
        
        # Group by status
        for bug in assigned_bugs:
            priority_marker = '⭐ ' if bug['high_priority'] else ''
            embed.add_field(
                name=f"{priority_marker}{bug['title'][:80]}",
                value=f"**Status:** {bug['status']} • [View Thread]({bug['url']})",
                inline=False
            )
    
    embed.set_footer(text=f'Scanned all messages in #{channel.name}')
    
    await interaction.followup.send(embed=embed, ephemeral=True)

# ========================
# RUN BOT
# ========================

bot.run(os.getenv('DISCORD_TOKEN'))