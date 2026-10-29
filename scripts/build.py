"""Build the portfolio page: site.yml -> _site/index.html (+ assets).

All text is HTML-escaped. Empty links in site.yml are left out, so nothing half-finished is shown.
Usage: python scripts/build.py        (then open _site/index.html, or serve _site/)
"""

import html
import math
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
URL = "https://petersolan.github.io/"  # link previews (LinkedIn, Slack) need absolute URLs
e = html.escape


def contours(cx=820, cy=110, rings=11) -> str:
    """Decorative contour lines (wobbly concentric rings), drawn as one SVG."""
    paths = []
    for k in range(1, rings + 1):
        r = 26 * k
        pts = []
        for i in range(73):
            a = 2 * math.pi * i / 72
            wobble = 1 + 0.10 * math.sin(3 * a + k * 0.7) + 0.06 * math.sin(5 * a - k * 0.4)
            pts.append(f"{cx + r * wobble * math.cos(a):.1f},{cy + 0.62 * r * wobble * math.sin(a):.1f}")
        paths.append(f'<path d="M{" L".join(pts)} Z"/>')
    return ('<svg class="contours" viewBox="0 0 1100 320" aria-hidden="true" preserveAspectRatio="xMidYMid slice">'
            f'{"".join(paths)}</svg>')


def links(profile: dict) -> str:
    out = []
    lk = profile.get("links", {})
    if lk.get("github"):
        out.append(f'<a class="btn" href="{e(lk["github"])}">GitHub</a>')
    if lk.get("linkedin"):
        out.append(f'<a class="btn" href="{e(lk["linkedin"])}">LinkedIn</a>')
    if lk.get("email"):
        out.append(f'<a class="btn" href="mailto:{e(lk["email"])}">Email</a>')
    if lk.get("cv"):
        out.append(f'<a class="btn" href="{e(lk["cv"])}">CV (PDF)</a>')
    return "".join(out)


def card(p: dict) -> str:
    tags = "".join(f"<li>{e(t)}</li>" for t in p.get("tags", []))
    # several live pages: demos: [{label, url}], the first one primary; otherwise one "Live demo"
    demos = p.get("demos") or ([{"label": "Live demo", "url": p["live"]}] if p.get("live") else [])
    buttons = [f'<a class="btn{" primary" if i == 0 else ""}" href="{e(d["url"])}">{e(d["label"])}</a>'
               for i, d in enumerate(demos)]
    buttons.append(f'<a class="btn" href="{e(p["repo"])}">Code</a>')
    earlier = '<span class="badge">Earlier work</span>' if p.get("earlier") else ""
    return f"""
    <article class="card" id="{e(p['id'])}">
      <a class="thumb" href="{e(demos[0]['url'] if demos else p['repo'])}" tabindex="-1" aria-hidden="true">
        <img src="{e(p['image'])}" alt="" loading="lazy" width="1000" height="625"></a>
      <div class="body">
        <h3>{e(p['title'])} {earlier}</h3>
        <p>{e(p['summary'])}</p>
        <ul class="tags" aria-label="Technologies">{tags}</ul>
        <div class="actions">{''.join(buttons)}</div>
      </div>
      <p class="sr-only">Image: {e(p.get('image_alt', ''))}</p>
    </article>"""


def matrix(projects: list[dict], skills: list[dict]) -> str:
    cols = [p for p in projects if not p.get("earlier")] + [p for p in projects if p.get("earlier")]
    head = "".join(f'<th scope="col"><a href="#{e(p["id"])}">{e(p["title"])}</a></th>' for p in cols)
    rows = []
    for s in skills:
        cells = "".join(
            f'<td>{"<span class=dot title=yes></span><span class=sr-only>yes</span>" if p["id"] in s["projects"] else ""}</td>'
            for p in cols)
        rows.append(f'<tr><th scope="row">{e(s["skill"])}</th>{cells}</tr>')
    return f'<table><thead><tr><th></th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


