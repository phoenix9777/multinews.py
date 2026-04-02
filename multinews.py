import os, requests, json, time
import xml.etree.ElementTree as ET
from discord import SyncWebhook, Embed

# WEBHOOKS
webhooks = {
    "charts": os.getenv("WEBHOOK_LIVE_CHARTS"),
    "traders": os.getenv("WEBHOOK_TWITTER_TRADER"),
    "alerts": os.getenv("WEBHOOK_MARKET_ALERTS")
}

ACCOUNTS = {
    "whale_alert": "alerts",
    "lookonchain": "alerts",
    "cryptotony_": "traders"
}

# XCancel ist aktuell die stabilste Alternative zu Nitter
INSTANCE = "https://xcancel.com"

def check_twitter():
    # Browser-Tarnung (Headers), um den 403-Fehler zu umgehen
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    for account, cat in ACCOUNTS.items():
        webhook_url = webhooks.get(cat)
        if not webhook_url: continue
            
        try:
            url = f"{INSTANCE}/{account}/rss"
            print(f"Versuche King-Check für @{account}...")
            
            # Wir nutzen eine Session, um Cookies vorzutäuschen
            session = requests.Session()
            res = session.get(url, headers=headers, timeout=20)
            
            if res.status_code == 200:
                print(f"✅ Erfolg für {account}!")
                root = ET.fromstring(res.text)
                items = root.findall(".//item")
                
                if items:
                    latest = items[0]
                    title = latest.find("title").text
                    link = latest.find("link").text
                    
                    webhook = SyncWebhook.from_url(webhook_url)
                    webhook.send(content=f"🎯 **ALPHA FOUND**: @{account} \n{title[:200]}... \n{link}")
            else:
                print(f"❌ Fehler {res.status_code} bei {account}. (Instanz blockiert)")
                
        except Exception as e:
            print(f"⚠️ Schwerer Fehler: {e}")

if __name__ == "__main__":
    check_twitter()
