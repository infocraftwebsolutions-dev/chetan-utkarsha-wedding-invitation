import os
import cv2
import numpy as np

with open(r"d:\biu_app_clone_13_1_2026\biu_app\wedding_invitation\fix_3d_frames.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace build_clean_palace_stage with seamless arch-shaped feather and tight samai stem mask
old_block = """    # Replace the ENTIRE inner arch area (x=90..678, y=330..1120) so ZERO purple saree remains anywhere!
    mask = np.zeros((H, W), dtype=np.float32)
    mask[335:1115, 92:676] = 1.0
    mask = cv2.GaussianBlur(mask, (41, 41), 0)[:, :, None]

    stage_inner = stage.copy()
    stage_inner[330:1120, 90:678] = inner_backdrop
    stage = stage * (1.0 - mask) + stage_inner * mask

    # Now restore ONLY the twin glowing 3D Brass Samais (left x=60..158, y=735..1075; right x=610..705, y=735..1075)
    # masking out any purple saree pixels (purple has Hue > 115 or Blue > Green)!
    b_hsv = cv2.cvtColor(bride_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    is_brass_gold = ((b_hsv[:, :, 0] < 42) & (b_hsv[:, :, 1] > 35) & (b_hsv[:, :, 2] > 65)) | (b_hsv[:, :, 2] > 210)
    samai_zone = np.zeros((H, W), dtype=np.float32)
    samai_zone[735:1080, 58:155] = 1.0
    samai_zone[735:1080, 612:708] = 1.0
    samai_restore = cv2.GaussianBlur((is_brass_gold.astype(np.float32) * samai_zone), (9, 9), 0)[:, :, None]
    stage = stage * (1.0 - samai_restore) + bride_bgr.astype(np.float32) * samai_restore"""

new_block = """    # Seamless arch-shaped mask covering the bride in bride_bgr (x=88..680, y=330..1120) with wide 91px Gaussian feather
    yy_s, xx_s = np.mgrid[0:H, 0:W]
    in_arch_body = (xx_s > 92) & (xx_s < 676) & (yy_s > 345) & (yy_s < 1115)
    mask = cv2.GaussianBlur(in_arch_body.astype(np.float32), (91, 91), 0)[:, :, None]

    stage_inner = stage.copy()
    stage_inner[330:1120, 90:678] = inner_backdrop
    stage = stage * (1.0 - mask) + stage_inner * mask

    # Restore strictly the twin 3D Brass Samai lamps (stems at x=60..114 and x=654..710, plus top flame bowls y=735..830)
    samai_zone = np.zeros((H, W), dtype=np.float32)
    samai_zone[735:1080, 58:112] = 1.0
    samai_zone[735:830, 58:148] = 1.0
    samai_zone[735:1080, 656:710] = 1.0
    samai_zone[735:830, 622:710] = 1.0
    samai_restore = cv2.GaussianBlur(samai_zone, (13, 13), 0)[:, :, None]
    stage = stage * (1.0 - samai_restore) + bride_bgr.astype(np.float32) * samai_restore"""

assert old_block in code, "old_block not found"
code = code.replace(old_block, new_block)

with open(r"d:\biu_app_clone_13_1_2026\biu_app\wedding_invitation\fix_3d_frames.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated fix_3d_frames.py")
