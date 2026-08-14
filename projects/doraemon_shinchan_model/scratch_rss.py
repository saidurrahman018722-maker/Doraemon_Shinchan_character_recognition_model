import requests
import re
r = requests.get("https://www.zerochan.net/Doraemon+%28Character%29%2CSolo?p=1&xml", headers={"User-Agent": "Mozilla/5.0"})
print(re.findall(r"https://static\.zerochan\.net/[^\"]+\.(?:jpg|png|jpeg)", r.text)[:10])
print(re.findall(r"https://s[0-9]\.zerochan\.net/[^\"]+\.jpg", r.text)[:10])
