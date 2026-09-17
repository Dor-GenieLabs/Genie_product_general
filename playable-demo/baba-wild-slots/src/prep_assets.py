"""Copy the sprites and sounds we use out of the extracted Baba Wild Slots data (baba-xapk/extracted),
crop, resize and quantize them into ../assets. Run: ../../../coin-master-xapk/.venv/bin/python prep_assets.py"""
import os, subprocess, tempfile
from PIL import Image
import soundfile as sf
SRC = "../../../baba-xapk/extracted"
OUT = "../assets"
os.makedirs(OUT, exist_ok=True)
def load(name):
    for d in ("sprites", "textures"):
        p = f"{SRC}/{d}/{name}.png"
        if os.path.exists(p): return Image.open(p).convert("RGBA")
    raise FileNotFoundError(name)
def save_png(im, out, mx=None, trim=True, size=None):
    if trim:
        b = im.getbbox()
        if b: im = im.crop(b)
    if size: im = im.resize(size, Image.LANCZOS)
    elif mx:
        w, h = im.size; s = min(mx / w, mx / h, 1.0)
        if s < 1: im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    q = im.quantize(256, method=Image.FASTOCTREE, dither=Image.NONE)
    q.save(f"{OUT}/{out}.png", optimize=True)
    print(f"{out:14s} {im.size[0]}x{im.size[1]} {os.path.getsize(f'{OUT}/{out}.png')//1024}KB")
def save_jpg(im, out, size, q=82):
    im = im.convert("RGB").resize(size, Image.LANCZOS); im.save(f"{OUT}/{out}.jpg", quality=q, optimize=True)
    print(f"{out:14s} {size[0]}x{size[1]} {os.path.getsize(f'{OUT}/{out}.jpg')//1024}KB")

# --- background (vertical palace from the game's slot room) ---
save_jpg(load("1128_BG_Vertical"), "bg", (720, 1217))
# --- Burning Hot cabinet pieces ---
cab = load("Laytout_Reels")                       # 1460x1483
save_png(cab.crop((195, 190, 1265, 620)), "panel", trim=False, size=(640, 257))   # ANY 5..9 sevens jackpot panel
save_png(cab.crop((130, 1095, 1330, 1460)), "deck", trim=False, size=(720, 200))  # orange leather deck
# --- symbols ---
sev = load("symbol_11_anim")                      # 10 frames of 142x140 flaming sevens
frames = [sev.crop((i * 142, 0, (i + 1) * 142, 140)).resize((120, 118), Image.LANCZOS) for i in range(10)]
sheet = Image.new("RGBA", (1200, 118)); [sheet.paste(f, (i * 120, 0)) for i, f in enumerate(frames)]
save_png(sheet, "seven_anim", trim=False)
save_png(frames[0], "sym_seven", trim=False)
wild = Image.open(f"{SRC}/textures/symbol_1_1.png").convert("RGBA"); assert wild.size == (144, 108)
save_png(wild, "sym_wild", trim=False)
for out, src, mx in [("sym_coin", "babaCoin", 120), ("sym_crown", "Crown", 108), ("sym_star", "Star_Center", 120),
                     ("sym_gem", "TeamsDiamond_Icon", 120), ("sym_crystal", "WildCrystal_Icon", 110), ("sym_chest", "GoldChest_Closed", 120)]:
    save_png(load(src), out, mx)
# --- UI ---
for out, src, mx in [("logo_bh", "BurningHotLogo", 512), ("logo_baba", "BabaWildSlotsLogo", 450), ("logo_baba_big", "BabaWildSlots_Logo", 520),
                     ("spin_btn", "Spin_Button", 273), ("spin_txt", "Spin_SpinButton", 230), ("stop_txt", "Stop_SpinButton", 230),
                     ("auto_btn", "AutoSpin_Button", 200), ("auto_txt", "Auto_AutoButton", 160), ("maxbet", "MaxBet_Icon", 130),
                     ("counter", "Counter_purple", 420), ("coin", "Coin_Icon", 78), ("bet_badge", "Badge_TotalBet", 73),
                     ("hand", "Pointer_Hand", 200), ("april", "April_HandsUp", 340), ("tony", "Tony_WithCoins", 360),
                     ("win_icon", "Win_Icon", 240), ("bigwin", "bigWinText", 560), ("megawin", "megaWinText", 600), ("babastic", "babasticWinText", 620),
                     ("jackpot_icon", "Jackpot_Icon", 240), ("rays", "Popup_Rays", 256), ("star", "Star_White", 85), ("spark", "Spark", 57),
                     ("lamp", "Lamp_on", 66), ("glow", "Glow_64x64", 64), ("coins_left", "LeftCoins", 420), ("coins_right", "RightCoins", 420),
                     ("coin_pile", "Coins09_StoreIcon", 330), ("cta_btn", "GreenButton_Big_Regular", 350), ("bubble", "TextBubble_Sliced", 105),
                     ("jp_hl", "JackpotHighlight", 57)]:
    save_png(load(src), out, mx)
# --- audio: ogg -> wav via soundfile, wav straight; afconvert -> mono AAC ---
AUDIO = [("spin", "spin2", None), ("stop", "reel_stop", None), ("win", "win", None), ("coinwin", "Coin Win1", None), ("press", "press", None),
         ("tension", "tension", None), ("bigwin", "big_win_1", None), ("winner", "we_have_a_winner", None), ("babastic", "babastic", None),
         ("jackpot", "jackpot", 5.0), ("collect", "Collected Coins 2", None), ("whoosh", "whoosh", None), ("popup", "popup_reveal", None),
         ("fanfare", "fanfare", None), ("bigwin2", "big_win", None)]
tmp = tempfile.mkdtemp()
for out, src, trim in AUDIO:
    p = f"{SRC}/audio/{src}.wav" if os.path.exists(f"{SRC}/audio/{src}.wav") else f"{SRC}/audio/{src}.ogg"
    data, sr = sf.read(p)
    if trim: data = data[: int(sr * trim)]
    wav = f"{tmp}/{out}.wav"; sf.write(wav, data, sr, subtype="PCM_16")
    subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", "-c", "1", wav, f"{OUT}/{out}.m4a"], check=True)
    print(f"{out:14s} audio {len(data)/sr:.1f}s {os.path.getsize(f'{OUT}/{out}.m4a')//1024}KB")
print("TOTAL KB:", sum(os.path.getsize(f"{OUT}/{f}") for f in os.listdir(OUT)) // 1024)
