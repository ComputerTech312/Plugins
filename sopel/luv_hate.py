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

    giver = trigger.nick
    receiver = trigger.group(2)

    if not receiver:
        bot.say("💖 You need to specify a user to give luv to. Usage: !luv <username>")
        return

    can_luv, remaining = can_use_command(giver)
    if not can_luv:
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        bot.notice(f"⏳ {giver}, you need to wait {minutes} minutes and {seconds} seconds before you can give luv again!", giver)
        return

    # Track how many times the giver has given luv
    luv_given_count[giver] = luv_given_count.get(giver, 0) + 1

    # Update luv points for the receiver
    luv_points[receiver] = luv_points.get(receiver, 0) + 1
    last_command_time[giver] = time.time()
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

    giver = trigger.nick
    receiver = trigger.group(2)

    if not receiver:
        bot.say("💔 You need to specify a user to give hate to. Usage: !hate <username>")
        return

    can_hate, remaining = can_use_command(giver)
    if not can_hate:
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        bot.notice(f"⏳ {giver}, you need to wait {minutes} minutes and {seconds} seconds before you can give hate again!", giver)
        return

    # Track how many times the giver has given hate
    hate_given_count[giver] = hate_given_count.get(giver, 0) + 1

    # Update hate points for the receiver
    hate_points[receiver] = hate_points.get(receiver, 0) + 1
    last_command_time[giver] = time.time()
    save_data()

    # Random response for giving hate
    response = random.choice([
        f"💔 {giver} throws some serious shade at {receiver}. 💢 {receiver} now has {hate_points[receiver]} 💢 points!",
        f"🔥 {giver} really isn’t feeling it with {receiver}. 💢 {receiver} now has {hate_points[receiver]} 💢 points!",
        f"😡 {giver} expresses their displeasure with {receiver}. 💢 {receiver} now has {hate_points[receiver]} 💢 points!"
    ])
    bot.say(response)

# Command to show top luv leaderboard
@sopel.plugin.command('topluv')
def topluv(bot, trigger):
    channel = trigger.sender
    if not is_plugin_enabled(channel):
        return  # Ignore if plugin is disabled in this channel

    count = trigger.group(2)
    if not count or not count.isdigit():
        count = 5
    else:
        count = int(count)

    if not luv_points:
        bot.say("No one has received any 💖 yet!")
        return

    sorted_luv = sorted(luv_points.items(), key=lambda x: x[1], reverse=True)[:count]
    luv_list = " | ".join([f"💖 {user}: {points} points" for user, points in sorted_luv])
    bot.say(f"✨ Top {count} users with the most 💖: {luv_list}")

# Command to show top hate leaderboard
@sopel.plugin.command('tophate')
def tophate(bot, trigger):
    channel = trigger.sender
    if not is_plugin_enabled(channel):
        return  # Ignore if plugin is disabled in this channel

    count = trigger.group(2)
    if not count or not count.isdigit():
        count = 5
    else:
        count = int(count)

    if not hate_points:
        bot.say("No one has received any 💢 yet!")
        return

    sorted_hate = sorted(hate_points.items(), key=lambda x: x[1], reverse=True)[:count]
    hate_list = " | ".join([f"💢 {user}: {points} points" for user, points in sorted_hate])
    bot.say(f"🔥 Top {count} users with the most 💢: {hate_list}")

# Load data on startup
load_data()
