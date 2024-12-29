import requests
from telegram.ext import Updater, CommandHandler
from config import BOT_TOKEN  # Import API key from config.py

# Proxy Scraper and Checker API URLs
PROXY_API_URL = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all"
PROXY_CHECKER_API = "https://api.proxyscrape.com/v2/?request=check&proxy={proxy}&protocol=http"

# Fetch proxies from the API
def fetch_proxies():
    try:
        response = requests.get(PROXY_API_URL)
        if response.status_code == 200:
            proxy_list = response.text.splitlines()
            return proxy_list
        else:
            return []
    except Exception as e:
        print(f"Error fetching proxies: {e}")
        return []

# Validate a proxy using Proxy Checker API
def validate_proxy(proxy):
    try:
        response = requests.get(PROXY_CHECKER_API.format(proxy=proxy))
        if response.status_code == 200:
            # Proxy is working if API returns success
            result = response.json()
            return result.get("working", False)
    except Exception as e:
        print(f"Error validating proxy: {e}")
    return False

# Telegram command: /proxies
def send_proxies(update, context):
    args = context.args
    count = int(args[0]) if args else 10  # Default 10 proxies

    update.message.reply_text("Fetching proxies...")
    proxies = fetch_proxies()

    if not proxies:
        update.message.reply_text("No proxies found.")
        return

    # Filter working proxies
    working_proxies = []
    for proxy in proxies:
        if len(working_proxies) >= count:
            break
        if validate_proxy(proxy):
            working_proxies.append(proxy)

    if working_proxies:
        update.message.reply_text(f"Found {len(working_proxies)} working proxies:\n" + "\n".join(working_proxies))
    else:
        update.message.reply_text("No working proxies found.")

# Main function to run the bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handler for /proxies
    dp.add_handler(CommandHandler("proxies", send_proxies))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
