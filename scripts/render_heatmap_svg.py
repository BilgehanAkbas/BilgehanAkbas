"""
Render the contributions.json calendar as a self-contained animated SVG:
53-week x 7-day grid of rounded boxes that slide in diagonally, once,
using pure CSS keyframes (GitHub renders SMIL/CSS inside <img>-embedded SVGs).
"""
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
OUT_PATH = Path(__file__).resolve().parent.parent / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 40
BOTTOM_PAD = 34


def load():
    payload = json.loads(DATA_PATH.read_text())
    return payload


def build_weeks(days):
    """Group days into GitHub-style weeks starting on Sunday."""
    by_date = {d["date"]: d["level"] for d in days}
    if not days:
        return []
    dates = sorted(datetime.strptime(d["date"], "%Y-%m-%d") for d in days)
    start, end = dates[0], dates[-1]
    # back up start to the preceding Sunday
    start_sun = start
    while start_sun.weekday() != 6:  # Monday=0 ... Sunday=6
        start_sun = start_sun.fromordinal(start_sun.toordinal() - 1)

    weeks = []
    cur = start_sun
    week = []
    while cur <= end:
        key = cur.strftime("%Y-%m-%d")
        level = by_date.get(key, 0)
        week.append((key, level))
        if cur.weekday() == 6 and week:
            weeks.append(week)
            week = []
        cur = cur.fromordinal(cur.toordinal() + 1)
    if week:
        weeks.append(week)
    return weeks


def month_labels(weeks):
    labels = []
    seen = set()
    for i, week in enumerate(weeks):
        first_valid = next((d for d in week if d[1] is not None), None)
        if not first_valid:
            continue
        dt = datetime.strptime(week[0][0], "%Y-%m-%d")
        key = (dt.year, dt.month)
        if dt.day <= 7 and key not in seen:
            seen.add(key)
            labels.append((i, dt.strftime("%b")))
    return labels


def main():
    payload = load()
    days = payload.get("days", [])
    stats = payload.get("stats", {})
    weeks = build_weeks(days)

    n_weeks = max(len(weeks), 1)
    width = LEFT_PAD + n_weeks * (CELL + GAP) + 20
    height = TOP_PAD + 7 * (CELL + GAP) + BOTTOM_PAD

    rects = []
    delay_step = 0.012
    idx = 0
    for wi, week in enumerate(weeks):
        for di, (date, level) in enumerate(week):
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + di * (CELL + GAP)
            color = PALETTE[min(level, len(PALETTE) - 1)]
            delay = (wi + di) * delay_step
            rects.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2.5" ry="2.5" fill="{color}" '
                f'style="animation-delay:{delay:.3f}s" data-date="{date}">'
                f"<title>{date}: level {level}</title></rect>"
            )
            idx += 1

    labels = month_labels(weeks)
    label_svgs = [
        f'<text x="{LEFT_PAD + wi * (CELL + GAP)}" y="{TOP_PAD - 12}" '
        f'class="month-label">{name}</text>'
        for wi, name in labels
    ]

    contributed = stats.get("contributed_days", 0)
    current_streak = stats.get("current_streak", 0)
    longest_streak = stats.get("longest_streak", 0)
    footer_text = (
        f"{contributed} contribution days in the last year · "
        f"current streak {current_streak} · longest streak {longest_streak}"
    )

    legend_x = width - 150
    legend_y = height - 14
    legend_swatches = "".join(
        f'<rect x="{legend_x + i * 14}" y="{legend_y - 10}" width="10" height="10" '
        f'rx="2" fill="{c}" />'
        for i, c in enumerate(PALETTE)
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" font-family="'Segoe UI', Ubuntu, Helvetica, Arial, sans-serif">
  <style>
    .bg {{ fill: #0d1117; }}
    .cell {{
      opacity: 0;
      transform: translate(-6px, -6px);
      animation: slideIn 0.5s ease-out forwards;
    }}
    @keyframes slideIn {{
      from {{ opacity: 0; transform: translate(-6px, -6px); }}
      to   {{ opacity: 1; transform: translate(0, 0); }}
    }}
    .month-label {{ fill: #8b949e; font-size: 10px; }}
    .footer {{ fill: #c9d1d9; font-size: 11px; }}
    .legend-label {{ fill: #8b949e; font-size: 9px; }}
  </style>
  <rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="6" />
  {''.join(label_svgs)}
  {''.join(rects)}
  <text x="{LEFT_PAD}" y="{height - 12}" class="footer">{footer_text}</text>
  <text x="{legend_x - 34}" y="{legend_y - 2}" class="legend-label">Less</text>
  {legend_swatches}
  <text x="{legend_x + len(PALETTE) * 14 + 4}" y="{legend_y - 2}" class="legend-label">More</text>
</svg>
"""
    OUT_PATH.write_text(svg)
    print(f"wrote {OUT_PATH} ({n_weeks} weeks, {idx} cells)")


if __name__ == "__main__":
    main()
