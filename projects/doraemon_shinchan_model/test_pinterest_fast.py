import requests
import re
import urllib.parse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

def fetch_pinterest_urls(char_query, count=15):
    urls = []
    # 1. Bing Pinterest index
    bing_url = f"https://www.bing.com/images/async?q=site%3apinterest.com+{urllib.parse.quote(char_query)}&first=1&count=40"
    try:
        res = requests.get(bing_url, headers=HEADERS, timeout=6)
        if res.status_code == 200:
            matches = re.findall(r'murl&quot;:&quot;(.*?)&quot;', res.text)
            for m in matches:
                if 'pinimg.com' in m and not m.endswith('.gif'):
                    # Convert to 736x or original quality
                    clean_m = re.sub(r'/[0-9]+x/', '/736x/', m)
                    urls.append(clean_m)
    except Exception as e:
        print(f"Error fetching for {char_query}: {e}")
        
    # 2. Pinterest Direct search page
    p_url = f"https://www.pinterest.com/search/pins/?q={urllib.parse.quote(char_query)}"
    try:
        res = requests.get(p_url, headers=HEADERS, timeout=6)
        if res.status_code == 200:
            matches = re.findall(r'https://i\.pinimg\.com/originals/[a-f0-9]+/[a-f0-9]+/[a-f0-9]+\.(?:jpg|png|webp)', res.text)
            matches_736 = re.findall(r'https://i\.pinimg\.com/736x/[a-f0-9]+/[a-f0-9]+/[a-f0-9]+\.(?:jpg|png|webp)', res.text)
            urls.extend(matches + matches_736)
    except Exception:
        pass
        
    unique_urls = list(dict.fromkeys(urls))
    return unique_urls[:count]

if __name__ == "__main__":
    chars = [
        "doraemon solo character",
        "nobita nobi solo character",
        "shizuka minamoto solo character",
        "takeshi goda gian solo",
        "suneo honekawa solo",
        "dorami doraemon solo",
        "shinnosuke nohara shinchan solo",
        "misae nohara shinchan solo",
        "hiroshi nohara shinchan solo",
        "himawari nohara shinchan solo",
        "shiro dog shinchan solo",
        "toru kazama shinchan solo",
        "nene sakurada shinchan solo",
        "masao sato shinchan solo",
        "bo chan shinchan solo"
    ]
    
    print("=== Testing Pinterest Image Scraper for all 15 characters ===")
    for c in chars:
        pin_urls = fetch_pinterest_urls(c, 10)
        print(f"[{c}] -> Found {len(pin_urls)} Pinterest pinimg URLs. Sample: {pin_urls[0] if pin_urls else 'None'}")
