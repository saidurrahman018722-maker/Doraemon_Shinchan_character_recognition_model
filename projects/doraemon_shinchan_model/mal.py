import requests
import re
r = requests.get("https://myanimelist.net/character/908/Shinnosuke_Nohara/pictures", headers={"User-Agent": "Mozilla/5.0"})
print(len(re.findall(r"https://cdn\.myanimelist\.net/images/characters/[^\"]+", r.text)))
