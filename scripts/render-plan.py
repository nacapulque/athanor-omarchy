"""Render docs/PLAN.md to a self-contained HTML page with a sidebar TOC.

usage: python -I scripts/render-plan.py docs/PLAN.md ~/claude-plan.html
"""

import html
import re
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
lines = src.read_text().splitlines()


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


body, toc, title = [], [], ""
i = 0
para = []


def flush_para():
    if para:
        body.append(f"<p>{inline(' '.join(para))}</p>")
        para.clear()


while i < len(lines):
    line = lines[i]
    if not line.strip():
        flush_para()
        i += 1
        continue
    m = re.match(r"^(#{1,3}) (.+)$", line)
    if m:
        flush_para()
        level, text = len(m.group(1)), m.group(2)
        if level == 1:
            title = text
        else:
            sid = slug(text)
            toc.append((level, text, sid))
            body.append(f'<h{level} id="{sid}">{inline(text)}</h{level}>')
        i += 1
        continue
    if line.startswith("|"):
        flush_para()
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            rows.append([c.strip() for c in lines[i].strip("|").split("|")])
            i += 1
        head, data = rows[0], [r for r in rows[1:] if not all(set(c) <= set("-: ") for c in r)]
        t = "<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
        t += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in data)
        body.append(t + "</tbody></table>")
        continue
    if re.match(r"^\s*(-|\d+\.) ", line):
        flush_para()
        ordered = bool(re.match(r"^\d+\.", line))
        items = []  # (depth, text)
        while i < len(lines) and (re.match(r"^\s*(-|\d+\.) ", lines[i]) or (lines[i].startswith("  ") and lines[i].strip() and items)):
            l = lines[i]
            mm = re.match(r"^(\s*)(?:-|\d+\.) (.*)$", l)
            if mm:
                items.append([len(mm.group(1)) // 2, mm.group(2)])
            else:
                items[-1][1] += " " + l.strip()
            i += 1
        tag = "ol" if ordered else "ul"
        h, depth = f"<{tag}>", 0
        for n, (d, text) in enumerate(items):
            if d > depth:
                h += "<ul>"
            elif d < depth:
                h += "</li></ul></li>"
            elif n:
                h += "</li>"
            depth = d
            h += f"<li>{inline(text)}"
        h += "</li>" + "</ul></li>" * depth + f"</{tag}>"
        body.append(h)
        continue
    para.append(line.strip())
    i += 1
flush_para()

nav = "".join(
    f'<a class="l{lvl}" href="#{sid}">{inline(text)}</a>' for lvl, text, sid in toc
)

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root {{
  --bg: #faf7f2; --surface: #f3eee6; --text: #2b2620; --muted: #6b6258;
  --rule: #e2d9cc; --accent: #9a5b13; --code: #efe8dc;
  --font: ui-serif, Georgia, "Iowan Old Style", serif;
  --sans: ui-sans-serif, system-ui, sans-serif;
  --mono: ui-monospace, "JetBrains Mono", monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #17140f; --surface: #1f1b15; --text: #e8dfcf; --muted: #a39682;
    --rule: #3a3227; --accent: #e0a24b; --code: #2a241c;
  }}
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
body {{ margin: 0; background: var(--bg); color: var(--text); font: 17px/1.6 var(--font); }}
.layout {{ display: grid; grid-template-columns: 260px minmax(0, 1fr); max-width: 1180px; margin: 0 auto; }}
nav {{ position: sticky; top: 0; align-self: start; height: 100vh; overflow-y: auto;
  padding: 40px 20px 40px 24px; border-right: 1px solid var(--rule); font: 14px/1.4 var(--sans); }}
nav .title {{ font: 600 15px/1.3 var(--sans); margin-bottom: 18px; }}
nav a {{ display: block; color: var(--muted); text-decoration: none; padding: 4px 0; }}
nav a:hover {{ color: var(--accent); }}
nav a.l3 {{ padding-left: 14px; font-size: 13px; }}
main {{ padding: 40px 48px 96px; min-width: 0; }}
h1 {{ font-size: 34px; line-height: 1.2; margin: 0 0 8px; }}
h2 {{ font-size: 24px; margin: 48px 0 12px; padding-top: 16px; border-top: 1px solid var(--rule); }}
h3 {{ font: 600 17px/1.4 var(--sans); margin: 28px 0 8px; color: var(--accent); }}
p, li {{ max-width: 72ch; }}
ul, ol {{ padding-left: 1.3em; }}
li {{ margin: 4px 0; }}
code {{ font: 0.86em var(--mono); background: var(--code); padding: 1px 5px; border-radius: 4px; overflow-wrap: anywhere; }}
a {{ color: var(--accent); }}
table {{ border-collapse: collapse; margin: 16px 0; font: 14px/1.45 var(--sans); width: 100%; display: block; overflow-x: auto; }}
th, td {{ text-align: left; vertical-align: top; padding: 8px 12px; border-bottom: 1px solid var(--rule); }}
th {{ background: var(--surface); font-weight: 600; }}
@media (max-width: 820px) {{
  .layout {{ grid-template-columns: 1fr; }}
  nav {{ position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--rule); padding: 20px 16px; }}
  main {{ padding: 24px 16px 64px; }}
}}
</style>
</head>
<body>
<div class="layout">
<nav aria-label="Contents"><div class="title">{html.escape(title)}</div>{nav}</nav>
<main><h1>{inline(title)}</h1>
{chr(10).join(body)}
</main>
</div>
</body>
</html>
"""
out.write_text(page)
print(f"wrote {out} ({len(toc)} toc entries)")
