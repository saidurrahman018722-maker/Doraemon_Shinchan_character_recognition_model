import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

TAGS = [
    "Doraemon (Character),Solo",
    "Nobi Nobita,Solo",
    "Minamoto Shizuka,Solo",
    "Gouda Takeshi,Solo",
    "Honekawa Suneo,Solo",
    "Dorami,Solo",
    "Nohara Misae,Solo",
    "Nohara Hiroshi,Solo",
    "Nohara Himawari,Solo",
    "Shiro (Crayon Shin-chan),Solo",
    "Kazama Tooru,Solo",
    "Sakurada Nene,Solo",
    "Satou Masao,Solo",
    "Bo-chan,Solo"
]

def check(tag):
    url = f"https://www.zerochan.net/{urllib.parse.quote(tag)}?p=1"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        print(f"[{r.status_code}] {tag}")
    except Exception as e:
        print(f"[ERR] {tag}: {e}")

with ThreadPoolExecutor(max_workers=5) as ex:
    for t in TAGS:
        ex.submit(check, t)
