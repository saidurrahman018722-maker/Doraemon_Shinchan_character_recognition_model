import requests
import re
import urllib.parse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def get_pinterest_images(query, max_count=20):
    url = f"https://www.pinterest.com/search/pins/?q={urllib.parse.quote(query)}"
    urls = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            # Match pinimg URLs in HTML content
            matches = re.findall(r'https://i\.pinimg\.com/[0-9xXorignal/]+/([a-f0-9]+/[a-f0-9]+/[a-f0-9]+\.(?:jpg|png|webp))', r.text)
            for m in matches:
                # Convert thumbnail URLs to high-res 736x or originals
                high_res = f"https://i.pinimg.com/736x/{m}"
                urls.append(high_res)
    except Exception as e:
        print(f"Pinterest fetch error: {e}")
    return list(dict.fromkeys(urls))[:max_count]

def get_bing_pinterest_images(query, max_count=20):
    query_str = f"pinterest {query}"
    url = f"https://www.bing.com/images/async?q={urllib.parse.quote(query_str)}&first=1&count=40"
    urls = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            matches = re.findall(r'murl&quot;:&quot;(.*?)&quot;', r.text)
            for m in matches:
                if 'pinimg.com' in m and not m.endswith('.gif'):
                    # Convert to 736x high resolution
                    clean_url = re.sub(r'/[0-9]+x/', '/736x/', m)
                    urls.append(clean_url)
    except Exception as e:
        print(f"Bing Pinterest fetch error: {e}")
    return list(dict.fromkeys(urls))[:max_count]

if __name__ == "__main__":
    test_chars = ["doraemon solo character", "nobita nobi solo character", "shinnosuke nohara shinchan solo", "shizuka minamoto solo"]
    for q in test_chars:
        p_imgs = get_pinterest_images(q, 10)
        b_imgs = get_bing_pinterest_images(q, 10)
        total = list(dict.fromkeys(p_imgs + b_imgs))
        print(f"Query '{q}' -> Found {len(total)} high quality Pinterest image URLs!")
        if total:
            print(f"  Sample Pinterest URL: {total[0]}")
