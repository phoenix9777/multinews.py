import os, requests
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
    "traders": [] # Alles erlaubt
}

# 3. ZUORDNUNG (Alle 9 Accounts integriert)
CATEGORIES = {
    # Kategorie: charts
    "Finora_EN": "charts",
    
    # Kategorie: traders
    "cryptotony_": "traders",
    "killaxbt": "traders",
    "astekz": "traders",
    "eliz883": "traders",
    "cryptobullet1": "traders",
    
    # Kategorie: alerts
    "whale_alert": "alerts",
    "lookonchain": "alerts", 
    "unusual_whales": "alerts"
}

def check_twitter():
    for account, cat in CATEGORIES.items():
        webhook_url = webhooks.get(cat)
        if not webhook_url: continue
        
        try:
            # Wir nutzen eine Nitter-Instanz für RSS (kostenlos & inkl. Bilder)
            rss_url = f"https://nitter.net/{account}/rss"
            res = requests.get(rss_url, timeout=15).text
            
            # Suche nach dem neuesten Eintrag und Bild
            if "<item>" in res:
                latest_post = res.split("<item>")[1]
                title = latest_post.split("<title>")[1].split("</title>")[0]
                link = latest_post.split("<link>")[1].split("</link>")[0]
                
                # Bild-Extraktion (Trick)
                image_url = ""
                if "src=\"" in latest_post:
                    image_url = latest_post.split("src=\"")[1].split("\"")[0]

                # Filter-Logik
                allowed_keywords = FILTER_RULES.get(cat, [])
                should_send = False
                if not allowed_keywords or any(kw.lower() in title.lower() for kw in allowed_keywords):
                    should_send = True

                if should_send:
                    webhook = SyncWebhook.from_url(webhook_url)
                    embed = Embed(title=f"Alpha von @{account}", description=title, url=link, color=0x00ff00)
                    if image_url:
                        embed.set_image(url=image_url)
                    
                    webhook.send(
                        content=f"🚀 **KING {cat.upper()} UPDATE**",
                        embed=embed,
                        username=f"KING {cat.upper()}"
                    )
        except:
            continue

if __name__ == "__main__":
    check_twitter()
