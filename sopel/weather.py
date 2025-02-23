import os
import json
import re
import sopel.plugin
import requests
import datetime

# Replace with your actual OpenWeatherMap API key
WEATHER_API_KEY = "YOUR_API_KEY_HERE"

# File to store user registered locations
LOCATION_FILE = os.path.expanduser("~/.sopel/weather_locations.json")
user_locations = {}

def load_locations():
    global user_locations
    if os.path.exists(LOCATION_FILE):
        try:
            with open(LOCATION_FILE, "r", encoding="utf-8") as f:
                user_locations = json.load(f)
        except Exception:
            user_locations = {}
    else:
        user_locations = {}

def save_locations():
    with open(LOCATION_FILE, "w", encoding="utf-8") as f:
        json.dump(user_locations, f, ensure_ascii=False)

# Load registered locations on module load
load_locations()

def sanitize_input(text):
    """
    Sanitize the input text:
      - Remove non-ASCII characters.
      - Collapse multiple whitespace characters.
      - Strip leading/trailing spaces.
    """
    if not isinstance(text, str):
        text = str(text)
    try:
        # Remove non-ASCII characters
        sanitized = text.encode('ascii', 'ignore').decode('ascii')
    except Exception:
        sanitized = text
    return " ".join(sanitized.strip().split())

def colorize_temperature(temp_c):
    """
    Returns a string with both Celsius and Fahrenheit, color-coded by the Celsius value.
    Temperature thresholds (°C):
      < 10°C: Blue, 10–19°C: Yellow, 20–29°C: Orange, ≥ 30°C: Red.
    """
    temp_f = temp_c * 9/5 + 32
    if temp_c < 10:
        color_code = "12"  # Blue
    elif temp_c < 20:
        color_code = "08"  # Yellow
    elif temp_c < 30:
        color_code = "07"  # Orange
    else:
        color_code = "04"  # Red
    return f"\x03{color_code}{temp_c:.1f}°C ({temp_f:.1f}°F)\x03"

def wind_direction(deg):
    """
    Convert wind degrees to a rough cardinal direction (N, NE, E, SE, S, SW, W, NW).
    """
    if deg is None:
        return "?"
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    ix = round(deg / 45) % 8
    return dirs[ix]

def get_weather_emoji(weather_id):
    """
    Return a weather emoji based on the OpenWeatherMap weather condition ID.
    """
    if 200 <= weather_id <= 232:
        return "⛈️"   # Thunderstorm
    elif 300 <= weather_id <= 321:
        return "🌦️"   # Drizzle
    elif 500 <= weather_id <= 531:
        return "🌧️"   # Rain
    elif 600 <= weather_id <= 622:
        return "❄️"   # Snow
    elif 700 <= weather_id <= 781:
        return "🌫️"   # Atmosphere
    elif weather_id == 800:
        return "☀️"   # Clear
    elif weather_id == 801:
        return "🌤️"   # Few clouds
    elif weather_id == 802:
        return "⛅"    # Scattered clouds
    elif weather_id == 803:
        return "🌥️"   # Broken clouds
    elif weather_id == 804:
        return "☁️"   # Overcast
    return "🌍"        # Fallback

@sopel.plugin.command('register_location')
def register_location(bot, trigger):
    """
    Usage: !register_location <location>
    Registers your preferred location so you can use !w and !f without specifying it every time.
    """
    args = trigger.group(2)
    if not args:
        bot.say("Usage: !register_location <location>")
        return
    location = sanitize_input(args)
    nick = trigger.nick.lower()
    user_locations[nick] = location
    save_locations()
    bot.say(f"Location for {trigger.nick} registered as: {location}")

@sopel.plugin.command('change_location')
def change_location(bot, trigger):
    """
    Usage: !change_location <new location>
    Changes your registered location.
    """
    args = trigger.group(2)
    if not args:
        bot.say("Usage: !change_location <new location>")
        return
    nick = trigger.nick.lower()
    if nick not in user_locations:
        bot.say("You do not have a registered location. Use !register_location <location> to register one.")
        return
    new_location = sanitize_input(args)
    user_locations[nick] = new_location
    save_locations()
    bot.say(f"Your location has been updated to: {new_location}")

@sopel.plugin.command('unregister_location')
def unregister_location(bot, trigger):
    """
    Usage: !unregister_location
    Unregisters your preferred location.
    """
    nick = trigger.nick.lower()
    if nick in user_locations:
        del user_locations[nick]
        save_locations()
        bot.say("Your registered location has been removed.")
    else:
        bot.say("You do not have a registered location.")

