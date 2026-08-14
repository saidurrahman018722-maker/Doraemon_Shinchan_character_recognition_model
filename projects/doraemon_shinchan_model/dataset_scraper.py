import os
import re
import requests
import urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

CHARACTER_QUERIES = {
    "doraemon": "Doraemon solo",
    "nobi_nobita": "Nobita Nobi Doraemon solo",
    "shizuka_minamoto": "Shizuka Minamoto Doraemon solo",
    "takeshi_goda_gian": "Takeshi Goda Gian Doraemon solo",
    "suneo_honekawa": "Suneo Honekawa Doraemon solo",
    "dorami": "Dorami Doraemon solo",
    "misae_nohara": "Misae Nohara Shinchan solo",
    "hiroshi_nohara": "Hiroshi Nohara Shinchan solo",
    "himawari_nohara": "Himawari Nohara Shinchan solo",
    "shiro_dog": "Shiro dog Shinchan solo",
    "toru_kazama": "Toru Kazama Shinchan solo",
    "nene_sakurada": "Nene Sakurada Shinchan solo",
    "masao_sato": "Masao Sato Shinchan solo",
    "bo_chan": "Bo chan Shinchan solo"
}

BASE_DIR = Path(__file__).resolve().parent / "doraemon_shinchan_dataset"
SAMPLE_DIR = BASE_DIR / "sample_10"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}

def fetch_pinterest_urls_for_query(query, count=20):
    urls = []
    
    # 1. Bing Pinterest Index (Primary because direct Pinterest is blocked)
    bing_url = f"https://www.bing.com/images/async?q=site%3apinterest.com+{urllib.parse.quote(query)}&first=1&count=40"
    try:
        res = requests.get(bing_url, headers=HEADERS, timeout=6)
        if res.status_code == 200:
            matches = re.findall(r'murl&quot;:&quot;(.*?)&quot;', res.text)
            for m in matches:
                if 'pinimg.com' in m and not m.endswith('.gif'):
                    # Convert thumbnails to high resolution 736x
                    clean_url = re.sub(r'/[0-9]+x/', '/736x/', m)
                    urls.append(clean_url)
    except Exception:
        pass
        
    return list(dict.fromkeys(urls))[:count]

def download_sample_images_for_char(char_name, target_count=10):
    char_dir = SAMPLE_DIR / char_name
    char_dir.mkdir(parents=True, exist_ok=True)
    
    existing = list(char_dir.glob("*.*"))
    if len(existing) >= target_count:
        print(f"[{char_name}] Already has {len(existing)} Pinterest sample images.")
        return len(existing)
        
    query = CHARACTER_QUERIES.get(char_name, f"{char_name.replace('_', ' ')} solo character pinterest")
    img_urls = fetch_pinterest_urls_for_query(query, count=25)
    
    downloaded = len(existing)
    img_idx = downloaded + 1
    
    for img_url in img_urls:
        if downloaded >= target_count:
            break
            
        ext = "jpg"
        if ".png" in img_url.lower(): ext = "png"
        elif ".webp" in img_url.lower(): ext = "webp"
        
        save_path = char_dir / f"pinterest_{char_name}_{img_idx}.{ext}"
        
        try:
            r = requests.get(img_url, headers=HEADERS, timeout=8)
            if r.status_code == 200 and len(r.content) > 2500:
                with open(save_path, 'wb') as f:
                    f.write(r.content)
                downloaded += 1
                img_idx += 1
        except Exception:
            pass
            
    print(f"[{char_name}] Downloaded {downloaded}/{target_count} Pinterest solo images.")
    return downloaded

def run_pinterest_sample_download():
    print("=== Step 1: Downloading 10 Pinterest Solo Images per Character ===")
    results = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(download_sample_images_for_char, char_name, 10): char_name for char_name in CHARACTER_QUERIES}
        for future in as_completed(futures):
            char_name = futures[future]
            try:
                count = future.result()
                results[char_name] = count
            except Exception as e:
                print(f"Error downloading Pinterest sample for {char_name}: {e}")
                results[char_name] = 0
                
    print("\nStep 1 Complete! Pinterest sample batch status:")
    for k, v in sorted(results.items()):
        print(f"  - {k}: {v}/10 Pinterest sample images")

if __name__ == "__main__":
    run_pinterest_sample_download()
