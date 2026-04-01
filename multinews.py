import os, requests
import xml.etree.ElementTree as ET
from discord import SyncWebhook, Embed

# 1. WEBHOOKS
webhooks = {
    "charts": os.getenv("WEBHOOK_LIVE_CHARTS"),
    "traders": os.getenv("WEBHOOK_TWITTER_TRADER"),
    "alerts": os.getenv("WEBHOOK_MARKET_ALERTS")
}

# 2. FILTER & ZUORDNUNG
FILTER_RULES = {
    "charts": ["SOL", "SUI", "BTC", "ETH"],
    "alerts": ["SOL", "BTC", "$SOL"],
    "traders": ["SOL", "SUI", "BTC"]
}

CATEGORIES = {
    "Finora_EN": "charts",
    "cryptotony_": "traders",
    "killaxbt": "traders",
    "whale_alert": "alerts",
    "lookonchain": "alerts"
}

# Liste von aktuellen Nitter-Instanzen (Backup-System)
INSTANCES = [
    "https://nitter.net",
    "https://nitter.cz",
    "https://nitter.it",
    "https://nitter.privacydev.net",
    "https://nitter.no-logs.com"
]

def check_twitter():
    for account, cat in CATEGORIES.items():
        webhook_url = webhooks.get(cat)
        if not webhook_url: continue
        
        success = False
        for base_url in INSTANCES:
            if success: break
            try:
                rss_url = f"{base_url}/{account}/rss"
                print(f"Versuche {account} via {base_url}...")
                res = requests.get(rss_url, timeout=10)
                
                if res.status_code == 200 and "<item>" in res.text:
                    root = ET.fromstring(res.text)
                    items = root.findall(".//item")
                    print(f"Erfolg! {len(items)} Posts gefunden für {account}")

                    for item in items[:5]:
                        title = item.find("title").text if item.find("title") is not None else ""
                        desc = item.find("description").text if item.find("description") is not None else ""
                        link = item.find("link").text if item.find("link") is not None else ""
                        
                        keywords = FILTER_RULES.get(cat, [])
                        if any(kw.lower() in title.lower() or kw.lower() in desc.lower() for kw in keywords):
                            img = desc.split('src="')[1].split('"')[0] if 'src="' in desc else ""
                            
                            webhook = SyncWebhook.from_url(webhook_url)
                            embed = Embed(title=f"Alpha von @{account}", description=title[:300], url=link, color=0x00ff00)
                            if img: embed.set_image(url=img)
                            
                            webhook.send(content=f"🎯 **KING {cat.upper()} FOUND**", embed=embed)
                            success = True
                            break
                else:
                    print(f"Instanz {base_url} liefert keine Daten (Status {res.status_code})")
            except Exception as e:
                print(f"Instanz {base_url} fehlgeschlagen.")
                continue

if __name__ == "__main__":
    check_twitter()
