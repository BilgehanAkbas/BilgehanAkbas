"""
Prep a source photo for ASCII conversion:
1. Remove background with rembg -> isolates the subject.
2. Boost local contrast with OpenCV CLAHE -> real highlights/shadows.
3. Composite onto pure white -> background maps to blank end of ramp.
Run once per photo; writes source-prepped.png.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) < 2:
        print("usage: python prep_photo.py <photo.jpg>")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    img = Image.open(src_path).convert("RGB")

    # 1. remove background
    cutout = remove(img)  # RGBA

    # 2. CLAHE contrast boost on the subject (grayscale)
    rgba = np.array(cutout)
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray)

    # 3. composite onto pure white using alpha mask
    white_bg = np.full_like(gray_eq, 255)
    mask = alpha.astype(np.float32) / 255.0
    composited = (gray_eq.astype(np.float32) * mask + white_bg.astype(np.float32) * (1 - mask))
    composited = composited.astype(np.uint8)

    out = Image.fromarray(composited, mode="L")
    out_path = ROOT / "source-prepped.png"
    out.save(out_path)
    print(f"wrote {out_path} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    main()
