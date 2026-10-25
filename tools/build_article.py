#!/usr/bin/env python3
"""Build a long-form article page for /writing/<slug>/ from a Markdown source.

Usage:
  python3 tools/build_article.py SOURCE.md SLUG [--type Essay|Paper|Lab] [--tags "A,B,C"] [--description "..."]

The source keeps its own title (the first "# " heading) and status line (the
first paragraph after it, e.g. "Draft. Jeff Hanna."). Edit the source and
rebuild; don't hand-edit the generated HTML.

Supported Markdown: #/##/### headings, paragraphs, ordered and unordered lists
(with wrapped continuation lines), pipe tables, `code`, [links](url), *em* and
**strong**. That covers the essays; extend here if a new piece needs more.
"""
import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "tools" / "article_template.html"


def slugify(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"^\d+\.\s*", "", text)
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def inline(text):
    # Pull code spans out first so nothing inside them is formatted.
    codes = []

    def stash(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>',
        text,
    )
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(
        r"\x00(\d+)\x00",
        lambda m: f"<code>{html.escape(codes[int(m.group(1))], quote=False)}</code>",
        text,
    )


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(lines):
    """Return (blocks_html, toc) for the body below the title and status line."""
    out, toc = [], []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue

        m = re.match(r"^(#{2,3})\s+(.*)$", s)
        if m:
            level = len(m.group(1))
            text = inline(m.group(2))
            hid = slugify(m.group(2))
            if level == 2:
                toc.append((hid, text))
            out.append(f'<h{level} id="{hid}">{text}</h{level}>')
            i += 1
            continue

        if s.startswith("|") and i + 1 < n and re.match(r"^\|?[\s:|-]+\|?$", lines[i + 1].strip()):
            head = split_row(s)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            th = "".join(f"<th>{inline(h)}</th>" for h in head)
            body = []
            for r in rows:
                tds = "".join(
                    f'<td data-label="{html.escape(re.sub(r"[`*]", "", head[k]))}">{inline(c)}</td>'
                    for k, c in enumerate(r)
                )
                body.append(f"<tr>{tds}</tr>")
            out.append(
                f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead>'
                f'<tbody>{"".join(body)}</tbody></table></div>'
            )
            continue

        lm = re.match(r"^(\d+\.|[-*])\s+(.*)$", s)
        if lm:
            ordered = lm.group(1)[0].isdigit()
            items = []
            while i < n:
                cur = lines[i]
                m2 = re.match(r"^(\d+\.|[-*])\s+(.*)$", cur.strip())
                if m2 and not cur.startswith(" "):
                    items.append(m2.group(2))
                elif cur.startswith(" ") and cur.strip() and items:
                    items[-1] += " " + cur.strip()
                else:
                    break
                i += 1
            tag = "ol" if ordered else "ul"
            lis = "".join(f"<li>{inline(t)}</li>" for t in items)
            out.append(f"<{tag}>{lis}</{tag}>")
            continue

        para = []
        while i < n and lines[i].strip() and not re.match(r"^(#{1,3}\s|\||\d+\.\s|[-*]\s)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out), toc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("slug")
    ap.add_argument("--type", default="Essay")
    ap.add_argument("--tags", default="")
    ap.add_argument("--description", default="")
    args = ap.parse_args()

    lines = Path(args.source).read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# "):
        sys.exit("source must start with a '# ' title")
    title = lines[0][2:].strip()

    # First paragraph after the title is the status/byline line.
    i = 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    status = []
    while i < len(lines) and lines[i].strip():
        status.append(lines[i].strip())
        i += 1
    status = " ".join(status)

    body, toc = convert(lines[i:])
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    minutes = max(1, round(words / 230))

    tags = "".join(f'<span class="tag">{html.escape(t.strip())}</span>' for t in args.tags.split(",") if t.strip())
    toc_html = "".join(f'<li><a href="#{hid}">{text}</a></li>' for hid, text in toc)

    page = TEMPLATE.read_text(encoding="utf-8")
    for key, val in {
        "TITLE": html.escape(title),
        "TYPE": html.escape(args.type),
        "DESCRIPTION": html.escape(args.description),
        "STATUS": inline(status),
        "TAGS": tags,
        "READ_TIME": f"{minutes} min read",
        "TOC": toc_html,
        "BODY": body,
    }.items():
        page = page.replace("{{" + key + "}}", val)

    dest = ROOT / "writing" / args.slug / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")
    print(f"wrote {dest.relative_to(ROOT)} ({words} words, {len(toc)} sections)")


if __name__ == "__main__":
    main()
