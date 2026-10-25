#!/usr/bin/env python3
"""Regenera assets/stats.svg y la sección de últimos pushes del README.

Solo usa la librería estándar. Si existe GITHUB_TOKEN lo usa para evitar
el rate limit de la API (en GitHub Actions viene dado).
"""
import json
import os
import re
import urllib.request
from collections import Counter
from html import escape
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "borizSam")
ROOT = Path(__file__).resolve().parent.parent
STATS_SVG = ROOT / "assets" / "stats.svg"
README = ROOT / "README.md"
TOP_LANGS = 6
RECENT = 5


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def all_repos():
    repos, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos += batch
        if len(batch) < 100:
            return repos
        page += 1


def render_stats(user, repos):
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    langs = Counter(r["language"] for r in own if r["language"])
    total = sum(langs.values()) or 1
    top = langs.most_common(TOP_LANGS)

    rows = [
        ("repos publicos", user["public_repos"]),
        ("repos propios", len(own)),
        ("stars recibidas", stars),
        ("followers", user["followers"]),
        ("following", user["following"]),
    ]

    # misma geometría que el SVG original: filas de 24px, cursor final + 25px de margen
    height = 94 + 24 * len(rows) + 16 + 24 * len(top) + 36 + 25

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}" font-family="\'JetBrains Mono\',\'Fira Code\',\'SF Mono\',Consolas,\'Courier New\',monospace" font-size="16">',
        f"<title>github stats · {USER}</title>",
        f'<rect x="1" y="1" width="898" height="{height - 2}" rx="10" fill="#000000" stroke="#00ff41" stroke-opacity="0.35"/>',
        '<path d="M1 11a10 10 0 0 1 10-10h878a10 10 0 0 1 10 10v26H1z" fill="#0a0a0a"/>',
        '<line x1="1" y1="37" x2="899" y2="37" stroke="#00ff41" stroke-opacity="0.2"/>',
        '<circle cx="24" cy="19" r="6" fill="#222"/>',
        '<circle cx="46" cy="19" r="6" fill="#222"/>',
        '<circle cx="68" cy="19" r="6" fill="#00ff41" fill-opacity="0.8"/>',
        '<text x="450.0" y="24" text-anchor="middle" font-size="13" fill="#6e7681">boris@fsociety: ~/stats</text>',
        f'<text x="28" y="70"><tspan fill="#00ff41">$ </tspan><tspan fill="#c9d1d9">gh user stats {USER}</tspan></text>',
    ]
    y = 94
    for label, value in rows:
        out.append(f'<text x="28" y="{y}" fill="#00ff41">{label}</text>')
        out.append(f'<text x="220" y="{y}" fill="#c9d1d9">{value}</text>')
        y += 24

    y += 16
    out.append(f'<text x="28" y="{y}"><tspan fill="#00ff41">$ </tspan><tspan fill="#c9d1d9">gh repo langs --top {TOP_LANGS}</tspan></text>')
    for lang, n in top:
        y += 24
        pct = n / total
        out.append(f'<text x="28" y="{y}" fill="#c9d1d9">{escape(lang)}</text>')
        out.append(f'<rect x="220" y="{y - 12}" width="420" height="12" rx="2" fill="#0f1a0f"/>')
        out.append(f'<rect x="220" y="{y - 12}" width="{420 * pct:.1f}" height="12" rx="2" fill="#00ff41" fill-opacity="0.85"/>')
        out.append(f'<text x="654" y="{y}" fill="#8b949e">{round(pct * 100)}%  ({n})</text>')

    y += 36
    out.append(f'<text x="28" y="{y}" fill="#00ff41">$</text>')
    out.append(f'<rect x="47.4" y="{y - 14}" width="9" height="17" fill="#00ff41"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></rect>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def render_recent(repos):
    own = [r for r in repos if not r["fork"] and r["name"].lower() != USER.lower()]
    own.sort(key=lambda r: r["pushed_at"], reverse=True)
    lines = []
    for r in own[:RECENT]:
        lang = f" · {r['language']}" if r["language"] else ""
        lines.append(f"- `{r['pushed_at'][:10]}` [{r['name']}]({r['html_url']}){lang}")
    return "\n".join(lines)


def main():
    user = api(f"/users/{USER}")
    repos = all_repos()

    STATS_SVG.write_text(render_stats(user, repos), encoding="utf-8")

    readme = README.read_text(encoding="utf-8")
    readme = re.sub(
        r"(<!-- RECENT:START -->\n).*?(<!-- RECENT:END -->)",
        lambda m: m.group(1) + render_recent(repos) + "\n" + m.group(2),
        readme,
        flags=re.S,
    )
    README.write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
