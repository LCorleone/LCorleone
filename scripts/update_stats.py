#!/usr/bin/env python3
"""Render the Cyber-HUD GitHub telemetry cards (assets/stats-{dark,light}.svg).

Standard library only: urllib + json for the API calls, no third-party deps.

Token handling
--------------
* ``ACCESS_TOKEN`` (personal token) or ``GITHUB_TOKEN`` (Actions) in the
  environment is used when present. GraphQL needs a token at all, so without
  one the REST endpoint is called anonymously and every GraphQL-only field
  degrades to ``n/a`` instead of crashing the build.
* Repo scope is pinned to ``privacy: PUBLIC`` even when a token is available:
  these cards are embedded in a public profile README, so private repo counts
  must never leak into them, and the numbers stay identical between a local
  render and the scheduled Action run. A token is only used for auth / higher
  rate limits and to reach the GraphQL endpoint.

Usage
-----
    python3 scripts/update_stats.py              # live fetch, writes both SVGs
    python3 scripts/update_stats.py --fixture scripts/fixtures/sample.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

LOGIN = "LCorleone"
SCOPE = "PUBLIC"
API_ROOT = "https://api.github.com"
REST_USER_URL = f"{API_ROOT}/users/{LOGIN}"
GRAPHQL_URL = f"{API_ROOT}/graphql"
HTTP_TIMEOUT = 25
MONTHS = 12

OUT_DIR = Path(__file__).resolve().parent.parent / "assets"

# --------------------------------------------------------------------------
# Canvas geometry (matches the 900px native width of hero / architecture)
# --------------------------------------------------------------------------
WIDTH, HEIGHT = 900, 420
CONTENT_LEFT, CONTENT_RIGHT = 36, 864
CONTENT_WIDTH = CONTENT_RIGHT - CONTENT_LEFT  # 828

TILE_GUTTER = 18
TILE_W = (CONTENT_WIDTH - 2 * TILE_GUTTER) // 3  # 264
TILE_H = 94
TILE_X = [CONTENT_LEFT, CONTENT_LEFT + TILE_W + TILE_GUTTER,
          CONTENT_LEFT + 2 * (TILE_W + TILE_GUTTER)]
TILE_Y = [70, 176]

BAR_W = 44.0
BAR_STEP = (CONTENT_WIDTH - BAR_W) / (MONTHS - 1)  # 71.27, fills x=36..864
BAR_BASE = 352.0
BAR_MAX_H = 52.0  # tallest bar tops out at y=300

DARK = {
    "bg0": "#070B14", "bg1": "#0F172A", "bg2": "#070B14",
    "border0": "#38BDF8", "border1": "#1E293B", "border2": "#10B981",
    "cyan": "#38BDF8", "emerald": "#10B981", "amber": "#F59E0B",
    "violet": "#A855F7",
    "text": "#E2E8F0", "muted": "#64748B",
    "grid": "#1E293B", "grid_dot": "#334155", "divider": "#1E293B",
    "tile": "#0B1120", "scan0": "#38BDF8", "scan1": "#10B981",
    "glow_cyan": "#38BDF8", "glow_emerald": "#10B981", "glow_violet": "#A855F7",
    "glow_a": "0.15", "glow_b": "0.11", "glow_c": "0.08",
    "pulse0": "#A855F7", "pulse1": "#38BDF8",
}

LIGHT = {
    "bg0": "#F8FAFC", "bg1": "#FFFFFF", "bg2": "#F1F5F9",
    "border0": "#0284C7", "border1": "#CBD5E1", "border2": "#059669",
    "cyan": "#0284C7", "emerald": "#059669", "amber": "#D97706",
    "violet": "#7C3AED",
    "text": "#0F172A", "muted": "#475569",
    "grid": "#E2E8F0", "grid_dot": "#94A3B8", "divider": "#CBD5E1",
    "tile": "#FFFFFF", "scan0": "#0284C7", "scan1": "#059669",
    "glow_cyan": "#0284C7", "glow_emerald": "#059669", "glow_violet": "#7C3AED",
    "glow_a": "0.08", "glow_b": "0.07", "glow_c": "0.05",
    "pulse0": "#7C3AED", "pulse1": "#0284C7",
}

PALETTES = {"dark": DARK, "light": LIGHT}


# ==========================================================================
# small helpers
# ==========================================================================
def _warn(message: str) -> None:
    print(f"[stats] {message}", file=sys.stderr)


def _num(value):
    """Coerce an API value to int, or None when it is unavailable."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _trim_float(value: float) -> str:
    return f"{value:.1f}".removesuffix(".0")


