import os, requests, json, time
import xml.etree.ElementTree as ET
from discord import SyncWebhook, Embed

# 1. WEBHOOKS AUS GITHUB SECRETS
webhooks = {
    "charts": os.getenv("WEBHOOK_LIVE_CHARTS"),
    "traders": os.getenv("WEBHOOK_TWITTER_TRADER"),
    "alerts": os.getenv("WEBHOOK_MARKET_ALERTS")
}

# 2. FILTER & ACCOUNT ZUORDNUNG
CATEGORIES = {
    "Finora_EN": "charts",
    "cryptotony_": "traders",
    "killaxbt": "traders",
    "whale_alert": "alerts",
    "lookonchain": "alerts"
}

# 3. RSS-QUELLEN (Falls eine Instanz blockt, nimmt er die nächste)
RSS_INSTANCES = [
    "https://nitter.poast.org/{user}/rss",
    "https://nitter.moomoo.me/{user}/rss",
    "https://xcancel.com/{user}/rss"
]

DB_FILE = "sent_tweets.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f)

def check_twitter():
    db = load_db()
    for user, cat in CATEGORIES.items():
        webhook_url = webhooks.get(cat)
        if not webhook_url: continue
        
        success = False
        for instance in RSS_INSTANCES:
            if success: break
            try:
                url = instance.format(user=user)
                res = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
                if res.status_code == 200:
                    root = ET.fromstring(res.text)
                    items = root.findall(".//item")
                    
                    for item in reversed(items[:5]): # Von alt nach neu
                        link = item.find("link").text
                        if link in db.get(user, []): continue
                        
                        title = item.find("title").text or "Tweet ohne Text"
                        webhook = SyncWebhook.from_url(webhook_url)
                        embed = Embed(title=f"💎 Alpha @{user}", description=title[:500], url=link, color=0x1DA1F2)
                        
                        webhook.send(content=f"🎯 **KING {cat.upper()} ALERT**", embed=embed)
                        
                        if user not in db: db[user] = []
                        db[user].append(link)
                        db[user] = db[user][-50:] # Nur die letzten 50 merken
                    success = True
            except: continue
    save_db(db)

if __name__ == "__main__":
    check_twitter()
