import os
import requests
from sopel import plugin
from google.cloud import translate_v2 as translate
from google.api_core.exceptions import GoogleAPIError

# Add the path to your service account JSON file here
SERVICE_ACCOUNT_PATH = '/path/to/your-service-account-file.json'

# Set the environment variable for Google Cloud authentication
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_PATH

# Initialize the Google Translate API client using the service account JSON file
try:
    translate_client = translate.Client()
except Exception as e:
    translate_client = None
    print(f"Error initializing Google Cloud Translate client: {e}")

@plugin.command('translate')
def translate_text(bot, trigger):
    """
    Translates text to the target language using Google Cloud Translation API (v2).
    Usage: .translate <target_language> <text>
    Example: .translate fr Hello, how are you?
    """
    if translate_client is None:
        bot.reply("Translation service is unavailable. Please check the bot configuration.")
        return

    args = trigger.group(2)

    if not args:
        bot.reply('Usage: .translate <target_language> <text>')
        return

    # Split the command into target language and text to translate
    parts = args.split(' ', 1)
    if len(parts) != 2:
        bot.reply('Usage: .translate <target_language> <text>')
        return

    target_language, text_to_translate = parts

    if not target_language.isalpha() or len(target_language) != 2:
        bot.reply(f"Invalid language code '{target_language}'. Please provide a valid ISO 639-1 language code (e.g., 'fr', 'en').")
        return

    try:
        # Use Google Cloud Translation API to translate the text
        result = translate_client.translate(text_to_translate, target_language=target_language)

        # Send back the translated text
        translated_text = result['translatedText']
        bot.reply(f'Translated ({target_language}): {translated_text}')
    except GoogleAPIError as api_error:
        bot.reply(f"API Error: {str(api_error)}")
    except requests.ConnectionError:
        bot.reply("Network error: Unable to reach the translation service. Please check your connection.")
    except ValueError as value_error:
        bot.reply(f"Translation error: {str(value_error)}")
    except Exception as e:
        bot.reply(f"An unexpected error occurred: {str(e)}")

@plugin.command('detectlang')
def detect_language(bot, trigger):
    """
    Detects the language of the provided text using Google Cloud Translation API.
    Usage: .detectlang <text>
    Example: .detectlang Bonjour tout le monde
    """
    if translate_client is None:
        bot.reply("Language detection service is unavailable. Please check the bot configuration.")
        return

    text_to_detect = trigger.group(2)

    if not text_to_detect:
        bot.reply('Usage: .detectlang <text>')
        return

    try:
        # Detect the language
        result = translate_client.detect_language(text_to_detect)

        # Extract the detected language and confidence
        detected_language = result['language']
        confidence = result['confidence']

        bot.reply(f'Detected Language: {detected_language} (Confidence: {confidence:.2f})')
    except GoogleAPIError as api_error:
        bot.reply(f"API Error: {str(api_error)}")
    except requests.ConnectionError:
        bot.reply("Network error: Unable to reach the language detection service. Please check your connection.")
    except ValueError as value_error:
        bot.reply(f"Language detection error: {str(value_error)}")
    except Exception as e:
        bot.reply(f"An unexpected error occurred: {str(e)}")
