import os
import time
import requests
from pathlib import Path

# Character mapping for Danbooru tags
CHARACTER_TAGS = {
    "doraemon": "doraemon",
    "nobi_nobita": "nobi_nobita",
    "shizuka_minamoto": "minamoto_shizuka",
    "takeshi_goda_gian": "gouda_takeshi",
    "suneo_honekawa": "honekawa_suneo",
    "dorami": "dorami",
    "misae_nohara": "nohara_misae",
    "hiroshi_nohara": "nohara_hiroshi",
    "himawari_nohara": "nohara_himawari",
    "shiro_dog": "shiro_(crayon_shin-chan)",
    "toru_kazama": "kazama_tooru",
    "nene_sakurada": "sakurada_nene",
    "masao_sato": "satou_masao",
    "bo_chan": "bo-chan_(crayon_shin-chan)"
}

HEADERS = {
    'User-Agent': 'DoraemonShinchanScraper/1.0 (contact@example.com)'
}

def get_danbooru_images(tag, limit=120):
    urls = []
    # Fetch 200 per page to ensure we get enough
    for page in range(1, 3):
        api_url = f"https://danbooru.donmai.us/posts.json?tags={tag}+solo&limit=200&page={page}"
        try:
            res = requests.get(api_url, headers=HEADERS)
            if res.status_code == 200:
                posts = res.json()
                for p in posts:
                    if 'file_url' in p:
                        urls.append(p['file_url'])
                        if len(urls) >= limit:
                            return urls
            else:
                print(f"  [!] Danbooru API Error {res.status_code}")
        except Exception as e:
            print(f"  [!] Exception: {e}")
        time.sleep(1)
    return urls

def fill_dataset(base_dir="doraemon_shinchan_dataset", target_train=100, target_val=20):
    base_path = Path(base_dir)
    train_dir = base_path / 'train'
    val_dir = base_path / 'val'
    
    # Ensure all 14 characters exist
    for char_id in CHARACTER_TAGS.keys():
        (train_dir / char_id).mkdir(parents=True, exist_ok=True)
        (val_dir / char_id).mkdir(parents=True, exist_ok=True)
        
        train_imgs = list((train_dir / char_id).glob('*.*'))
        val_imgs = list((val_dir / char_id).glob('*.*'))
        
        needed_train = target_train - len(train_imgs)
        needed_val = target_val - len(val_imgs)
        
        total_needed = max(0, needed_train) + max(0, needed_val)
        
        print(f"[{char_id}] Needs {total_needed} images (Train: {needed_train}, Val: {needed_val})")
        
        if total_needed > 0:
            danbooru_tag = CHARACTER_TAGS[char_id]
            print(f"  Fetching from Danbooru for tag: {danbooru_tag}")
            urls = get_danbooru_images(danbooru_tag, limit=total_needed + 20) # buffer
            
            print(f"  Found {len(urls)} urls on Danbooru")
            
            downloaded = 0
            for i, url in enumerate(urls):
                if downloaded >= total_needed:
                    break
                
                try:
                    ext = url.split('.')[-1]
                    if ext not in ['jpg', 'png', 'jpeg', 'webp']: continue
                    
                    img_data = requests.get(url, headers=HEADERS, timeout=10).content
                    
                    if needed_train > 0:
                        save_path = train_dir / char_id / f"danbooru_{downloaded}.{ext}"
                        needed_train -= 1
                    else:
                        save_path = val_dir / char_id / f"danbooru_{downloaded}.{ext}"
                        needed_val -= 1
                        
                    with open(save_path, 'wb') as f:
                        f.write(img_data)
                        
                    downloaded += 1
                except Exception as e:
                    pass
            print(f"  Downloaded {downloaded} images.")

if __name__ == "__main__":
    fill_dataset()