def fmt_count(value) -> str:
    """Integer with thousands separators; compacted above 6 digits.

    100000+ would overflow a 30px tile, so it is pre-shrunk (``12.3k``).
    Missing data renders ``n/a``; real zero renders ``0`` (never blank).
    """
    if value is None:
        return "n/a"
    number = int(value)
    sign = "-" if number < 0 else ""
    number = abs(number)
    if number >= 1_000_000:
        return f"{sign}{_trim_float(number / 1_000_000)}m"
    if number >= 100_000:
        return f"{sign}{_trim_float(number / 1_000)}k"
    return f"{sign}{number:,}"


def truncate(text, limit: int) -> str:
    """Collapse whitespace and clip so a sub-note can never overflow a tile."""
    clean = " ".join(str(text).split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "\u2026"


def parse_iso(text):
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def add_months(dt: datetime, delta: int) -> datetime:
    total = dt.year * 12 + (dt.month - 1) + delta
    year, month = divmod(total, 12)
    return dt.replace(year=year, month=month + 1, day=1)


def month_starts(now: datetime):
    """The 12 month windows ending with the current (partial) month."""
    current = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return [add_months(current, offset) for offset in range(-11, 1)]


def empty_data() -> dict:
    return {
        "login": LOGIN,
        "public_repos": None,
        "repo_total": None,
        "total_stars": None,
        "followers": None,
        "commits_12m": None,
        "contributed_to": None,
        "last_push_at": None,
        "last_push_repo": None,
        "window_label": None,
        "months": [],
        "rendered_at": None,
    }


# ==========================================================================
# GitHub data
# ==========================================================================
def resolve_token():
    return os.environ.get("ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN") or None


def _headers(token):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{LOGIN}-stats-card",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_json(url, token):
    request = urllib.request.Request(url, headers=_headers(token))
    with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _post_json(url, payload, token):
    body = json.dumps(payload).encode("utf-8")
    headers = dict(_headers(token))
    headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def build_query(months: int = MONTHS, scope: str = SCOPE) -> str:
    declarations = ["$login: String!", "$from: DateTime!", "$to: DateTime!"]
    month_fields = []
    for index in range(months):
        declarations.append(f"$m{index}From: DateTime!")
        declarations.append(f"$m{index}To: DateTime!")
        month_fields.append(
            f"    m{index}: contributionsCollection(from: $m{index}From, to: $m{index}To) "
            "{ contributionCalendar { totalContributions } }"
        )
    return f"""query Stats({", ".join(declarations)}) {{
  user(login: $login) {{
    followers {{ totalCount }}
    repositories(first: 100, ownerAffiliations: OWNER, privacy: {scope}) {{
      totalCount
      nodes {{ name stargazerCount isFork pushedAt }}
    }}
    repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY]) {{
      totalCount
    }}
    window: contributionsCollection(from: $from, to: $to) {{
      totalCommitContributions
      restrictedContributionsCount
    }}
{chr(10).join(month_fields)}
  }}
}}
"""


def build_variables(now: datetime) -> dict:
    starts = month_starts(now)
    variables = {"login": LOGIN, "from": iso(starts[0]), "to": iso(now)}
    for index, start in enumerate(starts):
        end = add_months(start, 1)
        variables[f"m{index}From"] = iso(start)
        variables[f"m{index}To"] = iso(min(end, now))
    return variables


def fetch_rest(token) -> dict:
    """Public REST payload: works anonymously (60 req/h unauthenticated)."""
    try:
        user = _get_json(REST_USER_URL, token)
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError) as exc:
        _warn(f"REST lookup failed: {exc}")
        return {}
    return {
        "public_repos": _num(user.get("public_repos")),
        "followers": _num(user.get("followers")),
    }


