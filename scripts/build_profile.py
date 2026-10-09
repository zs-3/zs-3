#!/usr/bin/env python3
"""Builds assets/profile.svg: the ENTIRE README as one animated SVG.
Pulls live data from the GitHub API (falls back to labelled preview data),
and embeds avatar + dist/github-snake.svg as data-URIs (SVG-in-SVG)."""
import os, json, base64, html, pathlib, urllib.request, datetime

USER = os.environ.get("PROFILE_USER", "zs-3")
TOKEN = os.environ.get("GITHUB_TOKEN")
ROOT = pathlib.Path(__file__).resolve().parent.parent
E = html.escape

def get(url, raw=False):
    h = {"User-Agent": "profile-builder", "Accept": "application/vnd.github+json"}
    if TOKEN: h["Authorization"] = f"Bearer {TOKEN}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=20) as r:
        b = r.read()
        return (b, r.headers.get("Content-Type", "")) if raw else json.loads(b)

# ---------- data ----------
preview = False
try:
    u = get(f"https://api.github.com/users/{USER}")
    assert "login" in u
    repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    langs = {}
    for r in own:
        try:
            for k, v in get(r["languages_url"]).items(): langs[k] = langs.get(k, 0) + v
        except Exception: pass
    tot = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda x: -x[1])[:5]
    top = [(k, v * 100 / tot) for k, v in top] or [("—", 0)]
    data = dict(repos=u["public_repos"], stars=stars, followers=u["followers"], following=u["following"],
                joined=u["created_at"][:4], name=u.get("name") or "Ziyaad")
    avatar = None
    try:
        b, ct = get(u["avatar_url"] + "&s=240", raw=True)
        avatar = f"data:{ct.split(';')[0] or 'image/png'};base64," + base64.b64encode(b).decode()
    except Exception: pass
except Exception as ex:
    preview = True
    data = dict(repos=12, stars=34, followers=21, following=9, joined="2023", name="Ziyaad")
    top = [("C++", 38), ("Python", 27), ("JavaScript", 19), ("Shell", 10), ("HTML", 6)]
    avatar = None

snake_path = ROOT / "dist" / "github-snake.svg"
snake = None
if snake_path.exists():
    snake = "data:image/svg+xml;base64," + base64.b64encode(snake_path.read_bytes()).decode()

# ---------- helpers ----------
W, H = 1000, 1560
LC = {"C++": "#f34b7d", "Python": "#4f9dff", "JavaScript": "#f7df1e", "TypeScript": "#3b82f6", "HTML": "#ff6a3d",
      "CSS": "#a855f7", "Shell": "#4ade80", "C": "#94a3b8", "Java": "#f59e0b", "Go": "#22d3ee", "Rust": "#fb923c"}
out = []
def add(s): out.append(s)

def card(x, y, w, h, d=0.0, tint=None):
    f = f'fill="url(#{tint})"' if tint else 'fill="#fff" fill-opacity=".045"'
    return (f'<g class="in" style="animation-delay:{d:.2f}s"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" {f} stroke="url(#cs)" stroke-width="1.3"/>'
            f'<path d="M{x+30} {y+1} H{x+w-30}" stroke="#fff" stroke-opacity=".28" stroke-linecap="round"/></g>')

