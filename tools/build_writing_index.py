#!/usr/bin/env python3
"""Build writing/index.html from tools/writing.json.

Usage:
  python3 tools/build_writing_index.py

writing.json holds every piece once (under "pieces") and says where it shows:
"featured" for the highlights at the top, and each track's "series" (in
reading order) and "standalone" lists. A track with no pieces is not shown.
A piece with "url": null is listed without a link (e.g. a draft with no page yet).
Edit the JSON and rebuild; don't hand-edit the generated HTML.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "writing.json"
TEMPLATE = ROOT / "tools" / "writing_index_template.html"

e = html.escape


def badges(p):
    return (f'<span class="project-badge">{e(p["status"])}</span>'
            f'<span class="project-badge type">{e(p["type"])}</span>')


def tags(p):
    return "".join(f'<span class="tag">{e(t)}</span>' for t in p.get("tags", []))


def featured_card(p):
    link = f'<div class="project-links"><a href="{e(p["url"])}" class="proj-link">Read →</a></div>' if p["url"] else ""
    return f'''      <div class="project-card featured-card">
        <div class="project-meta">{badges(p)}</div>
        <div class="project-title">{e(p["title"])}</div>
        <p class="project-desc">{e(p["summary"])}</p>
        <div class="tag-row">{tags(p)}</div>
        {link}
      </div>'''


def entry(p, num=None):
    title = (f'<a href="{e(p["url"])}" class="entry-title">{e(p["title"])}</a>' if p["url"]
             else f'<span class="entry-title">{e(p["title"])}</span>')
    cls = "entry pending" if p["status"] == "Coming soon" else "entry"
    num_html = f'<span class="entry-num">{num:02d}</span>' if num else ""
    return f'''        <li class="{cls}">{num_html}<div>
          {title}
          <div class="entry-meta">{badges(p)}</div>
          <p class="entry-desc">{e(p["summary"])}</p>
        </div></li>'''


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    pieces = data["pieces"]
    for slug in data["featured"] + [s for t in data["tracks"] for ser in t["series"] for s in ser["pieces"]] + \
            [s for t in data["tracks"] for s in t["standalone"]]:
        if slug not in pieces:
            raise SystemExit(f"unknown piece: {slug}")

    out = [f'''  <div class="page-wrap">
    <div class="fade-up">
      <div class="page-eyebrow">writing</div>
      <h1 class="page-title">Writing</h1>
      <p class="page-sub intro-sub">{e(data["intro"])}</p>
    </div>''']

    if data["featured"]:
        out.append('    <div class="ruled-divider fade-up"><span>// featured</span></div>\n    <div class="fade-up">')
        out += [featured_card(pieces[s]) for s in data["featured"]]
        out.append("    </div>")

    for t in data["tracks"]:
        if not (any(ser["pieces"] for ser in t["series"]) or t["standalone"]):
            continue
        out.append(f'''    <div class="ruled-divider fade-up"><span>// {e(t["name"].lower())}</span></div>
    <section class="track fade-up">
      <h2 class="track-name">{e(t["name"])}</h2>
      <p class="track-blurb">{e(t["blurb"])}</p>''')
        for ser in t["series"]:
            out.append(f'      <div class="series-label">SERIES · {e(ser["name"].upper())}</div>\n      <ol class="entry-list">')
            out += [entry(pieces[s], i) for i, s in enumerate(ser["pieces"], 1)]
            out.append("      </ol>")
        if t["standalone"]:
            out.append('      <ul class="entry-list unnumbered">')
            out += [entry(pieces[s]) for s in t["standalone"]]
            out.append("      </ul>")
        out.append("    </section>")
    out.append("  </div>\n")

    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("{{DESCRIPTION}}", e(data["intro"])).replace("{{CONTENT}}\n", "\n".join(out) + "\n")
    dest = ROOT / "writing" / "index.html"
    dest.write_text(page, encoding="utf-8")
    print(f"wrote {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