def fetch_graphql(token, now: datetime) -> dict:
    if not token:
        _warn("no ACCESS_TOKEN/GITHUB_TOKEN: skipping GraphQL fields (rendered as n/a)")
        return {}
    try:
        payload = _post_json(
            GRAPHQL_URL,
            {"query": build_query(), "variables": build_variables(now)},
            token,
        )
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError) as exc:
        _warn(f"GraphQL lookup failed: {exc}")
        return {}

    for error in payload.get("errors") or []:
        _warn(f"GraphQL error: {error.get('message', error)}")
    user = (payload.get("data") or {}).get("user") or {}

    collected = {}

    followers = _num((user.get("followers") or {}).get("totalCount"))
    if followers is not None:
        collected["followers"] = followers

    contributed = _num((user.get("repositoriesContributedTo") or {}).get("totalCount"))
    if contributed is not None:
        collected["contributed_to"] = contributed

    repositories = user.get("repositories") or {}
    repo_total = _num(repositories.get("totalCount"))
    if repo_total is not None:
        collected["repo_total"] = repo_total

    stars = 0
    stars_seen = False
    newest_push = None
    newest_repo = None
    for node in repositories.get("nodes") or []:
        count = _num(node.get("stargazerCount"))
        # Forks re-host someone else's stars: only count owned repos.
        if count is not None and not node.get("isFork"):
            stars += count
            stars_seen = True
        pushed = parse_iso(node.get("pushedAt"))
        if pushed is not None and (newest_push is None or pushed > newest_push):
            newest_push, newest_repo = pushed, node.get("name")
    if stars_seen:
        collected["total_stars"] = stars
    if newest_push is not None:
        collected["last_push_at"] = iso(newest_push)
        collected["last_push_repo"] = newest_repo

    window = user.get("window") or {}
    commits = _num(window.get("totalCommitContributions"))
    restricted = _num(window.get("restrictedContributionsCount"))
    if commits is not None or restricted is not None:
        collected["commits_12m"] = (commits or 0) + (restricted or 0)

    starts = month_starts(now)
    month_buckets = []
    for index, start in enumerate(starts):
        calendar = ((user.get(f"m{index}") or {}).get("contributionCalendar")) or {}
        month_buckets.append(
            {"label": start.strftime("%b").upper(), "count": _num(calendar.get("totalContributions"))}
        )
    collected["months"] = month_buckets
    collected["window_label"] = (
        f"{starts[0].strftime('%b').upper()} {starts[0].year} \u2013 "
        f"{starts[-1].strftime('%b').upper()} {starts[-1].year}"
    )
    return collected


def fetch_live(token, now: datetime) -> dict:
    data = empty_data()
    with ThreadPoolExecutor(max_workers=2) as pool:
        rest = pool.submit(fetch_rest, token)
        graph = pool.submit(fetch_graphql, token, now)
        for part in (rest.result(), graph.result()):
            for key, value in part.items():
                if value is None:
                    continue
                if key == "months" and not value:
                    continue
                data[key] = value
    return data


def load_fixture(path: Path) -> dict:
    """Render from a local JSON snapshot so the SVG can be validated offline."""
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    data = empty_data()
    data.update({key: value for key, value in raw.items() if key in data})
    months = []
    for index, entry in enumerate(data.get("months") or []):
        if isinstance(entry, dict):
            months.append({"label": str(entry.get("label", "")), "count": _num(entry.get("count"))})
        else:
            months.append({"label": f"M{index + 1}", "count": _num(entry)})
    data["months"] = months[:MONTHS]
    return data


# ==========================================================================
# SVG rendering
# ==========================================================================
def _style_block(suffix: str) -> str:
    return f"""  <style>
    .mono {{
      font-family: 'JetBrains Mono', 'Fira Code', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    }}
    .sans {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}
    .pulse-dot {{
      animation: statsPulseGlow{suffix} 2.2s ease-in-out infinite;
    }}
    .pulse-ring {{
      transform-origin: center;
      transform-box: fill-box;
      animation: statsRingExpand{suffix} 2.2s ease-out infinite;
    }}
    .scan-beam {{
      animation: statsScanSweep{suffix} 6.5s ease-in-out infinite;
    }}
    .led-1 {{ animation: statsBlinkLed{suffix} 2.6s ease-in-out infinite 0s; }}
    .led-2 {{ animation: statsBlinkLed{suffix} 2.6s ease-in-out infinite 0.65s; }}
    .led-3 {{ animation: statsBlinkLed{suffix} 2.6s ease-in-out infinite 1.3s; }}

    @keyframes statsPulseGlow{suffix} {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.4; }}
    }}
    @keyframes statsRingExpand{suffix} {{
      0% {{ transform: scale(0.9); opacity: 0.85; }}
      100% {{ transform: scale(2.4); opacity: 0; }}
    }}
    @keyframes statsScanSweep{suffix} {{
      0%, 100% {{ transform: translateY(0px); opacity: 0.22; }}
      50% {{ transform: translateY(382px); opacity: 0.65; }}
    }}
    @keyframes statsBlinkLed{suffix} {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.3; }}
    }}
  </style>"""