def label(x, y, t, size=18, w=700, fill="#f4f4fb", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{fill}" {extra}>{E(t)}</text>'

# ---------- document ----------
add(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
<clipPath id="pg"><rect width="{W}" height="{H}" rx="30"/></clipPath>
<linearGradient id="acc" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a78bfa"/><stop offset=".5" stop-color="#60a5fa"/><stop offset="1" stop-color="#22d3ee"/></linearGradient>
<linearGradient id="hot" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f472b6"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>
<linearGradient id="cs" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".30"/><stop offset=".5" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#a78bfa" stop-opacity=".35"/></linearGradient>
<linearGradient id="cta" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c3aed" stop-opacity=".45"/><stop offset=".6" stop-color="#2563eb" stop-opacity=".30"/><stop offset="1" stop-color="#0891b2" stop-opacity=".35"/></linearGradient>
<filter id="bl" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="70"/></filter>
<filter id="gl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="#fff" fill-opacity=".10"/></pattern>
<radialGradient id="fade" cx=".5" cy=".5" r=".7"><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
<mask id="dm"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
<clipPath id="av"><circle cx="150" cy="190" r="66"/></clipPath>
</defs>
<style>
text{{font-family:'Inter','SF Pro Display','Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif}}
@keyframes up{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:none}}}}
.in{{animation:up 1s cubic-bezier(.2,.8,.2,1) both}}
@keyframes bar{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.bar{{transform-box:fill-box;transform-origin:left center;animation:bar 1.6s cubic-bezier(.2,.8,.2,1) both}}
@keyframes d1{{50%{{transform:translate(90px,60px)}}}}@keyframes d2{{50%{{transform:translate(-80px,90px)}}}}
@keyframes d3{{50%{{transform:translate(70px,-70px)}}}}
.b1{{animation:d1 14s ease-in-out infinite}}.b2{{animation:d2 17s ease-in-out infinite}}.b3{{animation:d3 20s ease-in-out infinite}}
@keyframes role{{0%{{opacity:0;transform:translateY(10px)}}4%,22%{{opacity:1;transform:none}}27%,100%{{opacity:0;transform:translateY(-10px)}}}}
.role{{animation:role 12s ease-in-out infinite both}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.spin{{transform-box:fill-box;transform-origin:center;animation:spin 7s linear infinite}}
@keyframes pulse{{0%{{transform:scale(1);opacity:.7}}100%{{transform:scale(2.6);opacity:0}}}}
.pulse{{transform-box:fill-box;transform-origin:center;animation:pulse 2s ease-out infinite}}
@keyframes flt{{50%{{transform:translateY(-6px)}}}}
.flt{{animation:flt 4s ease-in-out infinite}}
@keyframes shine{{from{{transform:translateX(-400px)}}to{{transform:translateX(1400px)}}}}
.shine{{animation:shine 5s ease-in-out infinite}}
</style>
<g clip-path="url(#pg)">
<rect width="{W}" height="{H}" fill="#070813"/>
<g><circle class="b1" cx="150" cy="120" r="230" fill="#7c3aed" fill-opacity=".55" filter="url(#bl)"/>
<circle class="b2" cx="900" cy="420" r="210" fill="#2563eb" fill-opacity=".45" filter="url(#bl)"/>
<circle class="b3" cx="120" cy="820" r="220" fill="#db2777" fill-opacity=".32" filter="url(#bl)"/>
<circle class="b1" cx="880" cy="1100" r="230" fill="#06b6d4" fill-opacity=".34" filter="url(#bl)"/>
<circle class="b2" cx="200" cy="1420" r="220" fill="#7c3aed" fill-opacity=".45" filter="url(#bl)"/></g>
<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dm)"/>
''')

# decorative floating glass rings/orbs
for (cx, cy, r, c, dl) in [(975, 600, 16, "#a78bfa", 0), (60, 1010, 26, "#22d3ee", 1.2), (955, 1535, 16, "#f472b6", .6), (30, 440, 14, "#60a5fa", 2)]:
    add(f'<g class="flt" style="animation-delay:{dl}s"><circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c}" stroke-opacity=".55" stroke-width="1.5"/><circle cx="{cx}" cy="{cy}" r="{r*.45:.1f}" fill="{c}" fill-opacity=".25"/></g>')

# ---- HERO ----
add(card(40, 40, 920, 300, 0.0))
add('<g class="in" style="animation-delay:.15s">')
add('<circle class="spin" cx="150" cy="190" r="78" fill="none" stroke="url(#acc)" stroke-width="3" stroke-dasharray="120 60" stroke-linecap="round"/>')
if avatar:
    add(f'<image href="{avatar}" x="84" y="124" width="132" height="132" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>')
else:
    add('<circle cx="150" cy="190" r="66" fill="url(#acc)" fill-opacity=".25"/>' + label(150, 207, "ZS", 48, 800, "url(#acc)", 'text-anchor="middle"'))
add('</g>')
add('<g class="in" style="animation-delay:.3s">')
add(label(270, 118, "WELCOME TO MY PROFILE", 13, 600, "#9aa3c0", 'letter-spacing="4"'))
add(label(268, 190, data["name"], 68, 800, "url(#acc)"))
add(label(270, 228, f"@{USER}  ·  ZS  ·  member of @zs-org", 18, 500, "#9aa3c0"))
for i, r in enumerate(["Indie Programmer", "C++ · Python · JavaScript", "Linux-native builder", "Shipping things, solo"]):
    add(f'<g class="role" style="animation-delay:{i*3}s">' + label(270, 285, r, 28, 600, "#e9e7ff") + '</g>')
add('</g>')
add('<g class="in" style="animation-delay:.5s"><rect x="715" y="70" width="215" height="38" rx="19" fill="#22c55e" fill-opacity=".12" stroke="#22c55e" stroke-opacity=".45"/>'
    '<circle class="pulse" cx="740" cy="89" r="5" fill="#22c55e"/><circle cx="740" cy="89" r="5" fill="#22c55e"/>'
    + label(757, 94, "Open to collaborate", 13, 600, "#86efac") + '</g>')

# ---- STAT TILES ----
tiles = [("REPOSITORIES", data["repos"], "acc"), ("TOTAL STARS", data["stars"], "hot"), ("FOLLOWERS", data["followers"], "acc"), ("FOLLOWING", data["following"], "hot")]
for i, (lb, val, g) in enumerate(tiles):
    x = 40 + i * 236
    add(card(x, 370, 212, 120, .45 + i * .12))
    add(f'<g class="in" style="animation-delay:{.55+i*.12:.2f}s">' + label(x + 28, 430, str(val), 48, 800, f"url(#{g})") + label(x + 28, 462, lb, 12, 600, "#9aa3c0", 'letter-spacing="3"') +
        f'<rect x="{x+28}" y="388" width="26" height="4" rx="2" fill="url(#{g})"/></g>')

# ---- LANGUAGES ----
add(card(40, 520, 560, 310, 1.0))
add('<g class="in" style="animation-delay:1.1s">' + label(72, 564, "Top Languages", 20, 700) + label(72, 586, "by code size · public repos", 12, 500, "#8089a8") +
    ('<rect x="440" y="548" width="130" height="24" rx="12" fill="#f59e0b" fill-opacity=".14" stroke="#f59e0b" stroke-opacity=".5"/>' + label(505, 565, "PREVIEW DATA", 10, 700, "#fbbf24", 'text-anchor="middle" letter-spacing="2"') if preview else '') + '</g>')
for i, (name, pct) in enumerate(top):
    y = 626 + i * 40
    c = LC.get(name, "#a78bfa")
    bw = max(496 * pct / 100, 6)
    add(f'<g class="in" style="animation-delay:{1.2+i*.1:.2f}s">' + f'<circle cx="80" cy="{y-5}" r="5" fill="{c}"/>' + label(94, y, name, 14, 600, "#e5e7f5") +
        label(568, y, f"{pct:.1f}%", 13, 600, "#9aa3c0", 'text-anchor="end"') +
        f'<rect x="72" y="{y+10}" width="496" height="9" rx="4.5" fill="#fff" fill-opacity=".07"/>'
        f'<rect class="bar" style="animation-delay:{1.3+i*.12:.2f}s" x="72" y="{y+10}" width="{bw:.1f}" height="9" rx="4.5" fill="{c}" filter="url(#gl)"/></g>')

# ---- ABOUT ----
add(card(624, 520, 336, 310, 1.1))
add('<g class="in" style="animation-delay:1.2s">' + label(656, 564, "About", 20, 700) + label(656, 586, "contact & identity", 12, 500, "#8089a8"))
rows = [("ROLE", "Indie Programmer"), ("ORG", "@zs-org"), ("EMAIL", "hello@ziyaad.net"), ("BACKUP", "zsorg34@gmail.com"), ("JOINED", f"GitHub · {data['joined']}")]
for i, (k, v) in enumerate(rows):
    y = 618 + i * 40
    add(label(656, y, k, 10, 700, "#7c86a8", 'letter-spacing="3"') + label(656, y + 18, v, 15, 600, "#eceafd"))
add('</g>')

# ---- TECH STACK ----
add(card(40, 860, 920, 150, 1.4))
add('<g class="in" style="animation-delay:1.5s">' + label(72, 904, "Tech Stack", 20, 700) + '</g>')
chips = [("C++", "#f34b7d"), ("Python", "#4f9dff"), ("JavaScript", "#f7df1e"), ("Git", "#fb7185"), ("Linux", "#4ade80")]
x = 72
for i, (n, c) in enumerate(chips):
    w = len(n) * 9.5 + 62
    add(f'<g class="in" style="animation-delay:{1.6+i*.1:.2f}s"><g class="flt" style="animation-delay:{i*.5}s">'
        f'<rect x="{x}" y="930" width="{w:.0f}" height="46" rx="23" fill="{c}" fill-opacity=".10" stroke="{c}" stroke-opacity=".5"/>'
        f'<circle cx="{x+26}" cy="953" r="6" fill="{c}" filter="url(#gl)"/>' + label(x + 42, 959, n, 16, 600, "#f1f0ff") + '</g></g>')
    x += w + 16

# ---- SNAKE (SVG inside SVG) ----
add(card(40, 1040, 920, 310, 1.7))
add('<g class="in" style="animation-delay:1.8s">' + label(72, 1084, "Contribution Snake", 20, 700) + label(72, 1106, "live from dist/github-snake.svg", 12, 500, "#8089a8"))
if snake:
    add(f'<image href="{snake}" x="60" y="1120" width="880" height="210" preserveAspectRatio="xMidYMid meet"/>')
else:
    add('<rect x="72" y="1130" width="856" height="190" rx="16" fill="#fff" fill-opacity=".03" stroke="#fff" stroke-opacity=".12" stroke-dasharray="6 6"/>' +
        label(500, 1230, "Snake appears here after the first workflow run", 15, 500, "#8089a8", 'text-anchor="middle"'))
add('</g>')

# ---- CTA ----
add(card(40, 1380, 920, 140, 2.0, tint="cta"))
add('<g class="in" style="animation-delay:2.1s">' + label(76, 1442, "Let's build something great.", 32, 800, "#fff") +
    label(76, 1480, "hello@ziyaad.net   ·   zsorg34@gmail.com", 15, 500, "#c7d2fe") +
    '<rect x="740" y="1420" width="184" height="52" rx="26" fill="url(#acc)"/>' + label(832, 1452, "Say hello  →", 16, 700, "#0b0d1f", 'text-anchor="middle"') + '</g>')
add(f'<rect class="shine" x="0" y="0" width="160" height="{H}" fill="#fff" fill-opacity=".025" transform="skewX(-20)"/>')
add(label(500, 1546, f"auto-generated {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d} UTC", 11, 500, "#5b6384", 'text-anchor="middle" letter-spacing="2"'))
add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="30" fill="none" stroke="url(#cs)" stroke-width="2"/>')
add('</g></svg>')

(ROOT / "assets").mkdir(exist_ok=True)
(ROOT / "assets" / "profile.svg").write_text("\n".join(out), encoding="utf-8")
print("built assets/profile.svg", "(PREVIEW DATA)" if preview else "(live data)", "snake:", bool(snake))
