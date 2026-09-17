#!/usr/bin/env python3
"""Inline every asset in ../assets into playable.template.html and write ../coin-master-playable.html.
Markers: %%ASSETS_JSON%% (png map), %%SOUNDS_JSON%% (m4a map), %%IMG_<name>%% (single data URI)."""
import base64, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
OUT = os.path.join(HERE, "..", "coin-master-playable.html")
def uri(path, mime):
    with open(path, "rb") as f: return f"data:{mime};base64," + base64.b64encode(f.read()).decode()
imgs, snds = {}, {}
for f in sorted(os.listdir(ASSETS)):
    name, ext = os.path.splitext(f)
    if ext == ".png": imgs[name] = uri(os.path.join(ASSETS, f), "image/png")
    elif ext == ".m4a": snds[name] = uri(os.path.join(ASSETS, f), "audio/mp4")
html = open(os.path.join(HERE, "playable.template.html"), encoding="utf-8").read()
html = html.replace("%%ASSETS_JSON%%", json.dumps(imgs)).replace("%%SOUNDS_JSON%%", json.dumps(snds))
html = re.sub(r"%%IMG_(\w+)%%", lambda m: imgs[m.group(1)], html)
assert "%%" not in html, "unreplaced marker"
open(OUT, "w", encoding="utf-8").write(html)
print(f"wrote {OUT} ({os.path.getsize(OUT)/1024/1024:.2f} MB, {len(imgs)} images, {len(snds)} sounds)")
