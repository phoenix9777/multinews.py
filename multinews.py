import os, requests
from discord import SyncWebhook

# 1. WEBHOOKS AUS GITHUB SECRETS
webhooks = {
    "charts": os.getenv("WEBHOOK_LIVE_CHARTS"),
    "traders": os.getenv("WEBHOOK_TWITTER_TRADER"),
    "alerts": os.getenv("WEBHOOK_MARKET_ALERTS")
}

# 2. FILTER-REGELN PRO KATEGORIE
FILTER_RULES = {
    "charts": ["SOL", "SUI", "BTC", "ETH", "Solana", "Ethereum", "Bitcoin"],
    "alerts": ["SOL", "BTC", "Solana", "Bitcoin", "$SOL", "$BTC"],
    "traders": [] # LEER = KEIN FILTER (Alles wird gepostet)
}

# 3. ZUORDNUNG DER ACCOUNTS
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
    for account, cat in CATEGORIES.items():
        webhook_url = webhooks.get(cat)
        if not webhook_url: continue
        
        try:
            url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{account}"
            res = requests.get(url, timeout=10).text
            content_lower = res.lower()
            
            allowed_keywords = FILTER_RULES.get(cat, [])
            should_send = False
            found_kw = "ALL"

            # FILTER-LOGIK
            if not allowed_keywords:
                # Kein Filter für Trader
                should_send = True
            else:
                # Checke Keywords für Charts und Alerts
                for kw in allowed_keywords:
                    if kw.lower() in content_lower:
                        should_send = True
                        found_kw = kw.upper()
                        break
            
            if should_send:
                webhook = SyncWebhook.from_url(webhook_url)
                prefix = f"🎯 **{found_kw}**" if found_kw != "ALL" else "✍️ **TRADER ALPHA**"
                webhook.send(
                    content=f"{prefix} bei **@{account}**\nLink: https://twitter.com/{account}",
                    username=f"KING {cat.upper()}"
                )
        except:
            continue

if __name__ == "__main__":
    check_twitter()
