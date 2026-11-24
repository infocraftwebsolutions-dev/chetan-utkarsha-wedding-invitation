import os
import cv2
import numpy as np
from PIL import Image

BRAIN_DIR = r"C:\Users\Asus\.gemini\antigravity\brain\41d6c376-34ae-4c6b-a1e5-025b91ae9ffa"
DOOR_3D_PATH = os.path.join(BRAIN_DIR, "scene_1a_unlit_door_samai_1795073477628.jpg")
BRIDE_3D_PATH = os.path.join(BRAIN_DIR, "bride_royal_jharokha_3d_1795073496764.jpg")
GROOM_3D_PATH = os.path.join(BRAIN_DIR, "groom_royal_jharokha_3d_1795073528118.jpg")

for name, path in [("door", DOOR_3D_PATH), ("bride", BRIDE_3D_PATH), ("groom", GROOM_3D_PATH)]:
    img = cv2.imread(path)
    print(name, img.shape)
