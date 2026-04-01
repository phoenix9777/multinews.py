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

def check_twitter():
    # Wir nutzen jetzt eine stabilere Instanz (nitter.cz oder nitter.privacydev.net)
    base_url = "https://nitter.privacydev.net" 
    
    for account, cat in CATEGORIES.items():
        webhook_url = webhooks.get(cat)
        if not webhook_url: continue
        
        try:
            rss_url = f"{base_url}/{account}/rss"
            print(f"Checking {account} via {rss_url}...") # LOG FÜR GITHUB
            res = requests.get(rss_url, timeout=20)
            
            if res.status_code != 200:
                print(f"Fehler: Instanz {base_url} antwortet mit {res.status_code}")
                continue

            root = ET.fromstring(res.text)
            items = root.findall(".//item")
            print(f"Gefundene Posts für {account}: {len(items)}")

            for item in items[:10]:
                title = item.find("title").text if item.find("title") is not None else ""
                desc = item.find("description").text if item.find("description") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                
                # Prüfe Keywords
                keywords = FILTER_RULES.get(cat, [])
                if any(kw.lower() in title.lower() or kw.lower() in desc.lower() for kw in keywords):
                    # Bild extrahieren
                    img = ""
                    if "src=\"" in desc:
                        img = desc.split("src=\"")[1].split("\"")[0]

                    webhook = SyncWebhook.from_url(webhook_url)
                    embed = Embed(title=f"🚨 {account} Alpha", description=title[:300], url=link, color=0x00ff00)
                    if img: embed.set_image(url=img)
                    
                    webhook.send(content=f"🎯 **KING {cat.upper()} FOUND**", embed=embed)
                    print(f"Erfolg: Post für {account} gesendet!")
                    break
        except Exception as e:
            print(f"Fehler bei {account}: {e}")

if __name__ == "__main__":
    check_twitter()
