"""
Hand-authored neofetch-style SVG info card.
Lines fade + slide in on a short stagger (CSS keyframes, plays once).
"""
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "info-card.svg"

TITLE = "bilgehan@github"
ROWS = [
    ("OS", "Gazi Üniversitesi · Bilgisayar Müh."),
    ("Year", "3. Sınıf (2023 – 2028)"),
    ("Role", "Başkan Yrd. @ Gazi YZ Topluluğu"),
    ("Stack", "Python · C · C# · Java · ESP32"),
    ("Focus", "Siber Güvenlik · Gömülü Sistemler · AI"),
    ("Certs", "CyberOps Assoc. · CCNA · BTK Akademi"),
    ("Now", "ESP32 ağ güvenliği + AI/CV projeleri"),
]

WIDTH = 490
LINE_H = 26
TOP_PAD = 54
LEFT_PAD = 22


def main():
    rows_svg = []
    for i, (key, val) in enumerate(ROWS):
        y = TOP_PAD + i * LINE_H
        delay = 0.15 + i * 0.12
        rows_svg.append(
            f'<g class="row" style="animation-delay:{delay:.2f}s">'
            f'<text x="{LEFT_PAD}" y="{y}" class="key">{key}</text>'
            f'<text x="{LEFT_PAD + 70}" y="{y}" class="val">{val}</text>'
            f"</g>"
        )

    height = TOP_PAD + len(ROWS) * LINE_H + 24

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}"
     viewBox="0 0 {WIDTH} {height}" font-family="'Fira Code', 'Courier New', monospace">
  <style>
    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; }}
    .titlebar {{ fill: #161b22; }}
    .dot {{ }}
    .title {{ fill: #8b949e; font-size: 12px; }}
    .key {{ fill: #58a6ff; font-size: 13px; font-weight: 600; }}
    .val {{ fill: #c9d1d9; font-size: 13px; }}
    .row {{
      opacity: 0;
      transform: translateX(-8px);
      animation: fadeSlide 0.45s ease-out forwards;
    }}
    @keyframes fadeSlide {{
      from {{ opacity: 0; transform: translateX(-8px); }}
      to   {{ opacity: 1; transform: translateX(0); }}
    }}
  </style>
  <rect class="bg" x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8" />
  <rect class="titlebar" x="0.5" y="0.5" width="{WIDTH - 1}" height="30" rx="8" />
  <rect x="0.5" y="22" width="{WIDTH - 1}" height="8" fill="#161b22" />
  <circle class="dot" cx="20" cy="16" r="5" fill="#ff5f56" />
  <circle class="dot" cx="38" cy="16" r="5" fill="#ffbd2e" />
  <circle class="dot" cx="56" cy="16" r="5" fill="#27c93f" />
  <text x="{WIDTH / 2}" y="20" text-anchor="middle" class="title">{TITLE} — neofetch</text>
  {''.join(rows_svg)}
</svg>
"""
    OUT_PATH.write_text(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
