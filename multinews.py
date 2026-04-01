import os, requests
import xml.etree.ElementTree as ET
from discord import SyncWebhook, Embed

# 1. WEBHOOKS AUS GITHUB SECRETS
webhooks = {
    "charts": os.getenv("WEBHOOK_LIVE_CHARTS"),
    "traders": os.getenv("WEBHOOK_TWITTER_TRADER"),
    "alerts": os.getenv("WEBHOOK_MARKET_ALERTS")
}

# 2. FILTER-REGELN
FILTER_RULES = {
    "charts": ["SOL", "SUI", "BTC", "ETH", "Solana", "Ethereum", "Bitcoin"],
    "alerts": ["SOL", "BTC", "Solana", "Bitcoin", "$SOL", "$BTC"],
    "traders": ["SOL", "SUI", "BTC"] # Für den Test schalten wir SOL/SUI/BTC Filter ein
}

# 3. VOLLSTÄNDIGE ZUORDNUNG (Alle 9 Accounts)
CATEGORIES = {
    "Finora_EN": "charts",
    "cryptotony_": "traders",
    "killaxbt": "traders",
    "astekz": "traders",
    "eliz883": "traders",
    "cryptobullet1": "traders",
    "whale_alert": "alerts",
    "lookonchain": "alerts", 
    "unusual_whales": "alerts"
}

def check_twitter():
    # Wir probieren verschiedene Nitter-Instanzen, falls eine hakt
    instances = ["https://nitter.net", "https://nitter.cz", "https://nitter.it"]
    
    for account, cat in CATEGORIES.items():
        webhook_url = webhooks.get(cat)
        if not webhook_url: continue
        
        success = False
        for base_url in instances:
            if success: break
            try:
                rss_url = f"{base_url}/{account}/rss"
                res = requests.get(rss_url, timeout=15)
                if res.status_code != 200: continue
                
                root = ET.fromstring(res.text)
                items = root.findall(".//item")
                
                # Wir prüfen die letzten 10 Posts nach SOL
                for item in items[:10]:
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    desc = item.find("description").text if item.find("description") is not None else ""
                    
                    # Filter: Suchen wir nach SOL (oder den anderen Keywords)
                    allowed_keywords = FILTER_RULES.get(cat, [])
                    if any(kw.lower() in title.lower() or kw.lower() in desc.lower() for kw in allowed_keywords):
                        
                        # Bild-Suche im Description-Feld
                        image_url = ""
                        if "src=\"" in desc:
                            image_url = desc.split("src=\"")[1].split("\"")[0]

                        webhook = SyncWebhook.from_url(webhook_url)
                        embed = Embed(title=f"Alpha von @{account}", description=title[:250], url=link, color=0x00ff00)
                        if image_url:
                            embed.set_image(url=image_url)
                        
                        webhook.send(
                            content=f"🎯 **KING {cat.upper()} TEST-FOUND**",
                            embed=embed,
                            username=f"KING {cat.upper()}"
                        )
                        success = True # Ein Treffer pro Account reicht für den Test
                        break 
            except:
                continue

if __name__ == "__main__":
    check_twitter()
