import os
import xml.etree.ElementTree as ET
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
CUELINKS_SUBID = "telegram_bot"

def get_affiliate_link(raw_url):
    encoded_url = requests.utils.quote(raw_url)
    return f"https://links2revenue.com/?pubid=YOUR_ID&url={encoded_url}&subid={CUELINKS_SUBID}"

def check_live_deals():
    feed_urls = [
        "https://www.reddit.com/r/udemyfreebies/new/.rss",
        "https://www.reddit.com/r/googleplaydeals/new/.rss"
    ]
    
    # Using an updated 2026 browser identity to avoid Reddit blocking us
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for url in feed_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Skipping {url}: Status code {response.status_code}")
                continue
                
            # Safely parse XML data
            root = ET.fromstring(response.content)
            
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                title_node = entry.find("{http://www.w3.org/2005/Atom}title")
                if title_node is None or not title_node.text:
                    continue
                title = title_node.text
                
                link_node = entry.find("{http://www.w3.org/2005/Atom}link")
                if link_node is None:
                    continue
                raw_url = link_node.attrib.get("href")
                
                if "100% OFF" in title.upper() or "[FREE]" in title.upper():
                    affiliate_link = get_affiliate_link(raw_url)
                    
                    message = (
                        f"🔥 **LIMITED TIME 100% OFF DEAL** 🔥\n\n"
                        f"📚 **Asset:** {title}\n\n"
                        f"👇 **Claim it for 100% Free Here:**\n"
                        f"{affiliate_link}"
                    )
                    
                    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                    payload = {
                        "chat_id": TELEGRAM_CHANNEL_ID,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                    
                    tel_response = requests.post(telegram_url, json=payload, timeout=10)
                    print(f"Telegram response status: {tel_response.status_code}")

        except ET.ParseError:
            print(f"Failed to parse XML from {url} (Likely blocked by rate limit). Skipping safely.")
        except Exception as e:
            print(f"An unexpected error occurred with {url}: {e}. Keeping pipeline running.")

if __name__ == "__main__":
    check_live_deals()
