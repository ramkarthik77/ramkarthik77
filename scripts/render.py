#!/usr/bin/env python3
"""Regenerate profile contribution graphics using authenticated GitHub GraphQL."""
import datetime as dt
import html
import json
import os
from pathlib import Path
import urllib.request

USER = os.getenv("PROFILE_USER", "ramkarthik77")
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
ROOT = Path(__file__).resolve().parent.parent
if not TOKEN:
    raise SystemExit("GH_TOKEN is required to fetch real contribution statistics")

query = """query($login:String!){
 user(login:$login){
   contributionsCollection{
     contributionCalendar{
       totalContributions
       weeks { contributionDays { date contributionCount color } }
     }
   }
 }
}"""
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query, "variables": {"login": USER}}).encode(),
    headers={
        "Authorization": "Bearer " + TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
        "User-Agent": "ramkarthik77-profile-renderer",
    },
)
with urllib.request.urlopen(req, timeout=30) as response:
    payload = json.load(response)
if payload.get("errors"):
    raise SystemExit("GitHub GraphQL returned errors: " + str(payload["errors"]))
user = (payload.get("data") or {}).get("user")
if not user:
    raise SystemExit("GitHub user missing from GraphQL response")
calendar = user["contributionsCollection"]["contributionCalendar"]
weeks = calendar["weeks"]
days = [day for week in weeks for day in week["contributionDays"]]
total = calendar["totalContributions"]
active = sum(day["contributionCount"] > 0 for day in days)
peak = max((day["contributionCount"] for day in days), default=0)
today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d UTC")

def svg(width, height, inner):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
<rect width="{width}" height="{height}" rx="18" fill="#08111e"/>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="17" stroke="#20435f" fill="none"/>
<g font-family="Arial,Helvetica,sans-serif">{inner}</g></svg>"""

def text(x, y, content, size=18, fill="#e8f4ff", weight="normal"):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}">{html.escape(str(content))}</text>'

activity = (
    text(48, 44, "ENGINEERING TELEMETRY  /  VERIFIED GITHUB DATA", 15, "#57e7ff")
    + text(48, 102, f"{total:,}", 47, weight="bold")
    + text(48, 132, "CONTRIBUTIONS / LAST YEAR", 13, "#8da8c5")
    + text(472, 102, active, 47, weight="bold")
    + text(472, 132, "ACTIVE DAYS", 13, "#8da8c5")
    + text(770, 102, peak, 47, weight="bold")
    + text(770, 132, "BUSIEST DAY", 13, "#8da8c5")
    + text(48, 183, "LAST SYNC: " + today, 14, "#8da8c5")
)
(ROOT / "assets/activity.svg").write_text(svg(1200, 218, activity), encoding="utf-8")
cells = []
palette = ["#152f43", "#1c5670", "#287fa0", "#4bb8d1", "#a0f5ff"]
for w, week in enumerate(weeks[-53:]):
    for i, day in enumerate(week["contributionDays"]):
        count = day["contributionCount"]
        level = 0 if count == 0 else 1 if count <= 2 else 2 if count <= 5 else 3 if count <= 10 else 4
        cells.append(f'<rect x="{40+w*21}" y="{81+i*17}" width="14" height="12" rx="2" fill="{palette[level]}"><title>{html.escape(day["date"])}: {count} contributions</title></rect>')
matrix = (
    text(40, 36, "CONTRIBUTION MATRIX  /  LAST 12 MONTHS", 16, "#57e7ff")
    + text(905, 36, f"{total:,} CONTRIBUTIONS", 14, "#8da8c5")
    + "".join(cells)
)
(ROOT / "assets/contributions.svg").write_text(svg(1200, 220, matrix), encoding="utf-8")
print(f"Generated contribution SVGs: {total} contributions, {active} active days")
