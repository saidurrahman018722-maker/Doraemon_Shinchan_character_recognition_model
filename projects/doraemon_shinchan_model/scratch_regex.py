import re
html = open('zerochan_test.html', 'r', encoding='utf-8').read()
m3 = re.findall(r'src="(https://s[0-9]\.zerochan\.net/[^\"]+\.(?:jpg|png|webp))"', html)
print(f"Thumbnails: {len(m3)}")
print(m3[:5])
