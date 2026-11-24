import os
import cv2
import numpy as np
from PIL import Image, ImageOps

BRAIN_DIR = r"C:\Users\Asus\.gemini\antigravity\brain\41d6c376-34ae-4c6b-a1e5-025b91ae9ffa"
PREVIEW_DIR = os.path.join(BRAIN_DIR, "scratch", "previews")
OUT_DIR = r"d:\biu_app_clone_13_1_2026\biu_app\wedding_invitation\assets"

DOOR_3D_PATH = os.path.join(BRAIN_DIR, "scene_1a_unlit_door_samai_1795073477628.jpg")
BRIDE_3D_PATH = os.path.join(BRAIN_DIR, "bride_royal_jharokha_3d_1795073496764.jpg")
GROOM_3D_PATH = os.path.join(BRAIN_DIR, "groom_royal_jharokha_3d_1795073528118.jpg")

door_bgr = cv2.imread(DOOR_3D_PATH)
bride_bgr = cv2.imread(BRIDE_3D_PATH)
groom_bgr = cv2.imread(GROOM_3D_PATH)
H, W = door_bgr.shape[:2]

marigold_1 = cv2.imread(os.path.join(OUT_DIR, "petal_marigold_3d_1.png"), cv2.IMREAD_UNCHANGED)
marigold_2 = cv2.imread(os.path.join(OUT_DIR, "petal_marigold_3d_2.png"), cv2.IMREAD_UNCHANGED)
marigold_3 = cv2.imread(os.path.join(OUT_DIR, "petal_marigold_3d_3.png"), cv2.IMREAD_UNCHANGED)
rose_1 = cv2.imread(os.path.join(OUT_DIR, "petal_rose_3d_1.png"), cv2.IMREAD_UNCHANGED)
rose_2 = cv2.imread(os.path.join(OUT_DIR, "petal_rose_3d_2.png"), cv2.IMREAD_UNCHANGED)
lantern_rgba = cv2.imread(os.path.join(OUT_DIR, "lantern_gold_3d.png"), cv2.IMREAD_UNCHANGED)
door_lit_1 = cv2.imread(os.path.join(OUT_DIR, "scene1_door_lit_1.jpg"))
left_door_crop = cv2.imread(os.path.join(OUT_DIR, "door_left_panel.jpg"))
right_door_crop = cv2.imread(os.path.join(OUT_DIR, "door_right_panel.jpg"))

