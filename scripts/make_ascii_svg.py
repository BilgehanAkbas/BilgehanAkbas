"""
Convert source-prepped.png into a self-typing, monochrome ASCII-art SVG.
Each row wipes left-to-right, staggered top to bottom, then freezes.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "me-ascii.svg"

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense); leading space clears bg
COLS = 90
CHAR_W = 6.1
CHAR_H = 11
FONT_SIZE = 11


def image_to_grid(path: Path, cols: int):
    img = Image.open(path).convert("L")
    w, h = img.size
    # monospace cells are taller than wide -> compensate aspect ratio
    aspect = 0.55
    cell_w = w / cols
    rows = int((h / cell_w) * aspect)
    img_small = img.resize((cols, max(rows, 1)), Image.LANCZOS)
    arr = np.array(img_small, dtype=np.float32)
    return arr


def brightness_to_char(v: float) -> str:
    # v: 0 (black) .. 255 (white). Bright -> sparse (space), dark -> dense.
    idx = int((255 - v) / 255 * (len(RAMP) - 1))
    idx = max(0, min(len(RAMP) - 1, idx))
    return RAMP[idx]


def main():
    if not SRC.exists():
        print(f"missing {SRC}; run prep_photo.py first")
        return

    grid = image_to_grid(SRC, COLS)
    rows, cols = grid.shape

    width = cols * CHAR_W + 20
    height = rows * CHAR_H + 20

    row_svgs = []
    row_delay_step = 0.09
    for r in range(rows):
        line_chars = [brightness_to_char(grid[r, c]) for c in range(cols)]
        line = "".join(line_chars).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # collapse trailing spaces for cleanliness but keep leading structure
        y = 10 + (r + 1) * CHAR_H
        clip_id = f"clip{r}"
        delay = r * row_delay_step
        row_width = cols * CHAR_W
        row_svgs.append(f"""
    <clipPath id="{clip_id}">
      <rect x="0" y="{y - CHAR_H}" width="{row_width}" height="{CHAR_H}" class="wipe" style="animation-delay:{delay:.2f}s" />
    </clipPath>""")
        row_svgs.append(
            f'<text x="10" y="{y}" xml:space="preserve" font-family="'
            f'\'Courier New\', monospace" font-size="{FONT_SIZE}" '
            f'fill="#c9d1d9" clip-path="url(#{clip_id})">{line}</text>'
        )

    defs = "".join(s for s in row_svgs if s.strip().startswith("<clipPath") or "<clipPath" in s)
    texts = "\n  ".join(s for s in row_svgs if s.strip().startswith("<text"))
    clip_defs = "\n  ".join(s for s in row_svgs if "<clipPath" in s)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}"
     viewBox="0 0 {width:.0f} {height:.0f}">
  <style>
    .bg {{ fill: #0d1117; }}
    rect.wipe {{
      transform: scaleX(0);
      transform-box: fill-box;
      transform-origin: left;
      animation: wipeIn 0.35s steps(24) forwards;
    }}
    @keyframes wipeIn {{
      from {{ transform: scaleX(0); }}
      to   {{ transform: scaleX(1); }}
    }}
  </style>
  <rect class="bg" x="0" y="0" width="{width:.0f}" height="{height:.0f}" rx="6" />
  <defs>
  {clip_defs}
  </defs>
  {texts}
</svg>
"""
    OUT.write_text(svg)
    print(f"wrote {OUT} ({cols}x{rows} grid)")


if __name__ == "__main__":
    main()
