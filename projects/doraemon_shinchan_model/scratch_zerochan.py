import requests
import re
import urllib.parse

def test_zerochan():
    url = "https://www.zerochan.net/Doraemon%2CSolo?p=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    print("Status:", res.status_code)
    print("HTML Preview:", res.text[:1000])
    
    # Find static.zerochan.net links which are full resolution images
    img_urls = re.findall(r'https://static\.zerochan\.net/[^\"]+\.(?:jpg|png|jpeg)', res.text)
    
    print(f"Found {len(img_urls)} image URLs. Samples:")
    for u in list(set(img_urls))[:5]:
        print(u)

if __name__ == "__main__":
    test_zerochan()