def _defs(p: dict, sfx: str) -> str:
    return f"""  <defs>
    <linearGradient id="statsBg{sfx}" x1="0" y1="0" x2="{WIDTH}" y2="{HEIGHT}" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{p['bg0']}" />
      <stop offset="50%" stop-color="{p['bg1']}" />
      <stop offset="100%" stop-color="{p['bg2']}" />
    </linearGradient>
    <linearGradient id="statsBorder{sfx}" x1="0" y1="0" x2="{WIDTH}" y2="{HEIGHT}" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{p['border0']}" stop-opacity="0.75" />
      <stop offset="50%" stop-color="{p['border1']}" stop-opacity="0.9" />
      <stop offset="100%" stop-color="{p['border2']}" stop-opacity="0.75" />
    </linearGradient>
    <linearGradient id="statsScan{sfx}" x1="0" y1="0" x2="{WIDTH}" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{p['scan0']}" stop-opacity="0" />
      <stop offset="50%" stop-color="{p['scan0']}" stop-opacity="0.38" />
      <stop offset="100%" stop-color="{p['scan1']}" stop-opacity="0" />
    </linearGradient>
    <linearGradient id="statsPulse{sfx}" x1="{CONTENT_LEFT}" y1="0" x2="{CONTENT_RIGHT}" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{p['pulse0']}" />
      <stop offset="100%" stop-color="{p['pulse1']}" />
    </linearGradient>
    <radialGradient id="statsGlowCyan{sfx}" cx="20%" cy="30%" r="50%">
      <stop offset="0%" stop-color="{p['glow_cyan']}" stop-opacity="{p['glow_a']}" />
      <stop offset="100%" stop-color="{p['glow_cyan']}" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="statsGlowEmerald{sfx}" cx="82%" cy="62%" r="46%">
      <stop offset="0%" stop-color="{p['glow_emerald']}" stop-opacity="{p['glow_b']}" />
      <stop offset="100%" stop-color="{p['glow_emerald']}" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="statsGlowViolet{sfx}" cx="54%" cy="14%" r="40%">
      <stop offset="0%" stop-color="{p['glow_violet']}" stop-opacity="{p['glow_c']}" />
      <stop offset="100%" stop-color="{p['glow_violet']}" stop-opacity="0" />
    </radialGradient>
    <pattern id="statsGrid{sfx}" width="30" height="30" patternUnits="userSpaceOnUse">
      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="{p['grid']}" stroke-width="0.75" stroke-opacity="0.6" />
      <circle cx="30" cy="30" r="0.9" fill="{p['grid_dot']}" fill-opacity="0.7" />
    </pattern>
  </defs>"""


def _shell(p: dict, sfx: str) -> list[str]:
    """Background stack, HUD brackets and the animated scan beam."""
    parts = [
        "  <!-- Container: gradient + HUD grid + ambient glows -->",
        f'  <rect x="4" y="4" width="892" height="412" rx="14" fill="url(#statsBg{sfx})" />',
        f'  <rect x="4" y="4" width="892" height="412" rx="14" fill="url(#statsGrid{sfx})" />',
        f'  <rect x="4" y="4" width="892" height="412" rx="14" fill="url(#statsGlowCyan{sfx})" />',
        f'  <rect x="4" y="4" width="892" height="412" rx="14" fill="url(#statsGlowEmerald{sfx})" />',
        f'  <rect x="4" y="4" width="892" height="412" rx="14" fill="url(#statsGlowViolet{sfx})" />',
        f'  <rect x="4" y="4" width="892" height="412" rx="14" fill="none" stroke="url(#statsBorder{sfx})" stroke-width="1.6" />',
        "  <!-- Animated horizontal scanline -->",
        f'  <rect class="scan-beam" x="12" y="18" width="876" height="1.5" fill="url(#statsScan{sfx})" />',
        "  <!-- Corner HUD brackets -->",
        f'  <path d="M 16 34 L 16 16 L 34 16" stroke="{p["cyan"]}" stroke-width="2.2" stroke-linecap="square" />',
        f'  <path d="M 866 16 L 884 16 L 884 34" stroke="{p["emerald"]}" stroke-width="2.2" stroke-linecap="square" />',
        f'  <path d="M 16 386 L 16 404 L 34 404" stroke="{p["cyan"]}" stroke-width="2.2" stroke-linecap="square" />',
        f'  <path d="M 866 404 L 884 404 L 884 386" stroke="{p["emerald"]}" stroke-width="2.2" stroke-linecap="square" />',
    ]
    return parts


