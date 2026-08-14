import requests
import re

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}

def scrape_fandom(wiki_domain, category_or_page):
    # Fandom has an API we can use: /api.php?action=query&prop=imageinfo&iiprop=url...
    urls = []
    
    # 1. First get all images in a category or page
    api_url = f"https://{wiki_domain}/api.php?action=query&prop=images&titles={category_or_page}&format=json&imlimit=500"
    r = requests.get(api_url, headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_info in pages.items():
            images = page_info.get('images', [])
            for img in images:
                title = img['title']
                # Now get the URL for this image
                img_api = f"https://{wiki_domain}/api.php?action=query&prop=imageinfo&titles={title}&iiprop=url&format=json"
                r2 = requests.get(img_api, headers=HEADERS)
                if r2.status_code == 200:
                    d2 = r2.json()
                    p2 = d2.get('query', {}).get('pages', {})
                    for p_id2, p_info2 in p2.items():
                        if 'imageinfo' in p_info2:
                            urls.append(p_info2['imageinfo'][0]['url'])
                            if len(urls) >= 120: return urls
    return urls

print(f"Doraemon Fandom Images: {len(scrape_fandom('doraemon.fandom.com', 'Doraemon'))}")
print(f"Shinchan Fandom Images: {len(scrape_fandom('crayonshinchan.fandom.com', 'Shinnosuke_Nohara'))}")
