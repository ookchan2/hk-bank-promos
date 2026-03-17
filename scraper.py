import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

TODAY = datetime.now().strftime('%Y-%m-%d')

BANKS = {
    'za':      'https://bank.za.group/en/promotions',
    'mox':     'https://mox.com/promotions/',
    'welab':   'https://www.welab.bank/en/promotions/',
    'livi':    'https://www.livibank.com/en/promotions/',
    'airstar': 'https://www.airstarbank.com/en-hk/promotion',
    'pao':     'https://www.paob.com.hk/tc/',
    'fusion':  'https://www.fusionbank.com/?lang=zh-HK'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def extract_date(text):
    patterns = [
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+20\d{2})',
        r'(20\d{2}年\d{1,2}月\d{1,2}日)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def scrape_bank(bank_id, url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')

        for tag in soup(['nav', 'footer', 'script', 'style']):
            tag.decompose()

        selectors = [
            '.promotion-card', '.promo-card', '.promo-item',
            '.offer-card', '.offer-item', '.campaign-card',
            'article', '.card'
        ]

        cards = []
        for selector in selectors:
            cards = soup.select(selector)
            if len(cards) > 0:
                break

        promos = []
        for i, card in enumerate(cards[:10]):
            text = card.get_text(separator=' ', strip=True)
            title_tag = card.find(['h1', 'h2', 'h3', 'h4'])
            title = title_tag.get_text(strip=True) if title_tag else f'Promotion {i+1}'

            promos.append({
                'bank': bank_id,
                'name': title[:100],
                'summary': text[:200],
                'expiry': extract_date(text),
                'updated': TODAY
            })

        print(f"✅ {bank_id}: found {len(promos)} promotions")
        return promos

    except Exception as e:
        print(f"❌ {bank_id} failed: {str(e)}")
        return []

def update_html():
    try:
        with open('Bank promotion.html', 'r', encoding='utf-8') as f:
            html = f.read()

        html = re.sub(
            r'(Last updated:|最後更新：)\s*[\d\-]+',
            f'\\g<1> {TODAY}',
            html
        )

        with open('Bank promotion.html', 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ HTML updated with date: {TODAY}")

    except Exception as e:
        print(f"❌ Could not update HTML: {str(e)}")

if __name__ == '__main__':
    print(f"🚀 Starting daily update for {TODAY}")

    all_promos = []
    for bank_id, url in BANKS.items():
        promos = scrape_bank(bank_id, url)
        all_promos.extend(promos)

    with open('promos_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_promos, f, ensure_ascii=False, indent=2)

    update_html()

    print(f"\n🎉 Done! {len(all_promos)} total promotions found.")