@sopel.plugin.command('w')
def current_weather(bot, trigger):
    """
    Usage: !w [<location>]
    Displays current weather for the given location on one line.
    If no location is provided, uses your registered location.
    Bold labels: Location, Temperature, Pressure, Humidity, Rain, Wind, Cloud cover.
    """
    args = trigger.group(2)
    if not args:
        nick = trigger.nick.lower()
        if nick in user_locations:
            location = user_locations[nick]
        else:
            bot.say("Usage: !w <location> or register your location with !register_location <location>")
            return
    else:
        location = sanitize_input(args)
    current_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": WEATHER_API_KEY, "units": "metric"}
    try:
        r = requests.get(current_url, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        bot.say(f"Error retrieving current weather: {e}")
        return
    if data.get("cod") != 200:
        message = data.get("message", "Unknown error")
        bot.say(f"Error from OpenWeatherMap: {message}")
        return
    city = data.get("name", "Unknown location")
    country = data.get("sys", {}).get("country", "")
    weather_info = data.get("weather", [{}])[0]
    weather_id = weather_info.get("id", 800)
    conditions = weather_info.get("description", "N/A").capitalize()
    temp_c = data.get("main", {}).get("temp", 0.0)
    pressure = data.get("main", {}).get("pressure", 0)
    humidity = data.get("main", {}).get("humidity", 0)
    wind_speed_ms = data.get("wind", {}).get("speed", 0.0)
    wind_deg = data.get("wind", {}).get("deg")
    wind_dir = wind_direction(wind_deg)
    clouds = data.get("clouds", {}).get("all", 0)
    rain = data.get("rain", {}).get("1h", 0)
    # Convert wind speed: first km/h then mph
    wind_speed_kmh = wind_speed_ms * 3.6
    wind_speed_mph = wind_speed_ms * 2.23694
    color_temp = colorize_temperature(temp_c)
    weather_emoji = get_weather_emoji(weather_id)
    output = (
        f"\x02Location:\x02 {city}, {country} | "
        f"Conditions: {conditions} {weather_emoji} | "
        f"\x02Temperature:\x02 {color_temp} | "
        f"\x02Pressure:\x02 {pressure} hPa | "
        f"\x02Humidity:\x02 {humidity}% | "
        f"\x02Rain:\x02 {rain} mm | "
        f"\x02Wind:\x02 {wind_speed_kmh:.1f} km/h / {wind_speed_mph:.1f} mph from {wind_dir} | "
        f"\x02Cloud cover:\x02 {clouds}%"
    )
    bot.say(output)

@sopel.plugin.command('f')
def forecast_weather(bot, trigger):
    """
    Usage: !f [<location>]
    Displays a 4-day forecast (including today) for the given location on one line.
    If no location is provided, uses your registered location.
    For each day, it shows the weekday, a representative condition with emoji,
    plus the daily high and low temperatures.
    """
    args = trigger.group(2)
    if not args:
        nick = trigger.nick.lower()
        if nick in user_locations:
            location = user_locations[nick]
        else:
            bot.say("Usage: !f <location> or register your location with !register_location <location>")
            return
    else:
        location = sanitize_input(args)
    forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {"q": location, "appid": WEATHER_API_KEY, "units": "metric"}
    try:
        r = requests.get(forecast_url, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        bot.say(f"Error retrieving forecast: {e}")
        return
    if data.get("cod") != "200":
        message = data.get("message", "Unknown error")
        bot.say(f"Error from OpenWeatherMap: {message}")
        return
    forecast_list = data.get("list", [])
    if not forecast_list:
        bot.say("No forecast data available.")
        return
    # Group forecast items by day.
    daily = {}
    for item in forecast_list:
        dt_txt = item.get("dt_txt")
        if not dt_txt:
            continue
        dt = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
        day = dt.date()
        daily.setdefault(day, []).append(item)
    sorted_days = sorted(daily.keys())
    today = datetime.datetime.utcnow().date()
    filtered_days = [d for d in sorted_days if d >= today]
    forecast_days = filtered_days[:4]  # Include today and next 3 days
    city_name = data.get("city", {}).get("name", "Unknown location")
    country = data.get("city", {}).get("country", "")
    forecast_parts = []
    for day in forecast_days:
        items = daily[day]
        min_temp = min(item.get("main", {}).get("temp", 0.0) for item in items)
        max_temp = max(item.get("main", {}).get("temp", 0.0) for item in items)
        rep_item = min(items, key=lambda x: abs(datetime.datetime.strptime(x.get("dt_txt"), "%Y-%m-%d %H:%M:%S").hour - 12))
        condition = rep_item.get("weather", [{}])[0].get("description", "N/A").capitalize()
        weather_id = rep_item.get("weather", [{}])[0].get("id", 800)
        emoji = get_weather_emoji(weather_id)
        weekday = day.strftime("%A")
        max_temp_str = colorize_temperature(max_temp)
        min_temp_str = colorize_temperature(min_temp)
        part = f"{weekday} {condition} {emoji} {max_temp_str} {min_temp_str}"
        forecast_parts.append(part)
    forecast_str = " :: ".join(forecast_parts)
    output = f"\x02Location:\x02 {city_name}, {country} :: {forecast_str}"
    bot.say(output)
