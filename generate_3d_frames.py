import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw

BRAIN_DIR = r"C:\Users\Asus\.gemini\antigravity\brain\41d6c376-34ae-4c6b-a1e5-025b91ae9ffa"
PREVIEW_DIR = os.path.join(BRAIN_DIR, "scratch", "previews")
OUT_DIR = r"d:\biu_app_clone_13_1_2026\biu_app\wedding_invitation\assets"
os.makedirs(OUT_DIR, exist_ok=True)

DOOR_3D_PATH = os.path.join(BRAIN_DIR, "scene_1a_unlit_door_samai_1795073477628.jpg")
BRIDE_3D_PATH = os.path.join(BRAIN_DIR, "bride_royal_jharokha_3d_1795073496764.jpg")
GROOM_3D_PATH = os.path.join(BRAIN_DIR, "groom_royal_jharokha_3d_1795073528118.jpg")

door_bgr = cv2.imread(DOOR_3D_PATH)
bride_bgr = cv2.imread(BRIDE_3D_PATH)
groom_bgr = cv2.imread(GROOM_3D_PATH)

H, W = door_bgr.shape[:2]  # 1376, 768
print(f"Base 3D canvas: {W}x{H}")

# ---------------------------------------------------------
# 1. EXTRACT REAL 3D RENDERED SPRITES (MARIGOLDS, ROSES, LANTERNS, FLAMES)
# ---------------------------------------------------------
def extract_soft_patch(img_bgr, x1, y1, x2, y2, bg_thresh=None):
    patch = img_bgr[y1:y2, x1:x2].copy()
    ph, pw = patch.shape[:2]
    # Create radial alpha mask with soft feathered edge
    yy, xx = np.mgrid[0:ph, 0:pw]
    cx, cy = pw / 2.0, ph / 2.0
    rx, ry = pw / 2.0, ph / 2.0
    dist = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    alpha = np.clip((1.0 - dist) * 2.2, 0, 1) ** 1.3

    # Also boost alpha on colourful/bright pixels so flower petals pop cleanly
    hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV).astype(np.float32)
    sat = hsv[:, :, 1] / 255.0
    val = hsv[:, :, 2] / 255.0
    color_mask = np.clip((sat - 0.25) * 3.0, 0, 1) * np.clip((val - 0.15) * 2.5, 0, 1)
    final_alpha = np.clip(alpha * np.maximum(color_mask, alpha * 0.85), 0, 1)
    rgba = cv2.cvtColor(patch, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = (final_alpha * 255).astype(np.uint8)
    return rgba

# Extract real 3D marigold blossoms & rose petals from bride_bgr & groom_bgr
# In bride_bgr (768x1376):
# Big foreground marigold bottom-right: x=565..668, y=1058..1148
marigold_1 = extract_soft_patch(bride_bgr, 565, 1058, 668, 1148)
cv2.imwrite(os.path.join(OUT_DIR, "petal_marigold_3d_1.png"), marigold_1)

# Mid-left marigold in bride_bgr: x=85..155, y=608..675
marigold_2 = extract_soft_patch(bride_bgr, 85, 608, 155, 675)
cv2.imwrite(os.path.join(OUT_DIR, "petal_marigold_3d_2.png"), marigold_2)

# Foreground marigold in groom_bgr: x=105..218, y=898..1008
marigold_3 = extract_soft_patch(groom_bgr, 105, 898, 218, 1008)
cv2.imwrite(os.path.join(OUT_DIR, "petal_marigold_3d_3.png"), marigold_3)

# Foreground rose blossom bottom-right in bride_bgr: x=612..720, y=1185..1290
rose_1 = extract_soft_patch(bride_bgr, 612, 1185, 720, 1290)
cv2.imwrite(os.path.join(OUT_DIR, "petal_rose_3d_1.png"), rose_1)

# Mid-left red rose petal in bride_bgr: x=175..232, y=532..585
rose_2 = extract_soft_patch(bride_bgr, 175, 532, 232, 585)
cv2.imwrite(os.path.join(OUT_DIR, "petal_rose_3d_2.png"), rose_2)

# Extract 3D Hanging Golden Palace Lantern from groom_bgr: x=548..608, y=220..355
lantern_patch = groom_bgr[210:360, 545:610].copy()
lh, lw = lantern_patch.shape[:2]
yy, xx = np.mgrid[0:lh, 0:lw]
dist_x = np.abs(xx - lw / 2.0) / (lw / 2.0)
dist_y = np.abs(yy - lh / 2.0) / (lh / 2.0)
l_alpha = np.clip((1.0 - np.maximum(dist_x ** 2, dist_y ** 2)) * 2.0, 0, 1)
lantern_rgba = cv2.cvtColor(lantern_patch, cv2.COLOR_BGR2BGRA)
lantern_rgba[:, :, 3] = (l_alpha * 255).astype(np.uint8)
cv2.imwrite(os.path.join(OUT_DIR, "lantern_gold_3d.png"), lantern_rgba)

print("Extracted real 3D marigold, rose, and lantern sprites.")


# ---------------------------------------------------------
# 2. BUILD SCENE 1 & 2: 3D RAJWADA DOOR & PEACOCK SAMAI SEQUENCE
# ---------------------------------------------------------
# Save unlit base frame
cv2.imwrite(os.path.join(OUT_DIR, "scene1_door_unlit.jpg"), door_bgr, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Extract real 3D Samai flame cluster from bride_bgr left samai (x=58..155, y=735..845)
flame_src = bride_bgr[740:830, 62:152].copy()

def create_lit_door_frame(base_bgr, intensity=1.0, petal_shift=0):
    canvas = base_bgr.copy().astype(np.float32)
    # In door_bgr (768x1376), the Peacock Samai lamp tray is centered at x=384, y=840 (tray width ~130px)
    # Let's place 5 realistic glowing 3D flames along the circular brass oil tray:
    flame_positions = [
        (322, 835, 1.0),
        (352, 842, 1.15),
        (384, 845, 1.3),
        (416, 842, 1.15),
        (446, 835, 1.0),
    ]
    yy, xx = np.mgrid[0:H, 0:W]

    # Global warm volumetric golden god-rays radiating from (384, 825)
    dx = (xx - 384.0) / float(W)
    dy = (yy - 825.0) / float(H)
    dist = np.sqrt(dx * dx + dy * dy) + 1e-4
    angle = np.arctan2(dy, dx)

    # Volumetric ray streaks
    ray_pattern = (
        0.55
        + 0.25 * np.sin(angle * 14.0 + petal_shift * 0.7)
        + 0.20 * np.cos(angle * 23.0 - petal_shift * 1.1)
    )
    radial_falloff = np.exp(-dist * 2.3) * intensity
    god_rays = radial_falloff * ray_pattern

    # Specular highlight boost on carved gold inlays of the door
    gray_door = cv2.cvtColor(base_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    gold_spec = np.clip((gray_door - 0.18) * 2.5, 0, 1) * np.exp(-dist * 1.9) * intensity

    # Add warm golden light (BGR: 60, 185, 255)
    canvas[:, :, 0] += god_rays * 45.0 + gold_spec * 35.0
    canvas[:, :, 1] += god_rays * 155.0 + gold_spec * 135.0
    canvas[:, :, 2] += god_rays * 245.0 + gold_spec * 220.0

    # Render each of the 5 3D Samai flames with hot white-yellow core & orange-gold halo
    for fx, fy, fscale in flame_positions:
        s = fscale * (0.95 + 0.1 * np.sin(fx + petal_shift * 2.0))
        fdx = (xx - fx) / (11.0 * s)
        fdy = (yy - (fy - 14.0 * s)) / (24.0 * s)
        # Teardrop flame shape (narrower at top)
        taper = 1.0 + 0.45 * np.clip(-fdy, -1, 2)
        f_dist = np.sqrt((fdx * taper) ** 2 + fdy ** 2)

        core = np.exp(-(f_dist ** 2) * 2.8) * intensity
        inner = np.exp(-(f_dist ** 1.6) * 0.95) * intensity
        outer = np.exp(-f_dist * 0.45) * 0.55 * intensity

        canvas[:, :, 0] += core * 220.0 + inner * 70.0 + outer * 15.0
        canvas[:, :, 1] += core * 255.0 + inner * 200.0 + outer * 110.0
        canvas[:, :, 2] += core * 255.0 + inner * 255.0 + outer * 220.0

    canvas = np.clip(canvas, 0, 255).astype(np.uint8)

    # Composite a few floating 3D marigold petals & golden embers
    def overlay_rgba(bg, fg_rgba, px, py, scale=1.0, rot=0):
        fh, fw = fg_rgba.shape[:2]
        nw, nh = int(fw * scale), int(fh * scale)
        if nw < 5 or nh < 5:
            return
        resized = cv2.resize(fg_rgba, (nw, nh), interpolation=cv2.INTER_AREA)
        if rot != 0:
            M = cv2.getRotationMatrix2D((nw / 2, nh / 2), rot, 1.0)
            resized = cv2.warpAffine(resized, M, (nw, nh), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        x1, y1 = int(px - nw // 2), int(py - nh // 2)
        x2, y2 = x1 + nw, y1 + nh
        bx1, by1 = max(0, x1), max(0, y1)
        bx2, by2 = min(W, x2), min(H, y2)
        if bx2 <= bx1 or by2 <= by1:
            return
        fx1, fy1 = bx1 - x1, by1 - y1
        fx2, fy2 = fx1 + (bx2 - bx1), fy1 + (by2 - by1)
        alpha = (resized[fy1:fy2, fx1:fx2, 3:4].astype(np.float32) / 255.0) * 0.9
        bg[by1:by2, bx1:bx2] = (
            bg[by1:by2, bx1:bx2].astype(np.float32) * (1.0 - alpha)
            + resized[fy1:fy2, fx1:fx2, :3].astype(np.float32) * alpha
        ).astype(np.uint8)

    overlay_rgba(canvas, marigold_2, 160 + petal_shift * 12, 460 + petal_shift * 15, 0.75, petal_shift * 25)
    overlay_rgba(canvas, marigold_1, 610 - petal_shift * 10, 590 + petal_shift * 18, 0.65, -petal_shift * 20)
    overlay_rgba(canvas, rose_2, 230 + petal_shift * 8, 950 - petal_shift * 12, 0.85, petal_shift * 15)
    overlay_rgba(canvas, marigold_3, 560 - petal_shift * 14, 980 - petal_shift * 10, 0.55, petal_shift * 30)
    return canvas

door_lit_1 = create_lit_door_frame(door_bgr, intensity=1.05, petal_shift=0)
door_lit_2 = create_lit_door_frame(door_bgr, intensity=1.22, petal_shift=1)
cv2.imwrite(os.path.join(OUT_DIR, "scene1_door_lit_1.jpg"), door_lit_1, [cv2.IMWRITE_JPEG_QUALITY, 94])
cv2.imwrite(os.path.join(OUT_DIR, "scene1_door_lit_2.jpg"), door_lit_2, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Also create separated Left and Right 3D Carved Door panels & Outer Sandstone Arch for the 3D Door Swing animation!
# In door_lit_1 (768x1376), the wooden door opening spans x=128..640, y=180..1125
# Left door: x=128..384, Right door: x=384..640
left_door_crop = door_lit_1[180:1125, 128:384].copy()
right_door_crop = door_lit_1[180:1125, 384:640].copy()
cv2.imwrite(os.path.join(OUT_DIR, "door_left_panel.jpg"), left_door_crop, [cv2.IMWRITE_JPEG_QUALITY, 92])
cv2.imwrite(os.path.join(OUT_DIR, "door_right_panel.jpg"), right_door_crop, [cv2.IMWRITE_JPEG_QUALITY, 92])

print("Generated Scene 1 & 2 3D Rajwada Door & Blazing Peacock Samai frames.")


# ---------------------------------------------------------
# 3. CONSTRUCT THE 3D GOLDEN RAJWADA JHAROKHA PALACE STAGE & FOREGROUND PORTAL
# ---------------------------------------------------------
def build_empty_palace_stage(theme="haldi"):
    """
    Constructs a pure 3D Octane-rendered Rajwada Palace Jharokha backdrop (768x1376)
    by combining the unoccluded 3D architecture from bride_bgr and groom_bgr.
    """
    stage = bride_bgr.copy().astype(np.float32)

    # In bride_bgr, the bride occupies x=110..660, y=350..1376.
    # Let's fill the center palace backdrop (x=135..635, y=330..1120) using:
    # 1) The upper palace jali arch & colonnade from groom_bgr[130:440, 140:628]
    # 2) The volumetric sunlight god-rays from bride_bgr[170:365, 195:575]
    jali_top = groom_bgr[170:440, 140:628].copy()
    jali_stretched = cv2.resize(jali_top, (500, 790), interpolation=cv2.INTER_CUBIC)
    jali_blurred = cv2.GaussianBlur(jali_stretched, (25, 25), 0).astype(np.float32)

    # Also take the warm volumetric rays from bride_bgr top-center
    rays_top = bride_bgr[180:360, 210:558].copy()
    rays_stretched = cv2.resize(rays_top, (500, 790), interpolation=cv2.INTER_CUBIC)
    rays_blurred = cv2.GaussianBlur(rays_stretched, (45, 45), 0).astype(np.float32)

    center_fill = jali_blurred * 0.55 + rays_blurred * 0.45

    # Smooth feather mask for center region (x=135..635, y=330..1120)
    mask = np.zeros((H, W), dtype=np.float32)
    mask[345:1110, 155:613] = 1.0
    # Protect left & right 3D brass samais in bride_bgr (left samai x=55..158, y=735..1075; right samai x=610..705, y=735..1075)
    mask[720:1090, 0:165] = 0.0
    mask[720:1090, 603:768] = 0.0
    mask = cv2.GaussianBlur(mask, (61, 61), 0)[:, :, None]

    stage_center = stage.copy()
    stage_center[330:1120, 135:635] = center_fill
    stage = stage * (1.0 - mask) + stage_center * mask

    # Place the 3D Carved Sandstone & Gold Jali Balustrade from groom_bgr at the bottom (y=1075..1376)
    balustrade = groom_bgr[1075:1376, :].copy().astype(np.float32)
    b_mask = np.zeros((H, W), dtype=np.float32)
    b_mask[1100:1376, :] = 1.0
    b_mask = cv2.GaussianBlur(b_mask, (45, 45), 0)[:, :, None]
    stage_b = stage.copy()
    stage_b[1075:1376, :] = balustrade
    stage = stage * (1.0 - b_mask) + stage_b * b_mask

    # Add the 3D Hanging Golden Palace Lanterns from groom_bgr on left (x=140..220, y=185..430) and right (x=545..615, y=170..365)
    for lx1, ly1, lx2, ly2 in [(142, 190, 215, 425), (545, 175, 612, 360)]:
        l_patch = groom_bgr[ly1:ly2, lx1:lx2].astype(np.float32)
        lh, lw = l_patch.shape[:2]
        yy, xx = np.mgrid[0:lh, 0:lw]
        wx = np.sin(np.pi * xx / lw) ** 0.7
        wy = np.sin(np.pi * yy / lh) ** 0.7
        w = (wx * wy)[:, :, None]
        stage[ly1:ly2, lx1:lx2] = stage[ly1:ly2, lx1:lx2] * (1.0 - w) + l_patch * w

    if theme == "haldi":
        # Rich Surya-Kesar (Sunlit Saffron & Raw Turmeric Gold) grading
        stage[:, :, 0] *= 0.82  # warm amber-gold
        stage[:, :, 1] *= 1.06
        stage[:, :, 2] *= 1.14
    elif theme == "wedding":
        # Royal Starlit Palace Crimson-Gold & Deep Zari Amber grading
        stage[:, :, 0] *= 0.88
        stage[:, :, 1] *= 0.94
        stage[:, :, 2] *= 1.12
    elif theme == "sanctum":
        stage[:, :, 0] *= 0.85
        stage[:, :, 1] *= 1.04
        stage[:, :, 2] *= 1.16

    return np.clip(stage, 0, 255).astype(np.uint8)

stage_haldi = build_empty_palace_stage("haldi")
stage_wedding = build_empty_palace_stage("wedding")
stage_sanctum = build_empty_palace_stage("sanctum")

# Build the Foreground 3D Architectural Portal Mask (1.0 where the 3D Carved Golden Arch, Pillars, Twin Brass Samais, and Bottom Balustrade sit IN FRONT of subjects)
portal_mask = np.zeros((H, W), dtype=np.float32)
# Outer left & right 3D carved columns
portal_mask[:, :92] = 1.0
portal_mask[:, 676:] = 1.0
# Top 3D carved multi-foil arch curve
yy, xx = np.mgrid[0:H, 0:W]
arch_dx = (xx - 384.0) / 310.0
arch_dy = (yy - 360.0) / 245.0
arch_rad = np.sqrt(arch_dx ** 2 + arch_dy ** 2)
top_arch_region = (yy < 360) & (arch_rad > 0.92)
portal_mask[top_arch_region] = 1.0
portal_mask[:145, :] = 1.0
# Twin 3D blazing brass Samais in lower-left (x=62..152, y=745..1085) & lower-right (x=615..705, y=745..1085)
portal_mask[750:1085, 65:148] = 0.92
portal_mask[750:1085, 620:702] = 0.92
# Bottom 3D Carved Jali Balustrade (y=1145..1376)
portal_mask[1155:, :] = 1.0
portal_mask = cv2.GaussianBlur(portal_mask, (35, 35), 0)

print("Constructed 3D Golden Rajwada Palace Stages (Haldi, Wedding, Sanctum) and Foreground 3D Portal.")


# ---------------------------------------------------------
# 4. HELPER TO COMPOSITE & 3D-RELIGHT SUBJECTS INTO THE 3D PALACE STAGE
# ---------------------------------------------------------
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

def load_upright_bgr(rel_path):
    full_path = os.path.join(PREVIEW_DIR, rel_path)
    pil_im = ImageOps.exif_transpose(Image.open(full_path)).convert("RGB")
    return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

def composite_into_3d_palace(
    src_bgr,
    stage_bgr,
    crop_box,       # (x1_norm, y1_norm, x2_norm, y2_norm) on src_bgr
    dest_box,       # (dx1, dy1, dx2, dy2) on 768x1376 stage
    mode="outdoor", # "outdoor" (green foliage) or "indoor_couple" or "indoor_bride"
    theme="haldi",  # "haldi" or "wedding"
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
        # Green foliage detection (Hue 25..98 in OpenCV 0..180 scale)
        is_green = (h_ch > 24) & (h_ch < 98) & (s_ch > 22)
        # Sky / bright background at top
        is_sky = (v_ch > 180) & (s_ch < 45) & (ny < 0.38)
        # Grass at bottom corners
        is_grass = (h_ch > 20) & (h_ch < 95) & (ny > 0.80) & ((nx < 0.22) | (nx > 0.78))
        bg_prob = np.zeros((th, tw), dtype=np.float32)
        bg_prob[is_green | is_sky | is_grass] = 1.0

        # Despill any green tint on transition pixels into warm golden amber!
        green_zone = (h_ch > 24) & (h_ch < 98)
        subj_f = subj.astype(np.float32)
        # Replace excess green channel with warm gold (R > G > B)
        excess_g = np.maximum(0.0, subj_f[:, :, 1] - subj_f[:, :, 2] * 0.85)
        subj_f[:, :, 1] = np.where(green_zone, subj_f[:, :, 1] - excess_g * 0.75, subj_f[:, :, 1])
        subj_f[:, :, 2] = np.where(green_zone, np.minimum(255.0, subj_f[:, :, 2] + excess_g * 0.55), subj_f[:, :, 2])
        subj_f[:, :, 0] = np.where(green_zone, subj_f[:, :, 0] * 0.75, subj_f[:, :, 0])
        subj = np.clip(subj_f, 0, 255).astype(np.uint8)

        fg_mask = 1.0 - bg_prob

    elif mode == "indoor_couple":
        # For 5M5A2280 (1).JPG (couple facing each other holding hands)
        # White/cream curtain + red letters in center gap between bride (left) and groom (right)
        is_white_curtain = (v_ch > 175) & (s_ch < 48)
        # Center gap above their joined hands (nx in 0.36..0.58, ny in 0.0..0.67)
        in_center_gap = (nx > 0.35) & (nx < 0.58) & (ny < 0.67)
        # Top floral border above heads
        in_top_border = (ny < 0.14) | ((ny < 0.24) & (nx < 0.55))
        # Outer edges
        in_outer = (nx < 0.08) | (nx > 0.92) | ((ny > 0.75) & (nx > 0.37) & (nx < 0.57))

        bg_prob = np.zeros((th, tw), dtype=np.float32)
        bg_prob[in_center_gap | in_top_border | in_outer] = 1.0
        bg_prob[is_white_curtain & ((ny < 0.35) | (nx < 0.16) | (nx > 0.84))] = 1.0
        fg_mask = 1.0 - bg_prob

    elif mode == "indoor_bride":
        # For 5M5A2086.JPG (solo bride in aqua saree)
        is_bg = ((nx < 0.16) | (nx > 0.84) | (ny < 0.12))
        # Red letters 'देवश्री' on right background curtain (nx > 0.65, ny < 0.45)
        is_red_text = (nx > 0.64) & (ny < 0.45)
        is_white_bg = (v_ch > 180) & (s_ch < 45) & ((nx < 0.26) | (nx > 0.72) | (ny < 0.25))
        bg_prob = np.zeros((th, tw), dtype=np.float32)
        bg_prob[is_bg | is_red_text | is_white_bg] = 1.0
        fg_mask = 1.0 - bg_prob

    # Arch-shaped soft vignette around subject box so edges blend smoothly into the 3D Jharokha Arch
    arch_x = (nx - 0.5) / 0.47
    arch_y = (ny - 0.52) / 0.48
    arch_falloff = np.clip((1.0 - (arch_x ** 4 + arch_y ** 4)) * 2.5, 0, 1)
    fg_mask = fg_mask * arch_falloff
    fg_mask = cv2.GaussianBlur(fg_mask, (27, 27), 0)

    # Apply 3D Golden Rim-Lighting & Warm Palace Relighting to subject while keeping faces natural
    subj_f = subj.astype(np.float32)
    # Detect edge of silhouette for 3D golden rim light
    edge_grad = cv2.GaussianBlur(fg_mask, (5, 5), 0) - cv2.GaussianBlur(fg_mask, (35, 35), 0)
    rim_light = np.clip(edge_grad * 2.4, 0, 1)[:, :, None]

    if theme == "haldi":
        # Warm sunlit golden-saffron rim light + subtle warm ambience
        subj_f[:, :, 0] = subj_f[:, :, 0] * 0.93 + rim_light[:, :, 0] * 45.0
        subj_f[:, :, 1] = subj_f[:, :, 1] * 1.02 + rim_light[:, :, 0] * 175.0
        subj_f[:, :, 2] = subj_f[:, :, 2] * 1.06 + rim_light[:, :, 0] * 245.0
    else:
        # Royal starlit amber-gold palace rim light
        subj_f[:, :, 0] = subj_f[:, :, 0] * 0.95 + rim_light[:, :, 0] * 55.0
        subj_f[:, :, 1] = subj_f[:, :, 1] * 1.00 + rim_light[:, :, 0] * 160.0
        subj_f[:, :, 2] = subj_f[:, :, 2] * 1.05 + rim_light[:, :, 0] * 235.0

    subj_relit = np.clip(subj_f, 0, 255)

    # Composite subject onto the 3D Palace Stage
    canvas = stage_bgr.copy().astype(np.float32)
    alpha_3 = fg_mask[:, :, None]
    roi = canvas[dy1:dy2, dx1:dx2]
    canvas[dy1:dy2, dx1:dx2] = roi * (1.0 - alpha_3) + subj_relit * alpha_3

    # Layer the Foreground 3D Architectural Portal (Carved Golden Arch, Twin Brass Samais, Bottom Jali Balustrade) ON TOP
    p_alpha = portal_mask[:, :, None]
    canvas = canvas * (1.0 - p_alpha) + stage_bgr.astype(np.float32) * p_alpha

    # Add Volumetric 3D God-Rays streaming from the upper 3D Jharokha Arch (x=384, y=180)
    gy, gx = np.mgrid[0:H, 0:W]
    gdx = (gx - 384.0) / float(W)
    gdy = (gy - 160.0) / float(H)
    gdist = np.sqrt(gdx * gdx + gdy * gdy) + 1e-4
    gangle = np.arctan2(gdy, gdx)
    beams = (0.5 + 0.5 * np.sin(gangle * 16.0 + variant * 1.2)) * np.exp(-gdist * 1.8) * (gy > 160) * (gy < 980)

    if theme == "haldi":
        # Add swirling 3D golden Haldi turmeric mist at lower/mid courtyard + sunlit rays
        haldi_mist = np.exp(-((gy - 980.0) / 260.0) ** 2) * (0.4 + 0.3 * np.sin(gx / 95.0 + variant))
        total_glow = beams * 0.28 + haldi_mist * 0.16
        canvas[:, :, 0] += total_glow * 30.0
        canvas[:, :, 1] += total_glow * 180.0
        canvas[:, :, 2] += total_glow * 255.0
    else:
        # Starlit golden palace glow & rising sky lantern aura
        total_glow = beams * 0.24
        canvas[:, :, 0] += total_glow * 40.0
        canvas[:, :, 1] += total_glow * 155.0
        canvas[:, :, 2] += total_glow * 240.0

    canvas = np.clip(canvas, 0, 255).astype(np.uint8)

    # Layer real 3D rendered Marigold & Rose Petals (and 3D Golden Lanterns for wedding) in foreground bokeh!
    if theme == "haldi":
        overlay_rgba_sprite(canvas, marigold_1, 130 + variant * 25, 420 + variant * 15, 0.85, variant * 20, 0.92)
        overlay_rgba_sprite(canvas, marigold_3, 635 - variant * 20, 470 + variant * 20, 0.78, -variant * 25, 0.92)
        overlay_rgba_sprite(canvas, marigold_2, 145 + variant * 15, 1080 - variant * 18, 1.05, variant * 15, 0.95)
        overlay_rgba_sprite(canvas, marigold_1, 618 - variant * 18, 1115 - variant * 12, 0.95, -variant * 18, 0.95)
        overlay_rgba_sprite(canvas, rose_2, 650 - variant * 12, 720 + variant * 15, 0.80, variant * 30, 0.85)
    else:
        overlay_rgba_sprite(canvas, lantern_rgba, 175 + variant * 10, 275 + variant * 8, 0.95, 0, 0.92)
        overlay_rgba_sprite(canvas, lantern_rgba, 595 - variant * 10, 265 + variant * 8, 0.92, 0, 0.92)
        overlay_rgba_sprite(canvas, rose_1, 135 + variant * 20, 1120 - variant * 15, 0.90, variant * 20, 0.92)
        overlay_rgba_sprite(canvas, marigold_1, 625 - variant * 20, 1105 - variant * 15, 0.88, -variant * 15, 0.92)
        overlay_rgba_sprite(canvas, rose_2, 130 + variant * 15, 520 + variant * 20, 0.85, variant * 25, 0.88)

    return canvas

# ---------------------------------------------------------
# 5. GENERATE ALL MULTI-FRAME 3D SCENES
# ---------------------------------------------------------
# A) SOLO BRIDE 3D FRAMES (Scene 4 - वधू: चि. सौ. कां. देविश्री)
cv2.imwrite(os.path.join(OUT_DIR, "bride_3d_1.jpg"), bride_bgr, [cv2.IMWRITE_JPEG_QUALITY, 94])
bride_src_2 = load_upright_bgr(os.path.join("only_bride", "5M5A2086.JPG"))
bride_3d_2 = composite_into_3d_palace(
    bride_src_2, stage_haldi,
    crop_box=(0.05, 0.14, 0.95, 0.96),
    dest_box=(95, 290, 673, 1175),
    mode="indoor_bride", theme="haldi", variant=1
)
cv2.imwrite(os.path.join(OUT_DIR, "bride_3d_2.jpg"), bride_3d_2, [cv2.IMWRITE_JPEG_QUALITY, 94])

# B) SOLO GROOM 3D FRAMES (Scene 4 - वर: चि. चेतन)
cv2.imwrite(os.path.join(OUT_DIR, "groom_3d_1.jpg"), groom_bgr, [cv2.IMWRITE_JPEG_QUALITY, 94])
groom_src_2 = load_upright_bgr(os.path.join("only_groom", "5M5A2495.JPG"))
groom_3d_2 = composite_into_3d_palace(
    groom_src_2, stage_wedding,
    crop_box=(0.12, 0.18, 0.88, 0.72),
    dest_box=(95, 290, 673, 1175),
    mode="outdoor", theme="wedding", variant=1
)
cv2.imwrite(os.path.join(OUT_DIR, "groom_3d_2.jpg"), groom_3d_2, [cv2.IMWRITE_JPEG_QUALITY, 94])

# C) HALDI CEREMONY 3-FRAME 3D SEQUENCE (Scene 5 - ॥ हळद कार्यक्रम ॥)
# Frame 1: 5M5A2470.JPG (Forehead kiss & radiant smile)
mix_2470 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2470.JPG"))
haldi_3d_1 = composite_into_3d_palace(
    mix_2470, stage_haldi,
    crop_box=(0.02, 0.16, 0.96, 0.98),
    dest_box=(82, 275, 686, 1185),
    mode="outdoor", theme="haldi", variant=0
)
cv2.imwrite(os.path.join(OUT_DIR, "haldi_3d_1.jpg"), haldi_3d_1, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Frame 2: 5M5A2460.JPG (Romantic close-up forehead-to-forehead)
mix_2460 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2460.JPG"))
haldi_3d_2 = composite_into_3d_palace(
    mix_2460, stage_haldi,
    crop_box=(0.0, 0.02, 1.0, 0.98),
    dest_box=(82, 280, 686, 1185),
    mode="outdoor", theme="haldi", variant=1
)
cv2.imwrite(os.path.join(OUT_DIR, "haldi_3d_2.jpg"), haldi_3d_2, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Frame 3: 5M5A2563.JPG (Gazing into each other's eyes holding hands)
mix_2563 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2563.JPG"))
haldi_3d_3 = composite_into_3d_palace(
    mix_2563, stage_haldi,
    crop_box=(0.02, 0.14, 0.98, 0.96),
    dest_box=(82, 280, 686, 1185),
    mode="outdoor", theme="haldi", variant=2
)
cv2.imwrite(os.path.join(OUT_DIR, "haldi_3d_3.jpg"), haldi_3d_3, [cv2.IMWRITE_JPEG_QUALITY, 94])

# D) WEDDING MANDAP 3-FRAME 3D SEQUENCE (Scene 6 - ॥ यांचा शुभविवाह ॥)
# Frame 1: 5M5A2280 (1).JPG (Facing each other holding hands in ceremony pose)
mix_2280 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2280 (1).JPG"))
wedding_3d_1 = composite_into_3d_palace(
    mix_2280, stage_wedding,
    crop_box=(0.11, 0.10, 0.86, 0.98),
    dest_box=(78, 285, 690, 1180),
    mode="indoor_couple", theme="wedding", variant=0
)
cv2.imwrite(os.path.join(OUT_DIR, "wedding_3d_1.jpg"), wedding_3d_1, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Frame 2: 5M5A2581.JPG (Full romantic pose forehead touch in ivory gown & floral bandhgala)
mix_2581 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2581.JPG"))
wedding_3d_2 = composite_into_3d_palace(
    mix_2581, stage_wedding,
    crop_box=(0.14, 0.18, 0.88, 0.96),
    dest_box=(82, 275, 686, 1185),
    mode="outdoor", theme="wedding", variant=1
)
cv2.imwrite(os.path.join(OUT_DIR, "wedding_3d_2.jpg"), wedding_3d_2, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Frame 3: 5M5A2512.JPG (Walking hand-in-hand)
mix_2512 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2512.JPG"))
wedding_3d_3 = composite_into_3d_palace(
    mix_2512, stage_wedding,
    crop_box=(0.08, 0.34, 0.85, 0.96),
    dest_box=(82, 285, 686, 1185),
    mode="outdoor", theme="wedding", variant=2
)
cv2.imwrite(os.path.join(OUT_DIR, "wedding_3d_3.jpg"), wedding_3d_3, [cv2.IMWRITE_JPEG_QUALITY, 94])

print("Generated all Bride, Groom, Haldi, and Wedding 3D multi-frame sequences.")


# ---------------------------------------------------------
# 6. GENERATE SCENE 3 (3D GOLDEN SANCTUM), SCENE 7 (3D OPEN PALACE GATE), SCENE 8 (3D ALTAR)
# ---------------------------------------------------------
# Extract Peacock Samai with blazing flames from door_lit_1 (x=280..488, y=510..1325)
samai_crop = door_lit_1[510:1325, 280:488].copy()
sh_s, sw_s = samai_crop.shape[:2]
yy_s, xx_s = np.mgrid[0:sh_s, 0:sw_s]
# Peacock samai brightness/gold contrast against dark brown door behind it
hsv_s = cv2.cvtColor(samai_crop, cv2.COLOR_BGR2HSV).astype(np.float32)
val_s = hsv_s[:, :, 2] / 255.0
sat_s = hsv_s[:, :, 1] / 255.0
center_dist = np.abs(xx_s - sw_s / 2.0) / (sw_s / 2.0)
samai_alpha = np.clip((val_s - 0.16) * 3.2, 0, 1) * np.clip((1.0 - center_dist ** 1.8) * 1.8, 0, 1)
samai_alpha = cv2.GaussianBlur(samai_alpha, (9, 9), 0)
samai_rgba = cv2.cvtColor(samai_crop, cv2.COLOR_BGR2BGRA)
samai_rgba[:, :, 3] = (samai_alpha * 255).astype(np.uint8)
cv2.imwrite(os.path.join(OUT_DIR, "peacock_samai_3d.png"), samai_rgba)

def build_3d_golden_sanctum(variant=0):
    canvas = stage_sanctum.copy().astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    # Sculpt a 3D PBR Metallic Gold Mandala Halo in the center sanctum (cx=384, cy=610)
    dx = (xx - 384.0) / 185.0
    dy = (yy - 610.0) / 185.0
    r = np.sqrt(dx * dx + dy * dy) + 1e-5
    theta = np.arctan2(dy, dx)

    # 3D carved lotus & mandala rings heightfield
    petals_16 = np.cos(theta * 16.0 + variant * 0.4)
    petals_8 = np.cos(theta * 8.0 - variant * 0.3)
    rings = np.sin(r * 22.0) * 0.5 + 0.5
    mandala_h = (
        np.exp(-((r - 0.72) / 0.18) ** 2) * (0.6 + 0.4 * petals_16)
        + np.exp(-((r - 0.45) / 0.14) ** 2) * (0.6 + 0.4 * petals_8)
        + np.exp(-(r / 0.95) ** 2) * rings * 0.35
    ) * (r < 1.05)

    # Normal-map 3D lighting from top-center golden rays
    grad_y, grad_x = np.gradient(mandala_h * 12.0)
    light_score = np.clip(0.65 - grad_y * 0.45 - grad_x * 0.25, 0, 1.6)
    halo_mask = np.clip(mandala_h * 0.85, 0, 0.78)[:, :, None]

    gold_bgr = np.zeros((H, W, 3), dtype=np.float32)
    gold_bgr[:, :, 0] = 45.0 * light_score
    gold_bgr[:, :, 1] = 175.0 * light_score
    gold_bgr[:, :, 2] = 248.0 * light_score

    canvas = canvas * (1.0 - halo_mask) + gold_bgr * halo_mask
    canvas = np.clip(canvas, 0, 255).astype(np.uint8)

    # Place the 3D Blazing Peacock Samai in the center of the Golden Sanctum
    overlay_rgba_sprite(canvas, samai_rgba, 384, 835, scale=0.88, rot=0.0, opacity=0.98)
    # Floating 3D marigold & rose blossoms
    overlay_rgba_sprite(canvas, marigold_1, 145 + variant * 15, 480 + variant * 12, 0.85, variant * 20, 0.92)
    overlay_rgba_sprite(canvas, marigold_3, 625 - variant * 15, 510 + variant * 12, 0.82, -variant * 20, 0.92)
    overlay_rgba_sprite(canvas, rose_1, 155 + variant * 12, 1110 - variant * 10, 0.88, variant * 15, 0.92)
    overlay_rgba_sprite(canvas, marigold_2, 615 - variant * 12, 1100 - variant * 10, 0.95, -variant * 15, 0.92)
    return canvas

sanctum_1 = build_3d_golden_sanctum(0)
sanctum_2 = build_3d_golden_sanctum(1)
cv2.imwrite(os.path.join(OUT_DIR, "sanctum_3d_1.jpg"), sanctum_1, [cv2.IMWRITE_JPEG_QUALITY, 94])
cv2.imwrite(os.path.join(OUT_DIR, "sanctum_3d_2.jpg"), sanctum_2, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Build Scene 7: 3D Open Royal Palace Gate (Venue - ॥ विवाहस्थळ ॥)
def build_3d_open_palace_gate():
    # Start with the glowing inner courtyard stage
    inner = stage_wedding.copy().astype(np.float32)
    # Take the outer 3D Carved Sandstone Archway & Stone Floor from door_lit_1
    outer = door_lit_1.copy().astype(np.float32)

    # Create doorway opening mask where the wooden doors were (x=135..633, y=185..1120 with arch top)
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (xx - 384.0) / 248.0
    dy = (yy - 430.0) / 250.0
    in_rect = (xx > 136) & (xx < 632) & (yy > 430) & (yy < 1120)
    in_arch = (yy <= 430) & (yy > 180) & ((dx * dx + dy * dy) < 1.0)
    opening = np.zeros((H, W), dtype=np.float32)
    opening[in_rect | in_arch] = 1.0
    opening_blur = cv2.GaussianBlur(opening, (25, 25), 0)[:, :, None]

    # Blend glowing inner palace courtyard through the open 3D sandstone doorway
    gate = outer * (1.0 - opening_blur) + inner * opening_blur

    # Perspective-warp the Left & Right 3D Carved Teak-and-Gold Doors so they appear swung open at 65 degrees!
    lh_d, lw_d = left_door_crop.shape[:2]
    # Left door swung inward (foreshortened width from x=136..225)
    src_pts_l = np.float32([[0, 0], [lw_d, 0], [lw_d, lh_d], [0, lh_d]])
    dst_pts_l = np.float32([[136, 200], [220, 255], [220, 1070], [136, 1120]])
    M_l = cv2.getPerspectiveTransform(src_pts_l, dst_pts_l)
    warped_l = cv2.warpPerspective(left_door_crop, M_l, (W, H))
    mask_l = cv2.warpPerspective(np.ones((lh_d, lw_d), dtype=np.float32), M_l, (W, H))[:, :, None]
    mask_l = mask_l * opening_blur

    # Right door swung inward (foreshortened width from x=548..632)
    src_pts_r = np.float32([[0, 0], [lw_d, 0], [lw_d, lh_d], [0, lh_d]])
    dst_pts_r = np.float32([[548, 255], [632, 200], [632, 1120], [548, 1070]])
    M_r = cv2.getPerspectiveTransform(src_pts_r, dst_pts_r)
    warped_r = cv2.warpPerspective(right_door_crop, M_r, (W, H))
    mask_r = cv2.warpPerspective(np.ones((lh_d, lw_d), dtype=np.float32), M_r, (W, H))[:, :, None]
    mask_r = mask_r * opening_blur

    gate = gate * (1.0 - mask_l) + warped_l.astype(np.float32) * 0.85 * mask_l
    gate = gate * (1.0 - mask_r) + warped_r.astype(np.float32) * 0.85 * mask_r

    # Add warm golden floor light spilling out from the open doorway onto the carved stone floor (y=1080..1376)
    floor_spill = np.exp(-((xx - 384.0) / 220.0) ** 2) * np.exp(-((yy - 1140.0) / 180.0) ** 2) * (yy > 1020)
    gate[:, :, 0] += floor_spill * 40.0
    gate[:, :, 1] += floor_spill * 165.0
    gate[:, :, 2] += floor_spill * 245.0

    gate_u8 = np.clip(gate, 0, 255).astype(np.uint8)
    overlay_rgba_sprite(gate_u8, lantern_rgba, 305, 315, 0.90, 0, 0.95)
    overlay_rgba_sprite(gate_u8, lantern_rgba, 465, 315, 0.90, 0, 0.95)
    overlay_rgba_sprite(gate_u8, marigold_1, 175, 960, 0.80, 15, 0.90)
    overlay_rgba_sprite(gate_u8, rose_1, 595, 975, 0.80, -18, 0.90)
    return gate_u8

venue_gate_3d = build_3d_open_palace_gate()
cv2.imwrite(os.path.join(OUT_DIR, "venue_palace_3d.jpg"), venue_gate_3d, [cv2.IMWRITE_JPEG_QUALITY, 94])

# Also save close-up hands with "DC" mehendi inside the 3D Golden Arch for Finale / Blessing Altar!
mix_2572 = load_upright_bgr(os.path.join("bride_groom_mix", "5M5A2572.JPG"))
finale_altar_3d = composite_into_3d_palace(
    mix_2572, stage_wedding,
    crop_box=(0.05, 0.0, 0.95, 1.0),
    dest_box=(82, 340, 686, 1140),
    mode="outdoor", theme="wedding", variant=0
)
cv2.imwrite(os.path.join(OUT_DIR, "finale_altar_3d.jpg"), finale_altar_3d, [cv2.IMWRITE_JPEG_QUALITY, 94])

# ---------------------------------------------------------
# 7. GENERATE 3D DEPTH MAPS FOR WEBGL 3D PARALLAX SHADER
# ---------------------------------------------------------
def create_3d_depth_map(img_bgr, has_center_subject=True):
    yy, xx = np.mgrid[0:H, 0:W]
    nx = (xx - W / 2.0) / (W / 2.0)
    ny = (yy - H / 2.0) / (H / 2.0)

    # Outer 3D architectural portal (columns, top arch, bottom balustrade) is closest to camera (0.85..1.0)
    depth = portal_mask.copy() * 0.92

    if has_center_subject:
        # Subject 3D dome in center (x=150..618, y=310..1150) at mid-foreground depth (0.50..0.76)
        sx = (xx - 384.0) / 235.0
        sy = (yy - 730.0) / 410.0
        subj_dome = np.clip(1.0 - (sx * sx + sy * sy), 0, 1) ** 0.65 * 0.72
        depth = np.maximum(depth, subj_dome)

    # Add fine local 3D relief from luminance gradients
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    relief = cv2.GaussianBlur(gray, (15, 15), 0) * 0.16
    depth = np.clip(depth + relief, 0, 1)
    depth = cv2.GaussianBlur(depth, (31, 31), 0)
    return (depth * 255).astype(np.uint8)

for fname, has_subj in [
    ("scene1_door_unlit.jpg", True),
    ("scene1_door_lit_1.jpg", True),
    ("sanctum_3d_1.jpg", True),
    ("bride_3d_1.jpg", True),
    ("groom_3d_1.jpg", True),
    ("haldi_3d_1.jpg", True),
    ("wedding_3d_1.jpg", True),
    ("venue_palace_3d.jpg", False),
    ("finale_altar_3d.jpg", True),
]:
    im = cv2.imread(os.path.join(OUT_DIR, fname))
    dmap = create_3d_depth_map(im, has_subj)
    dname = fname.replace(".jpg", "_depth.jpg")
    cv2.imwrite(os.path.join(OUT_DIR, dname), dmap, [cv2.IMWRITE_JPEG_QUALITY, 90])

print("ALL 3D FRAMES AND DEPTH MAPS GENERATED SUCCESSFULLY!")