def overlay_rgba_sprite(bg_bgr, fg_rgba, px, py, scale=1.0, rot=0.0, opacity=0.95):
    fh, fw = fg_rgba.shape[:2]
    nw, nh = max(4, int(fw * scale)), max(4, int(fh * scale))
    resized = cv2.resize(fg_rgba, (nw, nh), interpolation=cv2.INTER_AREA)
    if rot != 0:
        M = cv2.getRotationMatrix2D((nw / 2.0, nh / 2.0), rot, 1.0)
        resized = cv2.warpAffine(resized, M, (nw, nh), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    x1, y1 = int(px - nw // 2), int(py - nh // 2)
    x2, y2 = x1 + nw, y1 + nh
    bx1, by1 = max(0, x1), max(0, y1)
    bx2, by2 = min(W, x2), min(H, y2)
    if bx2 <= bx1 or by2 <= by1:
        return
    fx1, fy1 = bx1 - x1, by1 - y1
    fx2, fy2 = fx1 + (bx2 - bx1), fy1 + (by2 - by1)
    alpha = (resized[fy1:fy2, fx1:fx2, 3:4].astype(np.float32) / 255.0) * opacity
    bg_bgr[by1:by2, bx1:bx2] = (
        bg_bgr[by1:by2, bx1:bx2].astype(np.float32) * (1.0 - alpha)
        + resized[fy1:fy2, fx1:fx2, :3].astype(np.float32) * alpha
    ).astype(np.uint8)

# ---------------------------------------------------------
# 1. CLEAN 100% ARTIFACT-FREE 3D GOLDEN PALACE STAGE
# ---------------------------------------------------------
def build_clean_palace_stage(theme="haldi"):
    stage = bride_bgr.copy().astype(np.float32)

    # Pure unoccluded 3D golden sunlight vault in bride_bgr is y=195..340, x=215..555!
    # Left & right background sandstone colonnade in bride_bgr is y=340..560, x=85..220 and x=548..683.
    vault_top = bride_bgr[195:340, 215:555].copy()
    vault_fill = cv2.resize(vault_top, (588, 790), interpolation=cv2.INTER_CUBIC)
    vault_fill = cv2.GaussianBlur(vault_fill, (45, 45), 0).astype(np.float32)

    # Add subtle vertical palace jali texture from the upper arch of groom_bgr (y=155..265, x=230..538 - strictly ABOVE groom's hat!)
    jali_clean = groom_bgr[155:265, 230:538].copy()
    jali_fill = cv2.resize(jali_clean, (588, 790), interpolation=cv2.INTER_CUBIC)
    jali_fill = cv2.GaussianBlur(jali_fill, (31, 31), 0).astype(np.float32)

    inner_backdrop = vault_fill * 0.65 + jali_fill * 0.35

    # Seamless arch-shaped mask covering the bride in bride_bgr (x=88..680, y=330..1120) with wide 91px Gaussian feather
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
    stage = stage * (1.0 - samai_restore) + bride_bgr.astype(np.float32) * samai_restore

    # Place the 3D Carved Sandstone & Gold Jali Balustrade from groom_bgr at the bottom (y=1075..1376)
    balustrade = groom_bgr[1075:1376, :].copy().astype(np.float32)
    b_mask = np.zeros((H, W), dtype=np.float32)
    b_mask[1095:1376, :] = 1.0
    b_mask = cv2.GaussianBlur(b_mask, (35, 35), 0)[:, :, None]
    stage_b = stage.copy()
    stage_b[1075:1376, :] = balustrade
    stage = stage * (1.0 - b_mask) + stage_b * b_mask

    # Add 3D Hanging Golden Palace Lanterns on left & right
    for lx1, ly1, lx2, ly2 in [(142, 190, 215, 425), (545, 175, 612, 360)]:
        l_patch = groom_bgr[ly1:ly2, lx1:lx2].astype(np.float32)
        lh, lw = l_patch.shape[:2]
        yy, xx = np.mgrid[0:lh, 0:lw]
        w = ((np.sin(np.pi * xx / lw) ** 0.7) * (np.sin(np.pi * yy / lh) ** 0.7))[:, :, None]
        stage[ly1:ly2, lx1:lx2] = stage[ly1:ly2, lx1:lx2] * (1.0 - w) + l_patch * w

    if theme == "haldi":
        stage[:, :, 0] *= 0.80
        stage[:, :, 1] *= 1.06
        stage[:, :, 2] *= 1.15
    elif theme == "wedding":
        stage[:, :, 0] *= 0.86
        stage[:, :, 1] *= 0.96
        stage[:, :, 2] *= 1.14
    elif theme == "sanctum":
        stage[:, :, 0] *= 0.82
        stage[:, :, 1] *= 1.04
        stage[:, :, 2] *= 1.16

    return np.clip(stage, 0, 255).astype(np.uint8), samai_restore

stage_haldi, samai_mask_3 = build_clean_palace_stage("haldi")
stage_wedding, _ = build_clean_palace_stage("wedding")
stage_sanctum, _ = build_clean_palace_stage("sanctum")

# Build clean Foreground 3D Architectural Portal Mask (Strictly outer pillars, top arch curve, twin brass samais, and bottom balustrade)
portal_mask = np.zeros((H, W), dtype=np.float32)
portal_mask[:, :88] = 1.0
portal_mask[:, 680:] = 1.0
yy, xx = np.mgrid[0:H, 0:W]
arch_dx = (xx - 384.0) / 312.0
arch_dy = (yy - 360.0) / 245.0
arch_rad = np.sqrt(arch_dx ** 2 + arch_dy ** 2)
portal_mask[(yy < 360) & (arch_rad > 0.93)] = 1.0
portal_mask[:142, :] = 1.0
portal_mask[1150:, :] = 1.0
portal_mask = cv2.GaussianBlur(portal_mask, (29, 29), 0)
portal_mask = np.maximum(portal_mask, samai_mask_3[:, :, 0])

print("Rebuilt 100% clean 3D Palace Stages.")


def load_upright_bgr(rel_path):
    full_path = os.path.join(PREVIEW_DIR, rel_path)
    pil_im = ImageOps.exif_transpose(Image.open(full_path)).convert("RGB")
    return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

def composite_clean_3d(
    src_bgr,
    stage_bgr,
    crop_box,
    dest_box,
    mode="outdoor",
    theme="haldi",
    variant=0
):
    sh, sw = src_bgr.shape[:2]
    cx1, cy1 = int(crop_box[0] * sw), int(crop_box[1] * sh)
    cx2, cy2 = int(crop_box[2] * sw), int(crop_box[3] * sh)
    cropped = src_bgr[cy1:cy2, cx1:cx2].copy()

    dx1, dy1, dx2, dy2 = dest_box
    tw, th = dx2 - dx1, dy2 - dy1
    subj = cv2.resize(cropped, (tw, th), interpolation=cv2.INTER_CUBIC)

    hsv = cv2.cvtColor(subj, cv2.COLOR_BGR2HSV).astype(np.float32)
    h_ch, s_ch, v_ch = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    yy, xx = np.mgrid[0:th, 0:tw]
    nx = xx / float(tw)
    ny = yy / float(th)

    if mode == "outdoor":
        # Target all green/olive foliage (Hue 22..102) including dark shaded bamboo leaves
        is_green = (h_ch > 22) & (h_ch < 102) & ((s_ch > 15) | (v_ch < 140))
        protect_gown = (nx > 0.24) & (nx < 0.82) & (ny > 0.28) & (s_ch < 34) & (v_ch > 130)
        bg_prob = np.zeros((th, tw), dtype=np.float32)
        bg_prob[is_green & (~protect_gown)] = 1.0

        # Despill green channel on all green-ish pixels so hair/shoulder edges turn warm golden amber
        green_zone = (h_ch > 25) & (h_ch < 96)
        subj_f = subj.astype(np.float32)
        excess_g = np.maximum(0.0, subj_f[:, :, 1] - subj_f[:, :, 2] * 0.84)
        subj_f[:, :, 1] = np.where(green_zone, subj_f[:, :, 1] - excess_g * 0.80, subj_f[:, :, 1])
        subj_f[:, :, 2] = np.where(green_zone, np.minimum(255.0, subj_f[:, :, 2] + excess_g * 0.60), subj_f[:, :, 2])
        subj_f[:, :, 0] = np.where(green_zone, subj_f[:, :, 0] * 0.72, subj_f[:, :, 0])
        subj = np.clip(subj_f, 0, 255).astype(np.uint8)
        fg_mask = 1.0 - cv2.GaussianBlur(bg_prob, (21, 21), 0)

    elif mode == "hands":
        # For 5M5A2572.JPG: remove green/grass above and below the joined hands (ny > 0.69 or ny < 0.16)
        is_green = ((h_ch > 22) & (h_ch < 102)) | (ny > 0.69) | (ny < 0.16)
        hand_band = np.exp(-((ny - 0.45) / 0.20) ** 2) * (ny < 0.68)
        bg_prob = np.clip(is_green.astype(np.float32) * (1.0 - hand_band * 0.85) + (ny > 0.68).astype(np.float32), 0, 1)
        green_zone = (h_ch > 25) & (h_ch < 96)
        subj_f = subj.astype(np.float32)
        excess_g = np.maximum(0.0, subj_f[:, :, 1] - subj_f[:, :, 2] * 0.84)
        subj_f[:, :, 1] = np.where(green_zone, subj_f[:, :, 1] - excess_g * 0.85, subj_f[:, :, 1])
        subj_f[:, :, 2] = np.where(green_zone, np.minimum(255.0, subj_f[:, :, 2] + excess_g * 0.65), subj_f[:, :, 2])
        subj_f[:, :, 0] = np.where(green_zone, subj_f[:, :, 0] * 0.70, subj_f[:, :, 0])
        subj = np.clip(subj_f, 0, 255).astype(np.uint8)
        fg_mask = 1.0 - cv2.GaussianBlur(bg_prob, (31, 31), 0)

    elif mode == "indoor_couple":
        # For 5M5A2280 (1).JPG:
        # First, inpaint the red curtain letters behind them (nx in 0.36..0.64, ny in 0.14..0.50) into soft warm golden curtain glow
        subj_f = subj.astype(np.float32)
        letter_zone = (nx > 0.35) & (nx < 0.64) & (ny > 0.12) & (ny < 0.52)
        is_red_letter = letter_zone & (s_ch > 38) & ((h_ch < 18) | (h_ch > 160))
        # Replace red curtain letters with warm golden backdrop color
        red_mask = cv2.GaussianBlur(is_red_letter.astype(np.float32), (25, 25), 0)[:, :, None]
        red_mask = np.clip(red_mask * 2.2, 0, 1)
        warm_curtain = cv2.GaussianBlur(subj_f, (55, 55), 0)
        warm_curtain[:, :, 0] = 140.0
        warm_curtain[:, :, 1] = 205.0
        warm_curtain[:, :, 2] = 248.0
        subj_f = subj_f * (1.0 - red_mask) + warm_curtain * red_mask

        # Tint bright white curtain into warm golden palace sunlight so it harmonizes with the 3D golden arch!
        curtain_whiteness = np.clip((v_ch - 165.0) / 85.0, 0, 1) * np.clip((55.0 - s_ch) / 55.0, 0, 1)
        cw = cv2.GaussianBlur(curtain_whiteness, (21, 21), 0)[:, :, None]
        gold_tint = np.zeros_like(subj_f)
        gold_tint[:, :, 0] = 115.0
        gold_tint[:, :, 1] = 195.0
        gold_tint[:, :, 2] = 248.0
        subj_f = subj_f * (1.0 - cw * 0.65) + gold_tint * (cw * 0.65)
        subj = np.clip(subj_f, 0, 255).astype(np.uint8)

        # Smoothly fade only the upper gap above their hands (nx in 0.38..0.58, ny < 0.56) and top floral border (ny < 0.16)
        gap_fade = np.exp(-((nx - 0.48) / 0.10) ** 2) * np.clip((0.58 - ny) * 3.0, 0, 1) * 0.82
        top_fade = np.clip((0.18 - ny) * 5.0, 0, 1)
        fg_mask = np.clip(1.0 - np.maximum(gap_fade, top_fade), 0, 1)
        fg_mask = cv2.GaussianBlur(fg_mask, (35, 35), 0)

    elif mode == "indoor_bride":
        # For 5M5A2086.JPG: remove red background text on upper left (nx < 0.36, ny < 0.38) and outer curtain
        bg_zone = ((nx < 0.18) | (nx > 0.82) | (ny < 0.12) | ((nx < 0.37) & (ny < 0.38)) | ((nx > 0.68) & (ny < 0.38)))
        bg_prob = cv2.GaussianBlur(bg_zone.astype(np.float32), (45, 45), 0)
        fg_mask = 1.0 - bg_prob

    # Arch-shaped soft vignette around subject box
    arch_x = (nx - 0.5) / 0.47
    arch_y = (ny - 0.52) / 0.48
    arch_falloff = np.clip((1.0 - (arch_x ** 4 + arch_y ** 4)) * 2.4, 0, 1)
    fg_mask = cv2.GaussianBlur(fg_mask * arch_falloff, (29, 29), 0)

    # 3D Golden Rim-Lighting
    subj_f = subj.astype(np.float32)
    edge_grad = cv2.GaussianBlur(fg_mask, (5, 5), 0) - cv2.GaussianBlur(fg_mask, (33, 33), 0)
    rim_light = np.clip(edge_grad * 2.2, 0, 1)[:, :, None]

    if theme == "haldi":
        subj_f[:, :, 0] = subj_f[:, :, 0] * 0.93 + rim_light[:, :, 0] * 45.0
        subj_f[:, :, 1] = subj_f[:, :, 1] * 1.02 + rim_light[:, :, 0] * 175.0
        subj_f[:, :, 2] = subj_f[:, :, 2] * 1.06 + rim_light[:, :, 0] * 245.0
    else:
        subj_f[:, :, 0] = subj_f[:, :, 0] * 0.95 + rim_light[:, :, 0] * 50.0
        subj_f[:, :, 1] = subj_f[:, :, 1] * 1.01 + rim_light[:, :, 0] * 165.0
        subj_f[:, :, 2] = subj_f[:, :, 2] * 1.05 + rim_light[:, :, 0] * 238.0

    subj_relit = np.clip(subj_f, 0, 255)

    # Composite onto clean 3D Palace Stage
    canvas = stage_bgr.copy().astype(np.float32)
    alpha_3 = fg_mask[:, :, None]
    roi = canvas[dy1:dy2, dx1:dx2]
    canvas[dy1:dy2, dx1:dx2] = roi * (1.0 - alpha_3) + subj_relit * alpha_3

    # Layer Foreground 3D Architectural Portal (Carved Golden Arch, Twin Brass Samais, Bottom Jali Balustrade)
    p_alpha = portal_mask[:, :, None]
    canvas = canvas * (1.0 - p_alpha) + stage_bgr.astype(np.float32) * p_alpha

    # Volumetric 3D God-Rays streaming from top arch
    gy, gx = np.mgrid[0:H, 0:W]
    gdx = (gx - 384.0) / float(W)
    gdy = (gy - 160.0) / float(H)
    gdist = np.sqrt(gdx * gdx + gdy * gdy) + 1e-4
    gangle = np.arctan2(gdy, gdx)
    beams = (0.5 + 0.5 * np.sin(gangle * 16.0 + variant * 1.2)) * np.exp(-gdist * 1.85) * (gy > 160) * (gy < 980)

    if theme == "haldi":
        haldi_mist = np.exp(-((gy - 1010.0) / 230.0) ** 2) * (0.4 + 0.3 * np.sin(gx / 95.0 + variant))
        total_glow = beams * 0.24 + haldi_mist * 0.14
        canvas[:, :, 0] += total_glow * 30.0
        canvas[:, :, 1] += total_glow * 180.0
        canvas[:, :, 2] += total_glow * 255.0
    else:
        total_glow = beams * 0.22
        canvas[:, :, 0] += total_glow * 40.0
        canvas[:, :, 1] += total_glow * 155.0
        canvas[:, :, 2] += total_glow * 240.0

    canvas = np.clip(canvas, 0, 255).astype(np.uint8)

    if theme == "haldi":
        overlay_rgba_sprite(canvas, marigold_1, 128 + variant * 20, 410 + variant * 15, 0.82, variant * 20, 0.92)
        overlay_rgba_sprite(canvas, marigold_3, 640 - variant * 18, 460 + variant * 18, 0.76, -variant * 25, 0.92)
        overlay_rgba_sprite(canvas, marigold_2, 142 + variant * 15, 1085 - variant * 15, 1.0, variant * 15, 0.94)
        overlay_rgba_sprite(canvas, marigold_1, 622 - variant * 15, 1110 - variant * 12, 0.92, -variant * 18, 0.94)
    else:
        overlay_rgba_sprite(canvas, lantern_rgba, 175 + variant * 8, 272 + variant * 6, 0.92, 0, 0.92)
        overlay_rgba_sprite(canvas, lantern_rgba, 595 - variant * 8, 265 + variant * 6, 0.90, 0, 0.92)
        overlay_rgba_sprite(canvas, rose_1, 138 + variant * 18, 1115 - variant * 12, 0.88, variant * 20, 0.92)
        overlay_rgba_sprite(canvas, marigold_1, 625 - variant * 18, 1105 - variant * 12, 0.86, -variant * 15, 0.92)

    return canvas

# Regenerate Bride 2 & Groom 2
bride_src_2 = load_upright_bgr(os.path.join("only_bride", "5M5A2086.JPG"))
bride_3d_2 = composite_clean_3d(bride_src_2, stage_haldi, (0.06, 0.14, 0.94, 0.96), (92, 285, 676, 1165), "indoor_bride", "haldi", 1)
cv2.imwrite(os.path.join(OUT_DIR, "bride_3d_2.jpg"), bride_3d_2, [cv2.IMWRITE_JPEG_QUALITY, 94])

groom_src_2 = load_upright_bgr(os.path.join("only_groom", "5M5A2495.JPG"))
groom_3d_2 = composite_clean_3d(groom_src_2, stage_wedding, (0.14, 0.20, 0.86, 0.72), (92, 285, 676, 1165), "outdoor", "wedding", 1)
cv2.imwrite(os.path.join(OUT_DIR, "groom_3d_2.jpg"), groom_3d_2, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Regenerate Haldi 1, 2, 3
mix_2470 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2470.JPG"))
haldi_3d_1 = composite_clean_3d(mix_2470, stage_haldi, (0.02, 0.18, 0.96, 0.98), (85, 280, 683, 1170), "outdoor", "haldi", 0)
cv2.imwrite(os.path.join(OUT_DIR, "haldi_3d_1.jpg"), haldi_3d_1, [cv2.IMWRITE_JPEG_QUALITY, 94])

mix_2460 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2460.JPG"))
haldi_3d_2 = composite_clean_3d(mix_2460, stage_haldi, (0.0, 0.04, 1.0, 0.98), (85, 280, 683, 1170), "outdoor", "haldi", 1)
cv2.imwrite(os.path.join(OUT_DIR, "haldi_3d_2.jpg"), haldi_3d_2, [cv2.IMWRITE_JPEG_QUALITY, 94])

mix_2563 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2563.JPG"))
haldi_3d_3 = composite_clean_3d(mix_2563, stage_haldi, (0.02, 0.16, 0.98, 0.96), (85, 280, 683, 1170), "outdoor", "haldi", 2)
cv2.imwrite(os.path.join(OUT_DIR, "haldi_3d_3.jpg"), haldi_3d_3, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Regenerate Wedding 1, 2, 3
mix_2280 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2280 (1).JPG"))
wedding_3d_1 = composite_clean_3d(mix_2280, stage_wedding, (0.12, 0.12, 0.86, 0.98), (85, 290, 683, 1165), "indoor_couple", "wedding", 0)
cv2.imwrite(os.path.join(OUT_DIR, "wedding_3d_1.jpg"), wedding_3d_1, [cv2.IMWRITE_JPEG_QUALITY, 94])

mix_2581 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2581.JPG"))
wedding_3d_2 = composite_clean_3d(mix_2581, stage_wedding, (0.16, 0.21, 0.86, 0.96), (88, 280, 680, 1170), "outdoor", "wedding", 1)
cv2.imwrite(os.path.join(OUT_DIR, "wedding_3d_2.jpg"), wedding_3d_2, [cv2.IMWRITE_JPEG_QUALITY, 94])

mix_2512 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2512.JPG"))
wedding_3d_3 = composite_clean_3d(mix_2512, stage_wedding, (0.08, 0.38, 0.84, 0.95), (88, 285, 680, 1170), "outdoor", "wedding", 2)
cv2.imwrite(os.path.join(OUT_DIR, "wedding_3d_3.jpg"), wedding_3d_3, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Regenerate Finale Altar (Hands with DC Mehendi)
mix_2572 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2572.JPG"))
finale_altar_3d = composite_clean_3d(mix_2572, stage_wedding, (0.02, 0.0, 0.98, 1.0), (85, 360, 683, 1120), "hands", "wedding", 0)
cv2.imwrite(os.path.join(OUT_DIR, "finale_altar_3d.jpg"), finale_altar_3d, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Regenerate Scene 3: 3D Golden Sanctum (using the 3D Carved Golden Lotus Medallions & Blazing Sacred Samai Halo!)
lotus_med_src = door_bgr[870:1014, 196:340].copy()
def build_clean_golden_sanctum(variant=0):
    canvas = stage_sanctum.copy().astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    # Place an enlarged 3D Carved Golden Lotus Mandala in the upper sanctum halo (cx=384, cy=650, radius=190)
    lotus_big = cv2.resize(lotus_med_src, (380, 380), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    if variant == 1:
        M = cv2.getRotationMatrix2D((190, 190), 11.25, 1.0)
        lotus_big = cv2.warpAffine(lotus_big, M, (380, 380))
    # Enhance golden specular glow
    lotus_big[:, :, 0] *= 0.95
    lotus_big[:, :, 1] *= 1.35
    lotus_big[:, :, 2] *= 1.55
    ly, lx = np.mgrid[0:380, 0:380]
    ldist = np.sqrt(((lx - 190.0) / 185.0) ** 2 + ((ly - 190.0) / 185.0) ** 2)
    lmask = (np.clip((1.0 - ldist) * 2.5, 0, 1) ** 1.4 * 0.82)[:, :, None]
    roi = canvas[460:840, 194:574]
    canvas[460:840, 194:574] = roi * (1.0 - lmask) + np.clip(lotus_big, 0, 255) * lmask

    # Add central sacred golden flame & volumetric aura at (384, 650)
    fdist = np.sqrt(((xx - 384.0) / 95.0) ** 2 + ((yy - 650.0) / 95.0) ** 2)
    aura = np.exp(-fdist * 1.4) * (0.45 + 0.1 * variant)
    canvas[:, :, 0] += aura * 50.0
    canvas[:, :, 1] += aura * 185.0
    canvas[:, :, 2] += aura * 255.0

    canvas = np.clip(canvas, 0, 255).astype(np.uint8)
    overlay_rgba_sprite(canvas, lantern_rgba, 180, 275, 0.95, 0, 0.95)
    overlay_rgba_sprite(canvas, lantern_rgba, 590, 275, 0.95, 0, 0.95)
    overlay_rgba_sprite(canvas, marigold_1, 145 + variant * 12, 480 + variant * 10, 0.85, variant * 20, 0.92)
    overlay_rgba_sprite(canvas, marigold_3, 625 - variant * 12, 510 + variant * 10, 0.82, -variant * 20, 0.92)
    overlay_rgba_sprite(canvas, rose_1, 155 + variant * 10, 1110 - variant * 8, 0.88, variant * 15, 0.92)
    overlay_rgba_sprite(canvas, marigold_2, 615 - variant * 10, 1100 - variant * 8, 0.95, -variant * 15, 0.92)
    return canvas

cv2.imwrite(os.path.join(OUT_DIR, "sanctum_3d_1.jpg"), build_clean_golden_sanctum(0), [cv2.IMWRITE_JPEG_QUALITY, 94])
cv2.imwrite(os.path.join(OUT_DIR, "sanctum_3d_2.jpg"), build_clean_golden_sanctum(1), [cv2.IMWRITE_JPEG_QUALITY, 94])

# Regenerate Scene 7: Clean 3D Open Royal Palace Gate (Venue - ॥ विवाहस्थळ ॥)
def build_clean_open_gate():
    inner = stage_wedding.copy().astype(np.float32)
    outer = door_lit_1.copy().astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (xx - 384.0) / 246.0
    dy = (yy - 430.0) / 248.0
    in_rect = (xx > 138) & (xx < 630) & (yy > 430) & (yy < 1095)
    in_arch = (yy <= 430) & (yy > 182) & ((dx * dx + dy * dy) < 1.0)
    opening = np.zeros((H, W), dtype=np.float32)
    opening[in_rect | in_arch] = 1.0
    opening_blur = cv2.GaussianBlur(opening, (45, 45), 0)[:, :, None]

    gate = outer * (1.0 - opening_blur) + inner * opening_blur

    lh_d, lw_d = left_door_crop.shape[:2]
    src_pts = np.float32([[0, 0], [lw_d, 0], [lw_d, lh_d], [0, lh_d]])
    dst_pts_l = np.float32([[136, 200], [222, 255], [222, 1065], [136, 1115]])
    M_l = cv2.getPerspectiveTransform(src_pts, dst_pts_l)
    warped_l = cv2.warpPerspective(left_door_crop, M_l, (W, H))
    mask_l = cv2.warpPerspective(np.ones((lh_d, lw_d), dtype=np.float32), M_l, (W, H))[:, :, None] * opening_blur

    dst_pts_r = np.float32([[546, 255], [632, 200], [632, 1115], [546, 1065]])
    M_r = cv2.getPerspectiveTransform(src_pts, dst_pts_r)
    warped_r = cv2.warpPerspective(right_door_crop, M_r, (W, H))
    mask_r = cv2.warpPerspective(np.ones((lh_d, lw_d), dtype=np.float32), M_r, (W, H))[:, :, None] * opening_blur

    gate = gate * (1.0 - mask_l) + warped_l.astype(np.float32) * 0.88 * mask_l
    gate = gate * (1.0 - mask_r) + warped_r.astype(np.float32) * 0.88 * mask_r

    # Smooth golden light spill onto stone floor
    floor_spill = np.exp(-((xx - 384.0) / 210.0) ** 2) * np.exp(-((yy - 1110.0) / 170.0) ** 2)
    gate[:, :, 0] += floor_spill * 35.0
    gate[:, :, 1] += floor_spill * 150.0
    gate[:, :, 2] += floor_spill * 235.0

    gate_u8 = np.clip(gate, 0, 255).astype(np.uint8)
    overlay_rgba_sprite(gate_u8, lantern_rgba, 305, 315, 0.90, 0, 0.95)
    overlay_rgba_sprite(gate_u8, lantern_rgba, 465, 315, 0.90, 0, 0.95)
    overlay_rgba_sprite(gate_u8, marigold_1, 175, 960, 0.80, 15, 0.90)
    overlay_rgba_sprite(gate_u8, rose_1, 595, 975, 0.80, -18, 0.90)
    return gate_u8

cv2.imwrite(os.path.join(OUT_DIR, "venue_palace_3d.jpg"), build_clean_open_gate(), [cv2.IMWRITE_JPEG_QUALITY, 94])
print("All fixed 3D frames saved!")
