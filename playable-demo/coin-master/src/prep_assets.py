"""Copy the sprites we use out of the extracted Coin Master data, resize and quantize them.
Run once: python3 prep_assets.py (uses the venv in coin-master-xapk/.venv for PIL)."""
import os, subprocess
from PIL import Image
SRC = "../../../coin-master-xapk/extracted"
OUT = "../assets"
# (output name, source sprite name, max dimension)
SPRITES = [
 ("sym_coin","Slot-Icon_coin",150),("sym_sack","Slot-Icon_Gold_sack",190),("sym_shield","Slot-Icon_shield",150),
 ("sym_spins","Slot-Icon_spins",150),("sym_hammer","Slot-Icon_attack",200),("sym_pig","Slot-Icon_steal",176),
 ("blur_coin","Slot-Icon_coin-blur",203),("blur_sack","Slot-Icon_Gold_sack_blur",230),("blur_shield","Slot-Icon_shield-blur",212),
 ("blur_spins","Slot-Icon_spins-blur",221),("blur_hammer","Slot-Icon_attack-blur",278),("blur_pig","Slot-Icon_steal-blur",230),
 ("spin_btn","Spin_Button__with_text_",362),("plate","King_BG_plate",456),("win_back","btn_back",406),("win_front","btn_front",432),
 ("hand","FTUE_hand_icon",220),("hud_coin","client_hud_coin",123),("hud_spins","spins_icon",120),("hud_shield","client_hud_shield_icon",97),
 ("shield_slot","client_hud_shieldSlot_bg",95),("build_btn","client_hud_build_icon",160),("star","client_hud_xp_bar_star",108),
 ("house1","Viking_house1",300),("house2","Viking_house2",320),("house3","Viking_house3",340),("house4","Viking_house4",360),
 ("house4_dmg","Viking_house4_damaged",360),("statue1","Viking_statue1",200),("statue4","Viking_statue4",300),("statue4_dmg","Viking_statue4_damaged",300),
 ("farm1","Viking_pumpkin1",300),("farm4","Viking_pumpkin4",320),("pig1","viking_pig1_base",200),("pig4","viking_pig4_base",320),
 ("ship4","Viking_ship4_damaged",300),
 ("hole","client_ui_improvements_raid_dig_hole",216),("dirt","client_ui_improvements_raid_dirt_patch",135),("shovel","client_ui_improvements_raid_shovel_icon",130),
 ("chest_gold","client_ui_improvements_raid_chest_golden",156),("chest_wood","client_ui_improvements_raid_chest_wooden",160),
 ("target","attackTarget",240),("hammer_big","hammer",220),("xmark","steal_target",200),
 ("clouds_back","BackClouds",512),("clouds_top","Top-clouds",256),("logo","Coin_master",428),("coin_stack","Btn_Gold",260),
 ("bubble","client_ui_improvements_ftue_main_bubble",128),("smoke","client_village_redesign_build_effect_smoke",128),("sack_big","gold_sack",300),
]
AUDIO = [("spin","slot_spin_1"),("stop1","slot_stop_1"),("stop2","slot_stop_2"),("stop3","slot_stop_3"),("coins","slot_coins_m"),
 ("hit","attack_hit"),("attack_win","attack_win"),("dig","dig"),("chest","Dug_Chest-01"),("build","item_build_end"),
 ("shield","shiled_win"),("collect","db_collect_coins"),("steal_win","steal_win"),("button","slot_button"),("nocoins","popup_no_coins")]
os.makedirs(OUT, exist_ok=True)
total=0
for out, src, mx in SPRITES:
    p=f"{SRC}/sprites/{src}.png"
    if not os.path.exists(p): p=f"{SRC}/textures/{src}.png"
    im=Image.open(p).convert("RGBA")
    bbox=im.getbbox()
    if bbox: im=im.crop(bbox)
    w,h=im.size; s=min(mx/w, mx/h, 1.0)
    if s<1: im=im.resize((round(w*s),round(h*s)), Image.LANCZOS)
    q=im.quantize(256, method=Image.FASTOCTREE, dither=Image.NONE)
    q.save(f"{OUT}/{out}.png", optimize=True)
    total+=os.path.getsize(f"{OUT}/{out}.png"); print(f"{out:12s} {im.size[0]}x{im.size[1]} {os.path.getsize(f'{OUT}/{out}.png')//1024}KB")
for out, src in AUDIO:
    subprocess.run(["afconvert","-f","m4af","-d","aac","-b","48000","-c","1",f"{SRC}/audio/{src}.wav",f"{OUT}/{out}.m4a"],check=True)
    total+=os.path.getsize(f"{OUT}/{out}.m4a"); print(f"{out:12s} audio {os.path.getsize(f'{OUT}/{out}.m4a')//1024}KB")
print("TOTAL KB:", total//1024)
