with open(r"d:\biu_app_clone_13_1_2026\biu_app\wedding_invitation\fix_3d_frames.py", "r", encoding="utf-8") as f:
    code = f.read()

old_outdoor = """    if mode == "outdoor":
        # Strictly target ONLY green foliage (Hue 28..95, Sat > 26) so white/cream outfits & skin are NEVER touched!
        is_green = (h_ch > 27) & (h_ch < 95) & (s_ch > 26)
        # Protect center lower body / cream gown (nx in 0.25..0.82, ny > 0.30) from any false positives
        bg_prob = np.zeros((th, tw), dtype=np.float32)
        bg_prob[is_green] = 1.0"""

new_outdoor = """    if mode == "outdoor":
        # Target all green/olive foliage (Hue 22..102) including dark shaded bamboo leaves
        is_green = (h_ch > 22) & (h_ch < 102) & ((s_ch > 15) | (v_ch < 140))
        protect_gown = (nx > 0.24) & (nx < 0.82) & (ny > 0.28) & (s_ch < 34) & (v_ch > 130)
        bg_prob = np.zeros((th, tw), dtype=np.float32)
        bg_prob[is_green & (~protect_gown)] = 1.0"""

old_hands = """    elif mode == "hands":
        # For 5M5A2572.JPG: only green bokeh outside the hands & sleeves
        is_green = (h_ch > 26) & (h_ch < 95) & (s_ch > 22)
        # Protect hands and sleeves band across center
        hand_band = np.exp(-((ny - 0.50) / 0.28) ** 2)
        bg_prob = is_green.astype(np.float32) * (1.0 - hand_band * 0.75)"""

new_hands = """    elif mode == "hands":
        # For 5M5A2572.JPG: remove green/grass above and below the joined hands (ny > 0.69 or ny < 0.16)
        is_green = ((h_ch > 22) & (h_ch < 102)) | (ny > 0.69) | (ny < 0.16)
        hand_band = np.exp(-((ny - 0.45) / 0.20) ** 2) * (ny < 0.68)
        bg_prob = np.clip(is_green.astype(np.float32) * (1.0 - hand_band * 0.85) + (ny > 0.68).astype(np.float32), 0, 1)"""

old_ib = """    elif mode == "indoor_bride":
        # For 5M5A2086.JPG: remove red background text on upper right (nx > 0.63, ny < 0.46) and tint white curtain warm gold
        subj_f = subj.astype(np.float32)
        bg_zone = ((nx < 0.18) | (nx > 0.82) | (ny < 0.12) | ((nx > 0.64) & (ny < 0.48)))
        bg_prob = cv2.GaussianBlur(bg_zone.astype(np.float32), (35, 35), 0)
        fg_mask = 1.0 - bg_prob"""

new_ib = """    elif mode == "indoor_bride":
        # For 5M5A2086.JPG: remove red background text on upper left (nx < 0.36, ny < 0.38) and outer curtain
        bg_zone = ((nx < 0.18) | (nx > 0.82) | (ny < 0.12) | ((nx < 0.37) & (ny < 0.38)) | ((nx > 0.68) & (ny < 0.38)))
        bg_prob = cv2.GaussianBlur(bg_zone.astype(np.float32), (45, 45), 0)
        fg_mask = 1.0 - bg_prob"""

assert old_outdoor in code and old_hands in code and old_ib in code
code = code.replace(old_outdoor, new_outdoor).replace(old_hands, new_hands).replace(old_ib, new_ib)
with open(r"d:\biu_app_clone_13_1_2026\biu_app\wedding_invitation\fix_3d_frames.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Patched outdoor, hands, and indoor_bride modes.")
