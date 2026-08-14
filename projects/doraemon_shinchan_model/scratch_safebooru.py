import requests

tags = [
    "doraemon_(character)", "nobi_nobita", "minamoto_shizuka", "gouda_takeshi", "honekawa_suneo", "dorami",
    "nohara_misae", "nohara_hiroshi", "nohara_himawari", "shiro_(crayon_shin-chan)", "kazama_tooru",
    "sakurada_nene", "satou_masao", "bo-chan_(crayon_shin-chan)"
]

for tag in tags:
    r = requests.get(f"https://safebooru.org/index.php?page=dapi&s=post&q=index&tags={tag}+solo&json=1")
    if r.status_code == 200:
        try:
            data = r.json()
            print(f"{tag}: {len(data)} images")
        except:
            print(f"{tag}: JSON error")
    else:
        print(f"{tag}: Error {r.status_code}")
