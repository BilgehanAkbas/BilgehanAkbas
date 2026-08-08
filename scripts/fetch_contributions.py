"""
Fetch a GitHub user's public contribution calendar HTML fragment
(no token needed) and store parsed data + derived stats as JSON.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "BilgehanAkbas"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, timeout=20, headers={"User-Agent": "profile-readme-bot"})
    resp.raise_for_status()
    return resp.text


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")
    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        level = td.get("data-level")
        if date is None or level is None:
            continue
        days.append({"date": date, "level": int(level)})
    if not days:
        # newer markup uses <rect> / <li> tool-tips instead of <td>; fall back
        for cell in soup.select("[data-date]"):
            date = cell.get("data-date")
            level = cell.get("data-level")
            if date and level is not None:
                days.append({"date": date, "level": int(level)})
    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days):
    total = len(days)
    contributed_days = sum(1 for d in days if d["level"] > 0)

    # current streak (from most recent day backwards)
    current_streak = 0
    for d in reversed(days):
        if d["level"] > 0:
            current_streak += 1
        else:
            break

    # longest streak
    longest = 0
    running = 0
    for d in days:
        if d["level"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["level"]) if days else None

    monthly = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + (1 if d["level"] > 0 else 0)

    return {
        "total_cells": total,
        "contributed_days": contributed_days,
        "current_streak": current_streak,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_active_days": monthly,
    }


def main():
    try:
        html = fetch_html(USERNAME)
        days = parse_days(html)
        if not days:
            raise ValueError("no contribution cells parsed")
    except Exception as e:
        print(f"[warn] live fetch failed ({e}); writing empty scaffold", file=sys.stderr)
        days = []

    stats = derive_stats(days)
    payload = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"wrote {OUT_PATH} ({len(days)} days)")


if __name__ == "__main__":
    main()
