"""Compose all 52 card faces from the 15 real faces found in the Solitaire Grand Harvest APK.
Rank glyphs are cut out of the real cards; the 9 is a rotated 6; missing colour variants are
recoloured from the other colour. Output: ../assets/cards/<rank><suit>.png at 90x140 plus back.png."""
import os
from PIL import Image
import numpy as np
S = "../../../solitaire-apk/extracted/sprites/"
OUT = "../assets/cards"
os.makedirs(OUT, exist_ok=True)
SRC = {  # rank -> {colour: sprite}
 'A': {'r': 'cards_heart_a'}, '2': {'b': 'cards_club_2'}, '3': {'r': 'cards_diamond_3'}, '4': {'b': 'cards_club_4'},
 '5': {'r': 'cards_heart_5'}, '6': {'r': 'cards_heart_6', 'b': 'cards_spade_6'}, '7': {'b': 'cards_club_7'}, '8': {'b': 'cards_club_8'},
 '10': {'b': 'cards_spade_10'}, 'J': {'r': 'cards_diamond_j', 'b': 'cards_spade_j'}, 'Q': {'r': 'cards_diamond_q'}, 'K': {'r': 'cards_heart_k', 'b': 'cards_club_k'},
}
SUIT_SRC = {'h': 'cards_heart_5', 'd': 'cards_diamond_j', 'c': 'cards_club_2', 's': 'cards_spade_10'}
COLOUR = {'h': 'r', 'd': 'r', 'c': 'b', 's': 'b'}
def load(n): return np.array(Image.open(S + n + '.png').convert('RGBA')).astype(np.float32)
def ink_alpha(a):
    """glyph coverage: card body is near white, glyphs are red or dark."""
    mean = a[..., :3].mean(-1)
    al = np.clip((205 - mean) / 55.0, 0, 1) * (a[..., 3] / 255.0)
    return al
def cut(a, box):
    """extract glyph in region box=(x0,y0,x1,y1) as RGBA with ink alpha, return (img, (ox,oy))"""
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1]; al = ink_alpha(sub)
    ys, xs = np.where(al > 0.35)
    if len(xs) == 0: raise RuntimeError('no glyph in box')
    bx0, bx1, by0, by1 = max(0, xs.min() - 2), xs.max() + 3, max(0, ys.min() - 2), ys.max() + 3
    g = sub[by0:by1, bx0:bx1].copy(); ga = al[by0:by1, bx0:bx1]
    g[..., 3] = ga * 255
    return g, (x0 + bx0, y0 + by0)
def recolour(g, to):
    """map glyph luminance to a red or black ramp"""
    out = g.copy(); al = g[..., 3] / 255.0
    lum = g[..., :3].mean(-1)
    m = al > 0.2
    lo, hi = np.percentile(lum[m], 5), np.percentile(lum[m], 95)
    t = np.clip((lum - lo) / max(hi - lo, 1), 0, 1)[..., None]
    if to == 'r': c0, c1 = np.array([150, 12, 22]), np.array([242, 58, 62])
    else: c0, c1 = np.array([18, 36, 40]), np.array([62, 86, 92])
    out[..., :3] = c0 + (c1 - c0) * t
    return out
def paste(base, g, pos):
    x, y = pos; h, w = g.shape[:2]
    dst = base[y:y + h, x:x + w]; al = (g[..., 3:4] / 255.0)
    dst[..., :3] = dst[..., :3] * (1 - al) + g[..., :3] * al
    dst[..., 3] = np.maximum(dst[..., 3], g[..., 3])
# --- blank card from cards_heart_5: replace glyph pixels with the row's background colour
ref = load('cards_heart_5'); H, W = ref.shape[:2]
blank = ref.copy(); al = ink_alpha(ref)
from scipy.ndimage import binary_dilation
mask = binary_dilation((ref[..., :3].mean(-1) < 238) & (ref[..., 3] > 200), iterations=4)
mask[:, :10] = False; mask[:, W - 10:] = False; mask[:8, :] = False; mask[H - 8:, :] = False
for y in range(H):
    cols = np.concatenate([ref[y, 12:22], ref[y, W - 22:W - 12]])
    cols = cols[cols[:, 3] > 250]
    if len(cols) == 0: continue
    bg = cols.mean(0)
    blank[y][mask[y]] = bg
# --- cut glyphs
BIG = (8, 84, W - 8, H - 8); SMALL = (6, 6, 95, 78); SUITBOX = (95, 6, W - 6, 82)
glyph = {}
for rank, d in SRC.items():
    for col, name in d.items():
        a = load(name)
        glyph[(rank, col, 'big')] = cut(a, BIG); glyph[(rank, col, 'small')] = cut(a, SMALL)
suits = {s: cut(load(n), SUITBOX) for s, n in SUIT_SRC.items()}
# 9 = 6 rotated
for col in 'rb':
    for kind in ('big', 'small'):
        g, (ox, oy) = glyph[('6', col, kind)]
        r = np.ascontiguousarray(g[::-1, ::-1]); glyph[('9', col, kind)] = (r, (ox, oy - (10 if kind == 'big' else 2)))
# fill missing colours by recolouring
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
for rank in RANKS:
    for col in 'rb':
        for kind in ('big', 'small'):
            if (rank, col, kind) not in glyph:
                other = 'b' if col == 'r' else 'r'
                g, pos = glyph[(rank, other, kind)]; glyph[(rank, col, kind)] = (recolour(g, col), pos)
# --- compose
def save(arr, path, size=(90, 140)):
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA').resize(size, Image.LANCZOS)
    im.quantize(256, method=Image.FASTOCTREE, dither=Image.NONE).save(path, optimize=True)
for suit in 'hdcs':
    col = COLOUR[suit]
    for rank in RANKS:
        card = blank.copy()
        g, pos = glyph[(rank, col, 'big')]; 
        # centre big glyph horizontally
        paste(card, g, ((W - g.shape[1]) // 2, pos[1]))
        g, pos = glyph[(rank, col, 'small')]; paste(card, g, pos)
        g, pos = suits[suit]; paste(card, g, pos)
        save(card, f'{OUT}/{rank}{suit}.png')
save(blank, f'{OUT}/blank.png')
# card back: strip the tutorial highlight border (crop 6px in) and keep rounded alpha from blank
back = Image.open(S + 'sl_tut_card_back.png').convert('RGBA'); back = back.crop((7, 7, back.width - 7, back.height - 7)).resize((W, H), Image.LANCZOS)
b = np.array(back).astype(np.float32); b[..., 3] = np.minimum(b[..., 3], blank[..., 3])
save(b, f'{OUT}/back.png')
print('cards:', len(os.listdir(OUT)), 'size', W, H)
