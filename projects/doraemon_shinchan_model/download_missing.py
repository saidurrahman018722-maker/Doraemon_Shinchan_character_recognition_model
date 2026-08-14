import os
import requests
import re
from pathlib import Path

HEADERS = {'User-Agent': 'Mozilla/5.0'}

missing = {
    'masao_sato': 'Masao_Sato',
    'bo_chan': 'Bo',
    'toru_kazama': 'Toru_Kazama'
}

def download_missing():
    base_dir = Path("doraemon_shinchan_dataset")
    train_dir = base_dir / 'train'
    val_dir = base_dir / 'val'
    
    for char_id, fandom_page in missing.items():
        print(f"Fetching images for {char_id}...")
        api_url = f"https://crayonshinchan.fandom.com/api.php?action=query&prop=images&titles={fandom_page}&format=json&imlimit=500"
        r = requests.get(api_url, headers=HEADERS)
        if r.status_code != 200: continue
        
        urls = []
        data = r.json()
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_info in pages.items():
            images = page_info.get('images', [])
            for img in images:
                title = img['title']
                img_api = f"https://crayonshinchan.fandom.com/api.php?action=query&prop=imageinfo&titles={title}&iiprop=url&format=json"
                r2 = requests.get(img_api, headers=HEADERS)
                if r2.status_code == 200:
                    d2 = r2.json()
                    p2 = d2.get('query', {}).get('pages', {})
                    for p_id2, p_info2 in p2.items():
                        if 'imageinfo' in p_info2:
                            url = p_info2['imageinfo'][0]['url']
                            if url.endswith(('.jpg', '.png', '.jpeg')):
                                urls.append(url)
                if len(urls) >= 10: break
            if len(urls) >= 10: break
            
        print(f"Found {len(urls)} images for {char_id}")
        
        # Download them
        char_train_dir = train_dir / char_id
        char_val_dir = val_dir / char_id
        char_train_dir.mkdir(parents=True, exist_ok=True)
        char_val_dir.mkdir(parents=True, exist_ok=True)
        
        for i, url in enumerate(urls):
            try:
                res = requests.get(url, headers=HEADERS)
                if res.status_code == 200:
                    target_dir = char_val_dir if i < 2 else char_train_dir
                    ext = url.split('.')[-1]
                    with open(target_dir / f"{char_id}_fandom_{i}.{ext}", 'wb') as f:
                        f.write(res.content)
            except:
                pass

if __name__ == "__main__":
    download_missing()
