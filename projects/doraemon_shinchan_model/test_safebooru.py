import urllib.parse
import requests

CHAR_SAFEBOORU_TAGS = {
    "doraemon": ["doraemon+solo", "doraemon"],
    "nobi_nobita": ["nobi_nobita+solo", "nobi_nobita", "nobita+solo"],
    "shizuka_minamoto": ["minamoto_shizuka+solo", "minamoto_shizuka"],
    "takeshi_goda_gian": ["goda_takeshi+solo", "goda_takeshi"],
    "suneo_honekawa": ["honekawa_suneo+solo", "honekawa_suneo"],
    "dorami": ["dorami+solo", "dorami"],
    "shinnosuke_nohara": ["nohara_shinnosuke+solo", "nohara_shinnosuke", "crayon_shin-chan+solo"],
    "misae_nohara": ["nohara_misae+solo", "nohara_misae"],
    "hiroshi_nohara": ["nohara_hiroshi+solo", "nohara_hiroshi"],
    "himawari_nohara": ["nohara_himawari+solo", "nohara_himawari"],
    "shiro_dog": ["shiro_(crayon_shin-chan)+solo", "shiro_(crayon_shin-chan)"],
    "toru_kazama": ["kazama_tooru+solo", "kazama_tooru"],
    "nene_sakurada": ["sakurada_nene+solo", "sakurada_nene"],
    "masao_sato": ["sato_masao+solo", "sato_masao"],
    "bo_chan": ["bo-chan+solo", "bo-chan"]
}

headers = {'User-Agent': 'DoraemonShinchanScraper/1.0'}

for name, tags in CHAR_SAFEBOORU_TAGS.items():
    found = False
    for tag in tags:
        url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={urllib.parse.quote(tag)}&limit=10"
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200 and isinstance(r.json(), list) and len(r.json()) > 0:
                print(f"[{name}] Tag '{tag}' -> {len(r.json())} posts found on Safebooru")
                found = True
                break
        except Exception as e:
            pass
    if not found:
        print(f"[{name}] No direct Safebooru posts found with tags {tags}")
