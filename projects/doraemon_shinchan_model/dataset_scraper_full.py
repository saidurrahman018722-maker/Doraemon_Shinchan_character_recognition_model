import os
import re
import time
import requests
import urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET_TRAIN = 100
TARGET_VAL = 20

CHARACTER_QUERIES = {
    "doraemon": "Doraemon (Character)",
    "nobi_nobita": "Nobi Nobita",
    "shizuka_minamoto": "Minamoto Shizuka",
    "takeshi_goda_gian": "Gouda Takeshi",
    "suneo_honekawa": "Honekawa Suneo",
    "dorami": "Dorami",
    "misae_nohara": "Nohara Misae",
    "hiroshi_nohara": "Nohara Hiroshi",
    "himawari_nohara": "Nohara Himawari",
    "shiro_dog": "Shiro (Crayon Shin-chan)",
    "toru_kazama": "Kazama Tooru",
    "nene_sakurada": "Sakurada Nene",
    "masao_sato": "Satou Masao",
    "bo_chan": "Bo-chan"
}

BASE_DIR = Path(__file__).resolve().parent / "doraemon_shinchan_dataset"
TRAIN_DIR = BASE_DIR / "train"
VAL_DIR = BASE_DIR / "val"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

from bs4 import BeautifulSoup

def fetch_zerochan_urls_for_query(query, count=120, scraper=None):
    urls = []
    if not scraper:
        import requests
        scraper = requests.Session()
        scraper.headers.update(HEADERS)
    # Zerochan displays 100 images per page. (RSS might be different but we just loop)
    for page in range(1, (count // 50) + 5):
        if len(urls) >= count:
            break
            
        z_url = f"https://www.zerochan.net/{urllib.parse.quote_plus(query)}?p={page}"
        print(f"  Fetching: {z_url}", flush=True)
        try:
            res = scraper.get(z_url, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                clean_matches = []
                ul = soup.find('ul', id='thumbs2')
                if ul:
                    for a in ul.find_all('a'):
                        href = a.get('href')
                        if href and 'static.zerochan.net' in href:
                            clean_matches.append(href)
                else:
                    # fallback
                    for a in soup.find_all('a'):
                        href = a.get('href')
                        if href and 'static.zerochan.net' in href:
                            clean_matches.append(href)
                
                if not clean_matches:
                    print(f"  No images found on {z_url}", flush=True)
                    break # Reached the end of the results
                urls.extend(clean_matches)
                print(f"  Found {len(clean_matches)} images.", flush=True)
            elif res.status_code == 404:
                print(f"  404 on {z_url}", flush=True)
                break # No more pages
            else:
                print(f"  Status code: {res.status_code} on {z_url}", flush=True)
        except Exception as e:
            print(f"  Exception in fetch: {e}", flush=True)
            pass
        # Add 10 second delay to avoid Cloudflare 503 blocking
        time.sleep(10)
            
    return list(dict.fromkeys(urls))[:count]

def download_full_zerochan_dataset_for_char(char_name):
    train_char_dir = TRAIN_DIR / char_name
    val_char_dir = VAL_DIR / char_name
    train_char_dir.mkdir(parents=True, exist_ok=True)
    val_char_dir.mkdir(parents=True, exist_ok=True)
    
    # We already wiped the dataset, so existing will be 0, but keep this safe.
    existing_train = list(train_char_dir.glob("*.*"))
    existing_val = list(val_char_dir.glob("*.*"))
    
    need_train = TARGET_TRAIN - len(existing_train)
    need_val = TARGET_VAL - len(existing_val)
    total_needed = max(0, need_train) + max(0, need_val)
    
    if total_needed <= 0:
        print(f"[{char_name}] Full 200 dataset already complete.", flush=True)
        return
        
    print(f"[{char_name}] Downloading {total_needed} Zerochan solo images...", flush=True)
    
    import requests
    scraper = requests.Session()
    scraper.headers.update(HEADERS)
    query = CHARACTER_QUERIES.get(char_name, "")
    
    img_urls = fetch_zerochan_urls_for_query(query, count=total_needed + 20, scraper=scraper)
    
    curr_train_need = need_train
    curr_val_need = need_val
    img_idx = len(existing_train) + len(existing_val) + 1
    
    for img_url in img_urls:
        if curr_train_need <= 0 and curr_val_need <= 0:
            break
            
        if curr_train_need > 0:
            target_dir = train_char_dir
            prefix = "train_"
            curr_train_need -= 1
        else:
            target_dir = val_char_dir
            prefix = "val_"
            curr_val_need -= 1
            
        ext = "jpg"
        if ".png" in img_url.lower(): ext = "png"
        elif ".webp" in img_url.lower(): ext = "webp"
        
        save_path = target_dir / f"{prefix}zerochan_{char_name}_{img_idx}.{ext}"
        
        try:
            r = scraper.get(img_url, timeout=10)
            if r.status_code == 200 and len(r.content) > 2500:
                with open(save_path, 'wb') as f:
                    f.write(r.content)
                img_idx += 1
            else:
                if curr_train_need >= 0 and target_dir == train_char_dir:
                    curr_train_need += 1
                elif target_dir == val_char_dir:
                    curr_val_need += 1
        except Exception as e:
            if curr_train_need >= 0 and target_dir == train_char_dir:
                curr_train_need += 1
            elif target_dir == val_char_dir:
                curr_val_need += 1
            pass
            
    final_t = len(list(train_char_dir.glob("*.*")))
    final_v = len(list(val_char_dir.glob("*.*")))
    print(f"[{char_name}] Full Download Done -> Train: {final_t}, Val: {final_v}", flush=True)

def run_full_download():
    print("=== Downloading 200 Zerochan Images per Character ===", flush=True)
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(download_full_zerochan_dataset_for_char, c) for c in CHARACTER_QUERIES.keys()]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                print(f"Exception in thread: {e}", flush=True)
    print("\nFull 200 Zerochan dataset collection complete across all 14 characters!", flush=True)

if __name__ == "__main__":
    run_full_download()