CSS = """
/* Layout: one reading column; hero, project cards (2 up), skills matrix, footer. */
:root{--bg:#f3f6f6;--surface:#fff;--ink:#0f1f26;--ink2:#41545c;--muted:#6f8189;--line:#dbe3e5;
 --accent:#0b6e64;--accent-ink:#fff;--chip:#e6efee;--contour:#0b6e64;
 --sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
 --mono:"IBM Plex Mono",ui-monospace,Consolas,monospace;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#0d1417;--surface:#141d21;--ink:#e8f0f1;--ink2:#b3c3c7;
 --muted:#7f9298;--line:#25333a;--accent:#4fc1b3;--accent-ink:#06201d;--chip:#1b2a2e;--contour:#4fc1b3;
 color-scheme:dark}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 var(--sans)}
a{color:var(--accent)} a:focus-visible,.btn:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.wrap{max-width:1080px;margin:0 auto;padding-inline:20px}
header.hero{position:relative;overflow:hidden;border-bottom:1px solid var(--line);background:var(--surface)}
.contours{position:absolute;inset:0;width:100%;height:100%;fill:none;stroke:var(--contour);
 stroke-width:1;opacity:.13}
.hero .wrap{position:relative;padding-block:64px 48px;display:grid;gap:14px}
.eyebrow{font:500 13px/1 var(--mono);letter-spacing:.06em;color:var(--muted);text-transform:uppercase}
h1{font-size:clamp(34px,6vw,54px);line-height:1.05;margin:0;letter-spacing:-.02em}
.role{font-size:clamp(19px,2.6vw,24px);color:var(--ink2);margin:0}
.intro{max-width:62ch;color:var(--ink2);margin:6px 0 0}
.looking{font-weight:600;margin:0}
.actions{display:flex;flex-wrap:wrap;gap:8px}
.btn{display:inline-block;padding:8px 14px;border:1px solid var(--line);border-radius:8px;
 text-decoration:none;color:var(--ink);background:var(--surface);font-weight:500;font-size:15px}
.btn:hover{border-color:var(--accent)} .btn.primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
main .wrap{padding-block:48px;display:grid;gap:56px}
h2{font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 18px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}
@media (max-width:760px){.grid{grid-template-columns:minmax(0,1fr)}}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
.thumb img{display:block;width:100%;height:auto;aspect-ratio:16/10;object-fit:cover;border-bottom:1px solid var(--line)}
.card .body{padding:18px 18px 20px;display:grid;gap:10px;align-content:start;flex:1}
.card h3{margin:0;font-size:20px;line-height:1.25}
.card p{margin:0;color:var(--ink2);font-size:15px}
.badge{font:500 11px/1 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted);
 border:1px solid var(--line);border-radius:4px;padding:3px 6px;vertical-align:middle;margin-left:4px}
.tags{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px}
.tags li{font:500 12.5px/1 var(--mono);background:var(--chip);color:var(--ink2);padding:5px 8px;border-radius:5px}
.card .actions{margin-top:auto;padding-top:4px}
.matrix{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:12px}
table{border-collapse:collapse;width:100%;font-size:14px;min-width:720px}
th,td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:center}
tbody th{text-align:left;font-weight:500;color:var(--ink2)}
thead th{font-size:12.5px;font-weight:600;vertical-align:bottom}
thead th a{color:var(--ink);text-decoration:none}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;background:var(--accent)}
footer{border-top:1px solid var(--line);color:var(--muted);font-size:14px}
footer .wrap{padding-block:24px}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
@media (prefers-reduced-motion:no-preference){.btn{transition:border-color .15s}}
"""


def page(cfg: dict) -> str:
    pr, projects = cfg["profile"], cfg["projects"]
    current = [p for p in projects if not p.get("earlier")]
    earlier = [p for p in projects if p.get("earlier")]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(pr['name'])} · {e(pr['role'])}</title>
<meta name="description" content="{e(pr['role'])} portfolio: {e(', '.join(p['title'] for p in current))}.">
<meta property="og:title" content="{e(pr['name'])} · {e(pr['role'])}">
<meta property="og:description" content="{e(pr['intro'])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{URL}{e(current[0]['image'])}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:,">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>{CSS}</style>
</head>
<body>
<header class="hero">
  {contours()}
  <div class="wrap">
    <div class="eyebrow">{e(pr['coordinates'])} · {e(pr['location'])}</div>
    <h1>{e(pr['name'])}</h1>
    <p class="role">{e(pr['role'])}</p>
    <p class="intro">{e(pr['intro'])}</p>
    <p class="looking">{e(pr['looking_for'])}</p>
    <div class="actions">{links(pr)}</div>
  </div>
</header>
<main>
  <div class="wrap">
    <section aria-labelledby="projects"><h2 id="projects">Projects</h2>
      <div class="grid">{''.join(card(p) for p in current)}</div></section>
    <section aria-labelledby="skills"><h2 id="skills">Skills by project</h2>
      <div class="matrix">{matrix(projects, cfg['skills'])}</div></section>
    {f'<section aria-labelledby="earlier"><h2 id="earlier">Earlier work</h2><div class="grid">{"".join(card(p) for p in earlier)}</div></section>' if earlier else ''}
  </div>
</main>
<footer><div class="wrap">Built from <a href="https://github.com/petersolan/petersolan.github.io">site.yml</a>
 with a small Python script. Project data: Open Government Licence v3.0 sources as credited in each repository.</div></footer>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "3211474cf009410a88d7addf6d1ba4a8"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


def main() -> None:
    cfg = yaml.safe_load((ROOT / "site.yml").read_text(encoding="utf-8"))
    # empty _site rather than delete it: on Windows a folder can't be removed while a preview
    # server (python -m http.server) is running inside it
    OUT.mkdir(exist_ok=True)
    for child in OUT.iterdir():
        shutil.rmtree(child) if child.is_dir() else child.unlink()
    (OUT / "assets").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("src"))
    (OUT / "index.html").write_text(page(cfg), encoding="utf-8")
    print(f"built {OUT / 'index.html'} ({(OUT / 'index.html').stat().st_size / 1e3:.0f} kB)")


if __name__ == "__main__":
    main()
