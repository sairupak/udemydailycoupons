import os
import praw
import requests

# 1. Configuration from environment variables (Security First)
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID") # e.g., "@yourchannel"
CUELINKS_SUBID = "telegram_bot"

def get_affiliate_link(raw_url):
    """
    Wraps the raw destination link into a monetized redirect.
    Replace this with your network's automated deep-link format.
    """
    # Example for standard redirection mapping:
    encoded_url = requests.utils.quote(raw_url)
    return f"https://links2revenue.com/?pubid=YOUR_ID&url={encoded_url}&subid={CUELINKS_SUBID}"

def run_deal_engine():
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent="FreeDealEngine v3.0"
    )
    
    # Target communities for 100% off drops
    subreddits = ["udemyfreebies", "googleplaydeals"]
    
    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        for submission in subreddit.new(limit=10):
            title = submission.title
            url = submission.url
            
            # Strict Filtering Mechanism
            if "100% OFF" in title.upper() or "[FREE]" in title.upper():
                affiliate_link = get_affiliate_link(url)
                
                # Format the Telegram Alert Message
                message = (
                    f"🔥 **LIMITED TIME 100% OFF DEAL** 🔥\n\n"
                    f"📚 **Asset:** {title}\n\n"
                    f"👇 **Claim it for 100% Free Here:**\n"
                    f"{affiliate_link}"
                )
                
                # Fire to Telegram Broadcast Channel
                telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": TELEGRAM_CHANNEL_ID,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                }
                
                # Deduplication logic goes here (e.g., checking against a local txt file)
                requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    run_deal_engine()