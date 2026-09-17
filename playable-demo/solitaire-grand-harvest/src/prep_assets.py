"""Pull the non-card sprites and the sounds out of the extracted Solitaire Grand Harvest APK."""
import os, subprocess
from PIL import Image
SRC = "../../../solitaire-apk/extracted"; OUT = "../assets"
SPRITES = [  # (out, src, max side)
 ("coin", "coin_icon", 110), ("gold_stack", "gold_stack", 126), ("coin_small", "coin3", 62),
 ("streak_bar", "label_streak_facelift", 365), ("streak_cell", "mr_streak_meter_cell", 39), ("streak_x2", "mr_streak_meter_multi_x2", 74),
 ("streak_x3", "mr_streak_meter_multi_x3", 74), ("streak_glow", "glow_streak_facelift", 130), ("streak_wood", "mr_streak_meter_wood", 131),
 ("star", "sb_star_glow", 62), ("sam", "sam_on_the_box", 300), ("carrot", "carrot1", 95), ("arrow", "tutotial_playfield_arrow", 120),
 ("undo", "extras_undo", 120), ("harvest_btn", "harvest_btn_facelift_bg_ready", 180), ("cards_fan", "cards_0", 258), ("basket", "basket_0", 275),
 ("wild", "streakmeter_wild", 101),
 ("bone", "s_a_b_bonebonus_bone", 100), ("digit0", "obstacle_bomb_font_0", 40), ("digit1", "obstacle_bomb_font_1", 40), ("digit2", "obstacle_bomb_font_2", 40), ("digit3", "obstacle_bomb_font_3", 40), ("digit4", "obstacle_bomb_font_4", 40), ("digit5", "obstacle_bomb_font_5", 40), ("digit6", "obstacle_bomb_font_6", 40), ("digit7", "obstacle_bomb_font_7", 40), ("digit8", "obstacle_bomb_font_8", 40), ("digit9", "obstacle_bomb_font_9", 40), ("bone_big", "bone_0", 100), ("bone_on", "sam_b_bone_on", 92), ("bone_off", "sam_b_bone_off", 92),
 ("bowl", "sam_b_bowl", 218), ("bowl_top", "sam_b_bowl_top", 148), ("rays", "bone_bonus_rays", 235), ("check", "sam_b_sign_v", 72),
 ("bomb", "obstacle_bomb_bomb", 102), ("fuse", "obstacle_bomb_fuse", 28), ("bomb_glow", "obstacle_bomb_glow", 110), ("skull", "obstacle_bomb_skull", 54),
 ("bomb_fire", "bomb_fire_0", 160), ("bomb_spark", "bomb_sparks", 32), ("bomb_star", "bomb_stars", 59), ("bomb_lost", "level_lost_bomb", 173),
 ("card_glow", "cards_glow", 101), ("shine", "glow_star", 128), ("button_green", "button_green", 138), ("sparkle", "sparkle", 64),
]
AUDIO = [("tap1", "SFX_Universal_cardtap1"), ("tap2", "SFX_Universal_cardtap2"), ("tap3", "SFX_Universal_cardtap3"), ("tap4", "SFX_Universal_cardtap4"),
 ("flip", "SFX_Universal_cardflipstack"), ("deal", "SFX_Universal_cardflipintro"), ("miss", "SFX_Universal_missedcard"), ("win", "SFX_Universal_winsoundlastcard"),
 ("coins", "SFX_Universal_wincoinsstackcards"), ("streak", "SFX_Universal_streakmeterwincard"), ("click", "SFX_Universal_wood_button_click"),
 ("star", "SFX_Unique_get_1st_star"), ("balance", "SFX_Unique_coin_balance_1"), ("lastcard", "SFX_Unique_last_card_play"), ("reveal", "SFX_Unique_card_reveal_positive"),
 ("bark", "SFX_Unique_SamBark"), ("bark2", "SFX_Unique_dog_bark"), ("bone_fly", "SFX_Unique_bone_meter_fly"), ("bone_hit", "SFX_Unique_bone_meter_hit"),
 ("bone_fill", "SFX_Unique_bone_meter_fill"), ("bone_prize", "SFX_Unique_bone_meter_prize"), ("bowl_reveal", "SFX_Unique_sams_bowl_rewards_reveal"),
 ("tick", "SFX_Unique_suicidebomb_tick"), ("explode", "SFX_Unique_suicidebomb_explosion"), ("bomb_clear", "SFX_Unique_suicidebomb_clear"), ("sam_in", "SFX_Unique_sam_appear")]
total = 0
for out, src, mx in SPRITES:
    p = f"{SRC}/sprites/{src}.png"
    if not os.path.exists(p): p = f"{SRC}/textures/{src}.png"
    im = Image.open(p).convert("RGBA"); bb = im.getbbox(); im = im.crop(bb) if bb else im
    w, h = im.size; s = min(mx / w, mx / h, 1.0)
    if s < 1: im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    im.quantize(256, method=Image.FASTOCTREE, dither=Image.NONE).save(f"{OUT}/{out}.png", optimize=True)
    total += os.path.getsize(f"{OUT}/{out}.png"); print(f"{out:12s} {im.size[0]}x{im.size[1]} {os.path.getsize(f'{OUT}/{out}.png')//1024}KB")
# table background: opaque, crop the left half to a 9:16 portrait and save as JPEG
bg = Image.open(f"{SRC}/sprites/bg_regular_left_v1_NoAlpha.png").convert("RGB"); W, H = bg.size
cw = int(H * 720 / 1280); x0 = (W - cw) // 2
bg = bg.crop((x0, 0, x0 + cw, H)).resize((720, 1280), Image.LANCZOS); bg.save(f"{OUT}/table.jpg", quality=82, optimize=True)
total += os.path.getsize(f"{OUT}/table.jpg"); print("table.jpg", os.path.getsize(f"{OUT}/table.jpg") // 1024, "KB")
for out, src in AUDIO:
    subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", "-c", "1", f"{SRC}/audio/{src}.wav", f"{OUT}/{out}.m4a"], check=True)
    total += os.path.getsize(f"{OUT}/{out}.m4a"); print(f"{out:12s} audio {os.path.getsize(f'{OUT}/{out}.m4a')//1024}KB")
print("TOTAL KB (excl. cards):", total // 1024)
