import os
import cv2
import numpy as np

BRAIN_DIR = r"C:\Users\Asus\.gemini\antigravity\brain\41d6c376-34ae-4c6b-a1e5-025b91ae9ffa"
OUT_DIR = r"d:\biu_app_clone_13_1_2026\biu_app\wedding_invitation\assets"
os.makedirs(OUT_DIR, exist_ok=True)

DOOR_3D_PATH = os.path.join(BRAIN_DIR, "scene_1a_unlit_door_samai_1795073477628.jpg")
GROOM_3D_PATH = os.path.join(BRAIN_DIR, "groom_royal_jharokha_3d_1795073528118.jpg")

door_bgr = cv2.imread(DOOR_3D_PATH)
groom_bgr = cv2.imread(GROOM_3D_PATH)

# 1. Extract the real 3D Carved Golden Lotus Medallion from door_bgr (x=196..340, y=870..1014)
lotus_med = door_bgr[870:1014, 196:340].copy()
mh, mw = lotus_med.shape[:2]
yy, xx = np.mgrid[0:mh, 0:mw]
dist = np.sqrt(((xx - mw / 2.0) / (mw / 2.0)) ** 2 + ((yy - mh / 2.0) / (mh / 2.0)) ** 2)
alpha = np.clip((1.05 - dist) * 6.0, 0, 1)
# Boost golden specular brightness
lotus_f = lotus_med.astype(np.float32)
lotus_f[:, :, 0] *= 1.05
lotus_f[:, :, 1] *= 1.25
lotus_f[:, :, 2] *= 1.38
lotus_rgba = cv2.cvtColor(np.clip(lotus_f, 0, 255).astype(np.uint8), cv2.COLOR_BGR2BGRA)
lotus_rgba[:, :, 3] = (alpha * 255).astype(np.uint8)
cv2.imwrite(os.path.join(OUT_DIR, "medallion_lotus_3d.png"), lotus_rgba)

# 2. Extract the real 3D Carved Teakwood & Gold Corner Plaque from door_bgr
# In door_bgr, x=176..356, y=575..748 has a 3D carved wood panel with 4 ornate 3D gold floral corners and a brass ring in the middle.
# If we take the outer 3D carved gold corners and replace the center ring with clean 3D carved dark teakwood grain,
# we get an authentic 3D Octane-rendered Rajwada Teak-and-Gold Inscription Plaque!
panel = door_bgr[575:748, 176:356].copy()
ph, pw = panel.shape[:2]
# Scale up to 640x360 plaque while keeping corners crisp
plaque = cv2.resize(panel, (640, 360), interpolation=cv2.INTER_CUBIC).astype(np.float32)
# Replace center circular ring region (x=150..490, y=65..295) with smooth 3D dark carved wood grain from door_bgr[815:865, 195:345]
wood_grain = cv2.resize(door_bgr[818:862, 195:345], (380, 250), interpolation=cv2.INTER_CUBIC).astype(np.float32) * 0.78
cmask = np.zeros((360, 640), dtype=np.float32)
cmask[55:305, 130:510] = 1.0
cmask = cv2.GaussianBlur(cmask, (51, 51), 0)[:, :, None]
plaque_center = plaque.copy()
plaque_center[55:305, 130:510] = wood_grain
plaque = plaque * (1.0 - cmask) + plaque_center * cmask
# Enhance 3D gold corner relief
plaque[:, :, 1] *= 1.15
plaque[:, :, 2] *= 1.28
cv2.imwrite(os.path.join(OUT_DIR, "plaque_teak_gold_3d.jpg"), np.clip(plaque, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94])

print("Extracted real 3D Lotus Medallion and 3D Carved Teak-and-Gold Plaque textures.")
