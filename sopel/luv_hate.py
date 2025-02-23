import sopel.plugin
import time
import json
import os
import random

# File to store luv and hate points persistently
DATA_FILE = os.path.expanduser('~/.sopel/luv_hate_data.json')
CHANNEL_FILE = os.path.expanduser('~/.sopel/enabled_channels.json')

# In-memory storage for luv and hate points, last command time (cooldown), counts, and enabled channels
luv_points = {}
hate_points = {}
last_command_time = {}
luv_given_count = {}
hate_given_count = {}
enabled_channels = set()

COOLDOWN = 1800  # Default cooldown is 30 minutes (in seconds)
DECAY_TIME = 2592000  # 30 days in seconds for point decay
DAILY_CAP = 10  # Maximum number of points a user can give in a day

# Optionally, admins can be exempt from cooldown.
ADMIN_THROTTLE_EXEMPT = True

def sanitize_input(text):
    """
    Sanitizes input by removing non-ASCII characters and extra whitespace.
    This will ignore any Unicode characters.
    """
    try:
        # Remove any non-ASCII characters.
        sanitized = text.encode('ascii', 'ignore').decode('ascii')
    except Exception:
        sanitized = text
    # Collapse multiple whitespace characters and strip leading/trailing spaces.
    return " ".join(sanitized.strip().split())

# Load data from file on startup
def load_data():
    global luv_points, hate_points, luv_given_count, hate_given_count, enabled_channels
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            luv_points = data.get('luv_points', {})
            hate_points = data.get('hate_points', {})
            luv_given_count = data.get('luv_given_count', {})
            hate_given_count = data.get('hate_given_count', {})

    if os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, 'r') as f:
            enabled_channels = set(json.load(f))

# Save data to file
def save_data():
    data = {
        'luv_points': luv_points,
        'hate_points': hate_points,
        'luv_given_count': luv_given_count,
        'hate_given_count': hate_given_count
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

    with open(CHANNEL_FILE, 'w') as f:
        json.dump(list(enabled_channels), f)

# Cooldown function
def can_use_command(nick):
    current_time = time.time()
    nick = nick.lower()  # Ensure nick is handled in lowercase
    if nick in last_command_time:
        last_time = last_command_time[nick]
        if current_time - last_time < COOLDOWN:
            return False, COOLDOWN - (current_time - last_time)
    return True, 0

# Check if plugin is enabled for the channel
def is_plugin_enabled(channel):
    return channel in enabled_channels

# Command to enable the luv/hate plugin for a channel (admin only)
@sopel.plugin.command('enableluv')
@sopel.plugin.require_admin
def enable_luv_hate(bot, trigger):
    channel = trigger.sender
    if channel in enabled_channels:
        bot.say(f"Luv/Hate plugin is already enabled in {channel}.")
    else:
        enabled_channels.add(channel)
        save_data()
        bot.say(f"Luv/Hate plugin has been enabled in {channel}.")

# Command to disable the luv/hate plugin for a channel (admin only)
@sopel.plugin.command('disableluv')
@sopel.plugin.require_admin
def disable_luv_hate(bot, trigger):
    channel = trigger.sender
    if channel not in enabled_channels:
        bot.say(f"Luv/Hate plugin is already disabled in {channel}.")
    else:
        enabled_channels.remove(channel)
        save_data()
        bot.say(f"Luv/Hate plugin has been disabled in {channel}.")

# Command to give luv (works only if plugin is enabled in the channel)
@sopel.plugin.command('luv')
def luv_user(bot, trigger):
    channel = trigger.sender
    if not is_plugin_enabled(channel):
        return  # Ignore if plugin is disabled in this channel

    giver = trigger.nick.lower()  # Normalize giver nickname to lowercase
    receiver = trigger.group(2)

    if not receiver:
        bot.say("💖 You need to specify a user to give luv to. Usage: !luv <username>")
        return

    # Sanitize input: remove non-ASCII characters and extra whitespace.
    receiver = sanitize_input(receiver).lower()

    # Check if the target is on the channel
    if channel in bot.channels:
        channel_users = {user.lower() for user in bot.channels[channel].users}
        if receiver not in channel_users:
            bot.say(f"❌ User {receiver} is not on the channel.")
            return
    else:
        bot.say("❌ Channel data is not available.")
        return

    # Check cooldown unless the user is an admin and admin exemption is enabled
    if not (ADMIN_THROTTLE_EXEMPT and trigger.admin):
        can_luv, remaining = can_use_command(giver)
        if not can_luv:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            bot.notice(f"⏳ {giver}, you need to wait {minutes} minutes and {seconds} seconds before you can give luv again!", giver)
            return
        last_command_time[giver] = time.time()
    # Else: Admins with exemption bypass the cooldown check

    # Track how many times the giver has given luv
    luv_given_count[giver] = luv_given_count.get(giver, 0) + 1

    # Update luv points for the receiver
    luv_points[receiver] = luv_points.get(receiver, 0) + 1
    save_data()

    # Random response for giving luv
    response = random.choice([
        f"💖 {giver} sends warm fuzzies to {receiver}! ❤️ {receiver} now has {luv_points[receiver]} ❤️ points!",
        f"✨ {giver} shares the love with {receiver}. Now {receiver} has {luv_points[receiver]} ❤️ points!",
        f"💕 {giver} spreads kindness to {receiver}. {receiver} now has {luv_points[receiver]} ❤️ points!"
    ])
    bot.say(response)

# Command to give hate (works only if plugin is enabled in the channel)
@sopel.plugin.command('hate')
def hate_user(bot, trigger):
    channel = trigger.sender
    if not is_plugin_enabled(channel):
        return  # Ignore if plugin is disabled in this channel

    giver = trigger.nick.lower()  # Normalize giver nickname to lowercase
    receiver = trigger.group(2)

    if not receiver:
        bot.say("💔 You need to specify a user to give hate to. Usage: !hate <username>")
        return

    # Sanitize input: remove non-ASCII characters and extra whitespace.
    receiver = sanitize_input(receiver).lower()

    # Check if the target is on the channel
    if channel in bot.channels:
        channel_users = {user.lower() for user in bot.channels[channel].users}
        if receiver not in channel_users:
            bot.say(f"❌ User {receiver} is not on the channel.")
            return
    else:
        bot.say("❌ Channel data is not available.")
        return

    # Check cooldown unless the user is an admin and admin exemption is enabled
    if not (ADMIN_THROTTLE_EXEMPT and trigger.admin):
        can_hate, remaining = can_use_command(giver)
        if not can_hate:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            bot.notice(f"⏳ {giver}, you need to wait {minutes} minutes and {seconds} seconds before you can give hate again!", giver)
            return
        last_command_time[giver] = time.time()
    # Else: Admins with exemption bypass the cooldown check

    # Track how many times the giver has given hate
    hate_given_count[giver] = hate_given_count.get(giver, 0) + 1

    # Update hate points for the receiver
    hate_points[receiver] = hate_points.get(receiver, 0) + 1
    save_data()

    # Random response for giving hate
    response = random.choice([
        f"💔 {giver} throws some serious shade at {receiver}. 💢 {receiver} now has {hate_points[receiver]} 💢 points!",
        f"🔥 {giver} really isn’t feeling it with {receiver}. 💢 {receiver} now has {hate_points[receiver]} 💢 points!",
        f"😡 {giver} expresses their displeasure with {receiver}. 💢 {receiver} now has {hate_points[receiver]} 💢 points!"
    ])
    bot.say(response)

# Load data on startup
load_data()
