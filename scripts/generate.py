#!/usr/bin/env python3
"""Gera os cards SVG do perfil do GitHub (tema terminal verde).

Uso:
    python scripts/generate.py          # dados reais da API do GitHub
    python scripts/generate.py --demo   # dados de exemplo (teste local, sem internet)

Variavel opcional: GITHUB_TOKEN (necessaria para o grafico de contribuicoes).
"""
import argparse
import base64
import io
import json
import os
import random
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "generated"

# ============================ CONFIG (edite aqui) ============================
USER = "fevillalon"
NAME = "villalón"
ROLE = "Computer Engineer - FHO 21y"
PILLS = ["Open Source", "Projects", "Systems"]
STATUS = "Building | Learning | Shipping"
ROLE_TERMINAL = "Computer Engineering - FHO 21y"
CONTACT = f"github.com/{USER}"
ASCII_COLS, ASCII_ROWS = 60, 30   # tamanho do retrato ASCII
INVERT_ASCII = False              # True se o retrato ficar "negativo"
MAX_PROJECTS = 3
MAX_LANGS = 4
EXCLUDE_REPOS = {USER}            # nao conta o repo do proprio perfil
# =============================================================================

TOKEN = os.environ.get("GITHUB_TOKEN", "")
FONT = "'JetBrains Mono','Fira Code','SF Mono',Consolas,'Courier New',monospace"
NEON, G2, DIM, TXT = "#00ff41", "#4ade80", "#5b8a68", "#b6f5c8"
LEVELS = ["#0b1d10", "#0e4b22", "#12803a", "#22c55e", "#7cff9b"]


