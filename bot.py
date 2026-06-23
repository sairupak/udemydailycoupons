import os
import xml.etree.ElementTree as ET
import requests
import re

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
CUELINKS_SUBID = "telegram_bot"

def get_affiliate_link(raw_url):
    # Trims out tracking junk from raw source url and builds your monetization hop link
    clean_url = raw_url.split('?')[0] if '?' in raw_url else raw_url
    encoded_url = requests.utils.quote(clean_url)
    return f"https://links2revenue.com/?pubid=YOUR_ID&url={encoded_url}&subid={CUELINKS_SUBID}"

def check_live_deals():
    # Direct Developer & Coupon RSS Hubs (No 429 blocks)
    feed_urls = [
        "https://feeds.feedburner.com/OnlineCourses24", 
        "https://www.tutorialbar.com/feed/",
        "https://freebieshopes.com/feed"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for url in feed_urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Skipping feed: {url} due to code {response.status_code}")
                continue
            
            root = ET.fromstring(response.content)
            
            # Standard WordPress/Website RSS formats use '<item>' instead of '<entry>'
            items = root.findall(".//item")
            print(f"Processing {len(items)} deals from {url}...")
            
            for item in items[:7]: # Scan the freshest 7 deals per run
                title = item.find("title").text
                raw_link = item.find("link").text
                
                # Broaden filtering to match any high-value free course or app giveaway
                if any(x in title.upper() for x in ["100% OFF", "FREE", "COUPON", "GIVEAWAY"]):
                    affiliate_link = get_affiliate_link(raw_link)
                    
                    message = (
                        f"🔥 **LIMITED TIME 100% FREE DROP** 🔥\n\n"
                        f"📚 **Deal:** {title}\n\n"
                        f"👇 **Claim Your Access Instantly Here:**\n"
                        f"{affiliate_link}"
                    )
                    
                    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                    payload = {
                        "chat_id": TELEGRAM_CHANNEL_ID,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                    
                    tel_res = requests.post(telegram_url, json=payload, timeout=10)
                    print(f"Telegram Broadcast Status: {tel_res.status_code} for {title[:30]}")

        except ET.ParseError:
            print(f"XML parsing variation on {url}. Skipping safely.")
        except Exception as e:
            print(f"Error checking {url}: {e}")

if __name__ == "__main__":
    check_live_deals()
