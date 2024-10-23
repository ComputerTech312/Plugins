import os
import time
import requests
from sopel import plugin

# Configuration
API_KEY = os.getenv('GOOGLE_API_KEY', 'Your-API-Key')
CSE_ID = os.getenv('GOOGLE_CSE_ID', 'Your-Engine-ID')
COMMAND_TRIGGER = "!google"
DEFAULT_MAX_RESULTS = 3
DEFAULT_SAFE_SEARCH = 'high'  # Options: 'off', 'medium', 'high'
MESSAGE_TYPE = 2  # 0 = notice, 1 = private message, 2 = channel message
LOGO = "\0032G\0034o\0038o\0032g\0033l\0034e\003"
SEARCH_URL = 'https://www.googleapis.com/customsearch/v1'

# Daily usage limit: 100 searches per day
USAGE_LIMIT = 100
USAGE_RESET_TIME = 86400  # 24 hours
usage_count = 0
last_reset = time.time()

# Safe search mode mapping for Google API
SAFE_SEARCH_MODES = {
    'off': 'off',
    'medium': 'medium',
    'high': 'high'
}

# Default per-user settings
user_settings = {}

def check_usage_limit():
    """Resets usage count after 24 hours."""
    global usage_count, last_reset
    current_time = time.time()
    if current_time - last_reset > USAGE_RESET_TIME:
        usage_count = 0
        last_reset = current_time

@plugin.command('google')
def google_search(bot, trigger):
    """
    Perform a Google search using Google Custom Search API.
    Usage: .google <query> [num_results] [safe_search]
    Example: .google Sopel IRC bot 3 off
    """
    global usage_count

    check_usage_limit()

    if usage_count >= USAGE_LIMIT:
        bot.reply("Daily usage limit reached (100 searches). Please wait until the next day.")
        return

    query = trigger.group(2)
    if not query:
        bot.reply(f"Usage: {COMMAND_TRIGGER} <query> [num_results] [safe_search]")
        return

    # Parse optional arguments for number of results and safe search mode
    query_parts = query.split()
    safe_search = DEFAULT_SAFE_SEARCH
    max_results = DEFAULT_MAX_RESULTS

    # Check if the user provided additional arguments (num_results and safe_search)
    if query_parts[-1] in SAFE_SEARCH_MODES:
        safe_search = query_parts.pop()  # Remove safe_search from query
    if query_parts[-1].isdigit():
        max_results = int(query_parts.pop())  # Remove num_results from query

    query = ' '.join(query_parts)

    # Limit the number of results to a reasonable max
    max_results = min(max_results, 5)  # You can adjust this limit

    if len(query) > 2048:
        bot.reply("Your search query is too long. Please shorten it.")
        return

    try:
        # Make a request to the Google Custom Search API
        params = {
            'key': API_KEY,
            'cx': CSE_ID,
            'q': query,
            'num': max_results,
            'safe': SAFE_SEARCH_MODES.get(safe_search, 'high')
        }
        response = requests.get(SEARCH_URL, params=params)
        data = response.json()

        if 'items' not in data:
            bot.reply("No results found for your search.")
            return

        # Prepare the output message based on the message type
        output = get_message_type(trigger.nick, trigger.sender)

        # Display total results and search time
        search_info = data['searchInformation']
        total_results = search_info.get('formattedTotalResults', 'N/A')
        search_time = search_info.get('formattedSearchTime', 'N/A')
        output_message = f"{LOGO} About {total_results} results ({search_time} seconds)"
        bot.say(output_message)

        # Loop through the results and display them
        for item in data['items'][:max_results]:
            title = item.get('title', 'No Title')
            link = item.get('link', 'No Link')
            snippet = item.get('snippet', 'No Snippet')
            bot.say(f"{title} / {link} / {snippet}")

        usage_count += 1

    except requests.exceptions.RequestException as e:
        bot.reply(f"An error occurred: {str(e)}")
    except Exception as e:
        bot.reply(f"An unexpected error occurred: {str(e)}")


@plugin.command('setmaxresults')
def set_max_results(bot, trigger):
    """
    Allows a user to set their preferred number of search results.
    Usage: .setmaxresults <num_results>
    Example: .setmaxresults 3
    """
    user = trigger.nick
    num_results = trigger.group(2)

    if not num_results or not num_results.isdigit():
        bot.reply("Usage: .setmaxresults <num_results>")
        return

    max_results = int(num_results)
    if max_results < 1 or max_results > 5:
        bot.reply("Please set a value between 1 and 5.")
        return

    if user not in user_settings:
        user_settings[user] = {}

    user_settings[user]['max_results'] = max_results
    bot.reply(f"Max results set to {max_results} for {user}.")


@plugin.command('setsafesearch')
def set_safe_search(bot, trigger):
    """
    Allows a user to set their preferred safe search setting.
    Usage: .setsafesearch <off|medium|high>
    Example: .setsafesearch high
    """
    user = trigger.nick
    safe_search = trigger.group(2)

    if safe_search not in SAFE_SEARCH_MODES:
        bot.reply("Usage: .setsafesearch <off|medium|high>")
        return

    if user not in user_settings:
        user_settings[user] = {}

    user_settings[user]['safe_search'] = safe_search
    bot.reply(f"Safe search set to {safe_search} for {user}.")


@plugin.command('googlesettings')
def show_settings(bot, trigger):
    """
    Shows the user's current search settings.
    Usage: .googlesettings
    """
    user = trigger.nick
    settings = user_settings.get(user, {})

    max_results = settings.get('max_results', DEFAULT_MAX_RESULTS)
    safe_search = settings.get('safe_search', DEFAULT_SAFE_SEARCH)

    bot.reply(f"{user}'s settings - Max results: {max_results}, Safe search: {safe_search}")


def get_message_type(nick, channel):
    """
    Determines the message type based on the configuration.
    0 = notice, 1 = private message, 2 = channel message.
    """
    if MESSAGE_TYPE == 0:
        return f"NOTICE {nick}"
    elif MESSAGE_TYPE == 1:
        return f"PRIVMSG {nick}"
    elif MESSAGE_TYPE == 2:
        return f"PRIVMSG {channel}"
    return f"PRIVMSG {channel}"  # Fallback to channel message