# ------------------------------- dados ---------------------------------------
def http(url, body=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-card-generator"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def rel_time(iso):
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    s = (datetime.now(timezone.utc) - dt).total_seconds()
    if s < 3600:
        return "updated just now"
    if s < 86400:
        return f"updated {int(s // 3600)}h ago"
    if s < 86400 * 30:
        return f"updated {int(s // 86400)}d ago"
    if s < 86400 * 365:
        return f"updated {int(s // (86400 * 30))}mo ago"
    return f"updated {int(s // (86400 * 365))}y ago"


def fetch_live():
    user = http(f"https://api.github.com/users/{USER}")
    repos = http(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&sort=pushed")
    repos = [r for r in repos if not r["fork"] and r["name"] not in EXCLUDE_REPOS]

    weeks, total = [], 0
    if TOKEN:
        q = """query($login:String!){user(login:$login){contributionsCollection{
        contributionCalendar{totalContributions weeks{contributionDays{contributionCount}}}}}}"""
        body = json.dumps({"query": q, "variables": {"login": USER}}).encode()
        try:
            data = http("https://api.github.com/graphql", body)
            cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            total = cal["totalContributions"]
            weeks = [[d["contributionCount"] for d in w["contributionDays"]] for w in cal["weeks"]]
        except Exception as e:  # noqa
            print(f"[aviso] contribuicoes indisponiveis: {e}", file=sys.stderr)

    counts = Counter(r["language"] for r in repos if r["language"])
    n = sum(counts.values()) or 1
    langs = [(k, v * 100 / n) for k, v in counts.most_common(MAX_LANGS)]

    projects = [
        dict(name=r["name"], desc=r["description"] or "No description yet",
             lang=r["language"] or "-", stars=r["stargazers_count"], when=rel_time(r["pushed_at"]))
        for r in repos[:MAX_PROJECTS]
    ]
    return dict(
        followers=user["followers"], repos=user["public_repos"],
        stars=sum(r["stargazers_count"] for r in repos),
        contributions=total, active_days=sum(1 for w in weeks for c in w if c > 0),
        weeks=weeks, langs=langs, projects=projects,
    )


def demo():
    rnd = random.Random(7)
    weeks = [[rnd.choice([0, 0, 0, 1, 2, 4, 7]) for _ in range(7)] for _ in range(53)]
    return dict(
        followers=3, repos=6, stars=5,
        contributions=sum(sum(w) for w in weeks),
        active_days=sum(1 for w in weeks for c in w if c > 0), weeks=weeks,
        langs=[("Python", 45.0), ("C", 25.0), ("TypeScript", 20.0), ("HTML", 10.0)],
        projects=[
            dict(name="sistema-estoque", desc="CRUD de estoque com Python e SQLite", lang="Python", stars=2, when="updated 2d ago"),
            dict(name="c-algoritmos", desc="Estruturas de dados e algoritmos em C", lang="C", stars=1, when="updated 5d ago"),
            dict(name="fevillalon", desc="My GitHub profile", lang="-", stars=0, when="updated just now"),
        ],
    )


# ------------------------------- avatar --------------------------------------
def load_avatar():
    try:
        from PIL import Image
    except ImportError:
        return None
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = ROOT / "assets" / f"avatar.{ext}"
        if p.exists():
            return Image.open(p).convert("RGB")
    return None


def avatar_b64(img):
    from PIL import ImageOps
    sq = ImageOps.fit(img, (160, 160))
    buf = io.BytesIO()
    sq.save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def ascii_lines(img):
    if img is None:
        return ["", "", "   ____  _   _ ", "  / ___|| | | |", "  \\___ \\| |_| |", "   ___) |  _  |",
                "  |____/|_| |_|", "", "   >_ add assets/avatar.png"]
    from PIL import ImageOps
    g = ImageOps.fit(img.convert("L"), (230, 198))
    g = ImageOps.autocontrast(g.resize((ASCII_COLS, ASCII_ROWS)))
    ramp = " .:-=+*#%@"
    px = list(g.tobytes())
    lines = []
    for y in range(ASCII_ROWS):
        row = ""
        for x in range(ASCII_COLS):
            i = min(int(px[y * ASCII_COLS + x] / 256 * len(ramp)), len(ramp) - 1)
            row += ramp[len(ramp) - 1 - i] if INVERT_ASCII else ramp[i]
        lines.append(row.rstrip())
    return lines


# ------------------------------- SVG base ------------------------------------
def frame(w, h, body, u, extra_css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">
<defs>
 <linearGradient id="bd{u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#00ff41" stop-opacity=".55"/><stop offset=".5" stop-color="#0a5a22" stop-opacity=".35"/><stop offset="1" stop-color="#a3e635" stop-opacity=".45"/></linearGradient>
 <radialGradient id="b1{u}" cx=".1" cy=".05" r=".6"><stop offset="0" stop-color="#00ff41" stop-opacity=".26"/><stop offset="1" stop-color="#00ff41" stop-opacity="0"/></radialGradient>
 <radialGradient id="b2{u}" cx=".5" cy="1.05" r=".5"><stop offset="0" stop-color="#d4e815" stop-opacity=".30"/><stop offset="1" stop-color="#d4e815" stop-opacity="0"/></radialGradient>
 <radialGradient id="b3{u}" cx="1" cy=".7" r=".45"><stop offset="0" stop-color="#4f46e5" stop-opacity=".28"/><stop offset="1" stop-color="#4f46e5" stop-opacity="0"/></radialGradient>
 <pattern id="sl{u}" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#00ff41" opacity=".05"/></pattern>
 <clipPath id="cp{u}"><rect width="{w}" height="{h}" rx="14"/></clipPath>
 <filter id="glow{u}" x="-20%" y="-30%" width="140%" height="160%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>.cur{{animation:blink 1s steps(2,start) infinite}}@keyframes blink{{to{{visibility:hidden}}}}{extra_css}</style>
<g clip-path="url(#cp{u})">
 <rect width="{w}" height="{h}" fill="#030803"/>
 <rect width="{w}" height="{h}" fill="url(#b1{u})"/>
 <rect width="{w}" height="{h}" fill="url(#b2{u})"/>
 <rect width="{w}" height="{h}" fill="url(#b3{u})"/>
 <rect width="{w}" height="{h}" fill="url(#sl{u})"/>
</g>
{body}
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="14" fill="none" stroke="url(#bd{u})" stroke-width="1.5"/>
</svg>'''


def t(x, y, s, fill=TXT, size=12, weight="normal", anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" xml:space="preserve" {extra}>{escape(str(s))}</text>')


def cut(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


# ------------------------------- cards ---------------------------------------
def card_header(img):
    w, h, u = 800, 150, "hd"
    if img is not None:
        av = (f'<clipPath id="av"><circle cx="82" cy="75" r="40"/></clipPath>'
              f'<image href="data:image/jpeg;base64,{avatar_b64(img)}" x="42" y="35" width="80" height="80" '
              f'clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>')
    else:
        av = f'<circle cx="82" cy="75" r="40" fill="#06200c"/>' + t(82, 83, "FV", NEON, 24, "bold", "middle")
    pills, x = "", 150
    for p in PILLS:
        pw = len(p) * 7.4 + 30
        pills += (f'<rect x="{x}" y="112" width="{pw:.0f}" height="22" rx="11" fill="#04140a" stroke="#14803a" stroke-opacity=".8"/>'
                  + t(x + pw / 2, 127, p, G2, 11, anchor="middle"))
        x += pw + 12
    body = f'''
<path d="M150 32 Q 330 12 470 40" fill="none" stroke="#00ff41" stroke-opacity=".35" stroke-width="1.2"/>
{av}
<circle cx="82" cy="75" r="43" fill="none" stroke="{NEON}" stroke-width="1.5" filter="url(#glow{u})"/>
{t(150, 52, "@" + USER, G2, 12)}
<text x="150" y="92" fill="{NEON}" font-size="38" font-weight="bold" filter="url(#glow{u})">{escape(NAME)}</text>
{t(152, 108, ROLE, TXT, 12)}
{pills}
<circle cx="752" cy="40" r="3" fill="{NEON}" filter="url(#glow{u})"/>'''
    return frame(w, h, body, u)


def card_terminal(d, img):
    w, h, u = 800, 340, "tm"
    langs = ", ".join(n for n, _ in d["langs"]) or "Python, C"
    rows = [
        ("Subject", NAME), ("Handle", "@" + USER), ("Role", ROLE_TERMINAL), ("Status", STATUS),
        ("Languages", langs), ("Repositories", d["repos"]), ("Contributions", d["contributions"]),
        ("Stars", d["stars"]), ("Followers", d["followers"]), ("Active Days", d["active_days"]),
        ("Contact", CONTACT),
    ]
    right = ""
    for i, (k, v) in enumerate(rows):
        y = 92 + i * 21
        right += t(350, y, k, G2, 11, "bold") + t(510, y, cut(str(v), 36), TXT, 11)
    art = "".join(t(34, 66 + i * 6.6, ln, NEON, 6.4, extra='opacity=".9"') for i, ln in enumerate(ascii_lines(img)))
    body = f'''
<rect x="0" y="0" width="{w}" height="30" fill="#041006" opacity=".9" clip-path="url(#cp{u})"/>
<circle cx="18" cy="15" r="4" fill="#ff5f56"/><circle cx="32" cy="15" r="4" fill="#ffbd2e"/><circle cx="46" cy="15" r="4" fill="#27c93f"/>
{t(w / 2, 19, f"{USER}@github ~ $ ./profile-scan --live", G2, 11, anchor="middle")}
{t(w - 20, 19, "# sync", DIM, 10, anchor="end")}
<rect x="16" y="42" width="300" height="282" rx="8" fill="#030c05" stroke="#14803a" stroke-opacity=".7"/>
{art}
<rect x="330" y="42" width="454" height="282" rx="8" fill="#030c05" stroke="#14803a" stroke-opacity=".7"/>
{t(350, 64, "profile.scan", DIM, 10)}
<line x1="346" y1="70" x2="768" y2="70" stroke="#14803a" stroke-opacity=".5"/>
{right}
<rect class="scan" x="0" y="42" width="{w}" height="26" fill="url(#sg{u})" opacity=".35"/>
<defs><linearGradient id="sg{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#00ff41" stop-opacity="0"/><stop offset=".5" stop-color="#00ff41" stop-opacity=".7"/><stop offset="1" stop-color="#00ff41" stop-opacity="0"/></linearGradient></defs>'''
    css = "@keyframes scan{0%{transform:translateY(0)}100%{transform:translateY(256px)}}.scan{animation:scan 5s linear infinite}"
    return frame(w, h, body, u, css)


def card_projects(d):
    u, w = "pj", 800
    projs = d["projects"]
    n = max(len(projs), 1)
    inner_h = n * 68 + 12
    h = 64 + inner_h + 24
    rows = ""
    if not projs:
        rows = t(52, 104, "no public repositories yet", DIM, 12) + f'<text class="cur" x="270" y="104" fill="{NEON}" font-size="12">_</text>'
    for i, p in enumerate(projs):
        y0 = 76 + i * 68
        rows += (f'<rect x="36" y="{y0}" width="728" height="58" rx="8" fill="#051208" stroke="#14803a" stroke-opacity=".6"/>'
                 + t(54, y0 + 24, p["name"], NEON, 14, "bold")
                 + f'<text class="cur" x="{54 + len(p["name"]) * 8.6 + 4:.0f}" y="{y0 + 24}" fill="{NEON}" font-size="14">_</text>'
                 + t(54, y0 + 44, cut(p["desc"], 64), DIM, 11)
                 + t(748, y0 + 24, f'{p["lang"]}  ·  ★ {p["stars"]}', G2, 11, anchor="end")
                 + t(748, y0 + 44, p["when"], DIM, 10, anchor="end"))
    body = f'''
{t(28, 34, "PROJECTS.LIST", NEON, 11, "bold", extra='letter-spacing="1.5"')}{t(150, 34, "./projects.sh --all", DIM, 11)}
{t(w - 28, 34, f"{len(projs)} project{'s' if len(projs) != 1 else ''}", G2, 11, anchor="end")}
<line x1="24" y1="46" x2="{w - 24}" y2="46" stroke="#14803a" stroke-opacity=".6"/>
<rect x="24" y="58" width="{w - 48}" height="{inner_h}" rx="10" fill="#030c05" opacity=".6" stroke="#14803a" stroke-opacity=".4"/>
{rows}'''
    return frame(w, h, body, u)


def card_stack(d):
    u, w = "st", 800
    langs = d["langs"] or [("Python", 100.0)]
    h = 100 + len(langs) * 36 + 20
    rows = ""
    for i, (name, pct) in enumerate(langs):
        y = 112 + i * 36
        bw = max(pct / 100 * 380, 4)
        rows += (f'<circle cx="52" cy="{y - 4}" r="4" fill="{NEON}" filter="url(#glow{u})"/>'
                 + t(68, y, name, TXT, 13, "bold")
                 + f'<rect x="300" y="{y - 11}" width="380" height="9" rx="4.5" fill="#0b1d10"/>'
                 + f'<rect x="300" y="{y - 11}" width="{bw:.0f}" height="9" rx="4.5" fill="url(#bar{u})"/>'
                 + t(748, y, f"{pct:.0f}%", G2, 12, "bold", "end"))
    body = f'''
<defs><linearGradient id="bar{u}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22c55e"/><stop offset="1" stop-color="#00ff41"/></linearGradient></defs>
<text x="28" y="40" fill="{NEON}" font-size="20" font-weight="bold" filter="url(#glow{u})">Language Stack</text>
{t(28, 62, "Repository-weighted technologies", TXT, 11, "bold")}
<text x="772" y="40" fill="{G2}" font-size="11" text-anchor="end">&gt; stack.scan <tspan class="cur">_</tspan></text>
<rect x="24" y="78" width="{w - 48}" height="{h - 98}" rx="10" fill="#030c05" opacity=".6" stroke="#14803a" stroke-opacity=".4"/>
{rows}'''
    return frame(w, h, body, u)


def card_activity(d):
    u, w, h = "ac", 800, 230
    weeks = d["weeks"]
    mx = max((c for wk in weeks for c in wk), default=0)

    def level(c):
        if c == 0 or mx == 0:
            return 0
        r = c / mx
        return 1 if r <= .25 else 2 if r <= .5 else 3 if r <= .75 else 4

    cells = ""
    if weeks:
        for x, wk in enumerate(weeks[-53:]):
            for y, c in enumerate(wk):
                cells += f'<rect x="{34 + x * 14}" y="{96 + y * 14}" width="11" height="11" rx="2" fill="{LEVELS[level(c)]}"/>'
    else:
        for x in range(53):
            for y in range(7):
                cells += f'<rect x="{34 + x * 14}" y="{96 + y * 14}" width="11" height="11" rx="2" fill="{LEVELS[0]}"/>'
    legend = t(590, 52, "Less", DIM, 10, anchor="end") + "".join(
        f'<rect x="{598 + i * 14}" y="43" width="10" height="10" rx="2" fill="{c}"/>' for i, c in enumerate(LEVELS)) + t(676, 52, "More", DIM, 10)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = f'''
<text x="28" y="40" fill="{NEON}" font-size="20" font-weight="bold" filter="url(#glow{u})">Contribution Activity</text>
{t(28, 62, f"{d['contributions']} contributions in the last year", TXT, 11, "bold")}
{legend}
<rect x="24" y="78" width="{w - 48}" height="{h - 98}" rx="10" fill="#030c05" opacity=".6" stroke="#14803a" stroke-opacity=".4"/>
{cells}
{t(w - 28, h - 10, "synced " + now, DIM, 9, anchor="end")}'''
    return frame(w, h, body, u)


# ------------------------------- main ----------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="usa dados de exemplo")
    args = ap.parse_args()
    try:
        d = demo() if args.demo else fetch_live()
    except Exception as e:  # noqa
        print(f"[erro] nao foi possivel buscar dados do GitHub: {e}", file=sys.stderr)
        sys.exit(1)
    img = load_avatar()
    OUT.mkdir(exist_ok=True)
    files = {
        "header.svg": card_header(img), "terminal.svg": card_terminal(d, img),
        "projects.svg": card_projects(d), "stack.svg": card_stack(d), "activity.svg": card_activity(d),
    }
    for name, svg in files.items():
        (OUT / name).write_text(svg, encoding="utf-8")
        print("ok ->", OUT / name)


if __name__ == "__main__":
    main()