def _header(p: dict, stamp_date: str) -> list[str]:
    return [
        "  <!-- Header row -->",
        f'  <circle class="pulse-ring" cx="46" cy="41" r="4.5" fill="none" stroke="{p["emerald"]}" stroke-width="1.5" />',
        f'  <circle class="pulse-dot" cx="46" cy="41" r="4" fill="{p["emerald"]}" />',
        f'  <text x="60" y="46" class="mono" font-size="14" font-weight="800" fill="{p["text"]}" letter-spacing="1.6">SYSTEM VITALS // LIVE GITHUB TELEMETRY</text>',
        f'  <text x="864" y="46" class="mono" font-size="11" fill="{p["muted"]}" text-anchor="end" letter-spacing="0.8">SYNC {stamp_date}</text>',
        f'  <line x1="{CONTENT_LEFT}" y1="60" x2="{CONTENT_RIGHT}" y2="60" stroke="{p["divider"]}" stroke-width="1" />',
        f'  <line x1="{CONTENT_LEFT}" y1="60" x2="132" y2="60" stroke="{p["cyan"]}" stroke-width="1.6" stroke-opacity="0.85" />',
    ]


def _tiles(p: dict, data: dict, now: datetime) -> list[str]:
    months = data.get("months") or []
    window_label = data.get("window_label")
    if not window_label and months:
        window_label = f"{months[0]['label']} \u2013 {months[-1]['label']}"

    repo_total = data.get("repo_total")
    stars_note = (
        f"across {repo_total:,} repos" if repo_total else "public repos · owned"
    )

    pushed = parse_iso(data.get("last_push_at"))
    if pushed is None:
        age_value, age_note = "n/a", "awaiting telemetry"
    else:
        days = max(0, (now - pushed).days)
        age_value = f"{days}d"
        repo_name = truncate(data.get("last_push_repo") or "unknown", 26)
        age_note = f"ago \u00b7 {repo_name}"

    tiles = [
        ("PUBLIC REPOS", fmt_count(data.get("public_repos")), "github profile \u00b7 public", p["cyan"]),
        ("TOTAL STARS", fmt_count(data.get("total_stars")), stars_note, p["amber"]),
        ("FOLLOWERS", fmt_count(data.get("followers")), "github network", p["emerald"]),
        ("COMMITS / 12M", fmt_count(data.get("commits_12m")), window_label or "rolling window", p["cyan"]),
        ("CONTRIBUTED TO", fmt_count(data.get("contributed_to")), "repos \u00b7 commit + PR", p["violet"]),
        ("LAST PUSH", age_value, age_note, p["emerald"]),
    ]

    parts = ["  <!-- Stat tiles: 3 x 2 -->"]
    for index, (label, value, note, accent) in enumerate(tiles):
        x = TILE_X[index % 3]
        y = TILE_Y[index // 3]
        led = f"led-{(index % 3) + 1}"
        parts.extend([
            f'  <rect x="{x}" y="{y}" width="{TILE_W}" height="{TILE_H}" rx="10" fill="{p["tile"]}" stroke="{accent}" stroke-width="1.2" stroke-opacity="0.55" />',
            f'  <rect x="{x}" y="{y}" width="3.5" height="{TILE_H}" rx="1.75" fill="{accent}" />',
            f'  <circle class="{led}" cx="{x + TILE_W - 18}" cy="{y + 17}" r="3" fill="{accent}" />',
            f'  <text x="{x + 16}" y="{y + 25}" class="mono" font-size="11" font-weight="700" fill="{p["muted"]}" letter-spacing="1.2">{escape(label)}</text>',
            f'  <text x="{x + 16}" y="{y + 62}" class="sans" font-size="30" font-weight="700" fill="{accent}">{escape(value)}</text>',
            f'  <text x="{x + 16}" y="{y + 84}" class="mono" font-size="10.5" fill="{p["muted"]}">{escape(note)}</text>',
        ])
    return parts


def _pulse_strip(p: dict, sfx: str, data: dict) -> list[str]:
    months = data.get("months") or []
    counts = [(month.get("count") or 0) for month in months]
    peak = max(counts) if counts else 0

    parts = [
        "  <!-- Contribution pulse: 12 month bars -->",
        f'  <text x="{CONTENT_LEFT}" y="284" class="mono" font-size="10.5" font-weight="700" fill="{p["muted"]}" letter-spacing="1.4">CONTRIBUTION PULSE // LAST 12 MONTHS</text>',
        f'  <line x1="{CONTENT_LEFT}" y1="{BAR_BASE:.0f}" x2="{CONTENT_RIGHT}" y2="{BAR_BASE:.0f}" stroke="{p["divider"]}" stroke-width="1" />',
    ]
    for index, month in enumerate(months):
        count = counts[index]
        # Zero months stay a flat hairline so they never read as "a few commits".
        height = (
            1.5 if peak <= 0 or count <= 0
            else max(2.0, round(BAR_MAX_H * count / peak, 1))
        )
        x = CONTENT_LEFT + index * BAR_STEP
        y = BAR_BASE - height
        parts.append(
            f'  <rect x="{x:.1f}" y="{y:.1f}" width="{BAR_W:.0f}" height="{height:.1f}" rx="2" fill="url(#statsPulse{sfx})" fill-opacity="0.9" />'
        )
        parts.append(
            f'  <text x="{x + BAR_W / 2:.1f}" y="370" class="mono" font-size="9" fill="{p["muted"]}" text-anchor="middle" letter-spacing="0.5">{escape(str(month.get("label", "")))}</text>'
        )
    return parts


def _footer(p: dict, stamp: str) -> list[str]:
    return [
        "  <!-- Footer -->",
        f'  <text x="{CONTENT_LEFT}" y="400" class="mono" font-size="10" fill="{p["muted"]}" letter-spacing="0.8">DATA // GitHub GraphQL \u00b7 PUBLIC SCOPE</text>',
        f'  <text x="{CONTENT_RIGHT}" y="400" class="mono" font-size="10" fill="{p["muted"]}" text-anchor="end" letter-spacing="0.6">RENDERED {stamp}</text>',
    ]


def render(data: dict, theme: str, stamp: str) -> str:
    p = PALETTES[theme]
    sfx = "Dark" if theme == "dark" else "Light"
    now = parse_iso(stamp) or datetime.now(timezone.utc)
    label = (
        f"Live GitHub telemetry for @{LOGIN} - public repos, total stars, followers, "
        "commits in the last 12 months, contributed repos, last push and a 12-month contribution pulse"
    )

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" fill="none" role="img" aria-label="{escape(label)}">',
        _defs(p, sfx),
        _style_block(sfx),
    ]
    lines += _shell(p, sfx)
    lines += _header(p, now.strftime("%Y-%m-%d"))
    lines += _tiles(p, data, now)
    lines += _pulse_strip(p, sfx, data)
    lines += _footer(p, stamp)
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


# ==========================================================================
# entry point
# ==========================================================================
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render the Cyber-HUD GitHub stats cards.")
    parser.add_argument("--fixture", type=Path, help="render from a local JSON snapshot instead of the network")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR, help="destination directory (default: assets/)")
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    if args.fixture:
        data = load_fixture(args.fixture)
        # A fixture may pin the render stamp so offline output is byte-identical.
        stamp = data.get("rendered_at") or iso(now)
    else:
        data = fetch_live(resolve_token(), now)
        stamp = iso(now)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for theme, filename in (("dark", "stats-dark.svg"), ("light", "stats-light.svg")):
        target = args.out_dir / filename
        target.write_text(render(data, theme, stamp), encoding="utf-8")
        print(f"[stats] wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
