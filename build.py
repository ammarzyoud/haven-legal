#!/usr/bin/env python3
"""
Generate the published HTML pages from the plain-text sources in src/.

The text files are the single source of truth — edit those, run this, commit.
The internal "READ BEFORE PUBLISHING" note is addressed to the Haven team and
is stripped from the public pages.

Usage:  python3 build.py
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"

PAGES = [
    ("privacy-policy.txt", "privacy.html", "Privacy Policy"),
    ("terms-of-service.txt", "terms.html", "Terms of Service"),
]

CSS = """
:root {
  --sand: #F5F0E8;
  --ink: #1A1612;
  --ink-soft: #4A4038;
  --muted: #8A8175;
  --gold: #C4A86B;
  --white: #FEFCF8;
  --rule: #E4DBCC;
  color-scheme: light;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--sand);
  color: var(--ink);
  font: 16px/1.65 "DM Sans", system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 780px; margin: 0 auto; padding: 56px 20px 96px; }
header { border-bottom: 1px solid var(--rule); padding-bottom: 28px; margin-bottom: 40px; }
.brand {
  font: 400 15px/1 "DM Sans", sans-serif;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--muted);
  text-decoration: none;
}
h1 {
  font: 400 40px/1.1 "Cormorant Garamond", Georgia, serif;
  letter-spacing: -0.01em;
  margin: 18px 0 10px;
}
.dates { color: var(--muted); font-size: 14px; margin: 0; }
h2 {
  font: 400 26px/1.25 "Cormorant Garamond", Georgia, serif;
  margin: 46px 0 14px;
  padding-top: 18px;
  border-top: 1px solid var(--rule);
}
h3 {
  font: 500 15px/1.4 "DM Sans", sans-serif;
  letter-spacing: 0.04em;
  margin: 28px 0 10px;
  color: var(--ink-soft);
}
p { margin: 0 0 16px; color: var(--ink-soft); }
ul { margin: 0 0 18px; padding-left: 22px; color: var(--ink-soft); }
li { margin-bottom: 7px; }
pre {
  background: var(--white);
  border: 1px solid var(--rule);
  border-left: 3px solid var(--gold);
  padding: 16px 18px;
  overflow-x: auto;
  font: 13px/1.6 ui-monospace, SFMono-Regular, Menlo, monospace;
  color: var(--ink-soft);
  margin: 0 0 20px;
  white-space: pre;
}
strong { color: var(--ink); font-weight: 600; }
a { color: var(--ink); text-decoration: underline; text-decoration-color: var(--gold); }
footer {
  margin-top: 64px; padding-top: 24px;
  border-top: 1px solid var(--rule);
  color: var(--muted); font-size: 13px;
}
footer a { color: var(--muted); }
@media (max-width: 480px) {
  .wrap { padding: 36px 16px 64px; }
  h1 { font-size: 32px; }
  h2 { font-size: 22px; }
}
"""

SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} — Haven</title>
<meta name="description" content="{title} for Haven, a luxury residential real estate platform in Amman, Jordan.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="wrap">
<header>
  <a class="brand" href="./">Haven</a>
  <h1>{title}</h1>
  {dates}
</header>
{body}
<footer>
  <p>Haven — luxury residential real estate, Amman, Jordan.<br>
  <a href="./privacy.html">Privacy Policy</a> &middot; <a href="./terms.html">Terms of Service</a></p>
</footer>
</div>
</body>
</html>
"""


def strip_internal_note(lines):
    """Drop the team-facing note that sits above section 1."""
    start = next((i for i, l in enumerate(lines) if l.startswith("IMPORTANT")), None)
    if start is None:
        return lines
    end = next((i for i, l in enumerate(lines) if re.match(r"^1\.\s", l)), None)
    if end is None:
        return lines
    return lines[:start] + lines[end:]


SMALL_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "nor",
    "of", "on", "or", "so", "the", "to", "up", "with", "yet",
}


def title_case(text):
    """Title-case a heading: small words stay lowercase, except first and last."""
    words = text.lower().split()
    last = len(words) - 1
    out = []
    for i, w in enumerate(words):
        keep_lower = 0 < i < last and w in SMALL_WORDS
        out.append(w if keep_lower else w[:1].upper() + w[1:])
    return " ".join(out)


def inline(text):
    """Escape, then mark bracket placeholders and ALL-CAPS emphasis."""
    out = html.escape(text)
    # Make the remaining fill-me-in placeholders visually obvious
    out = re.sub(r"(\[[^\]]+\])", r"<strong>\1</strong>", out)
    return out


def render(lines):
    blocks, para, bullets, pre = [], [], [], []

    def flush():
        if para:
            blocks.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()
        if bullets:
            items = "".join(f"<li>{inline(b)}</li>" for b in bullets)
            blocks.append(f"<ul>{items}</ul>")
            bullets.clear()
        if pre:
            while pre and not pre[-1].strip():
                pre.pop()
            blocks.append("<pre>" + "\n".join(html.escape(p) for p in pre) + "</pre>")
            pre.clear()

    for raw in lines:
        line = raw.rstrip()

        # Section heading: "7. PROPERTY OWNER ACCOUNTS"
        if re.match(r"^\d+\.\s+\S", line):
            flush()
            num, _, rest = line.partition(".")
            blocks.append(f"<h2>{num}. {inline(title_case(rest.strip()))}</h2>")
            continue

        # Sub-heading: "3.1 When you request a property viewing"
        if re.match(r"^\d+\.\d+\s+\S", line):
            flush()
            blocks.append(f"<h3>{inline(line)}</h3>")
            continue

        # Bullet
        m = re.match(r"^\s+-\s+(.*)$", line)
        if m:
            if para:
                flush()
            bullets.append(m.group(1))
            continue

        # Continuation of a bullet
        if bullets and line.startswith("    ") and line.strip():
            bullets[-1] += " " + line.strip()
            continue

        # Indented, column-aligned content (tables, key/value) -> preformatted
        if line.startswith("  ") and re.search(r"\S\s{2,}\S", line):
            if para or bullets:
                flush()
            pre.append(line)
            continue

        if pre and line.startswith("  ") and line.strip():
            pre.append(line)
            continue

        if not line.strip():
            flush()
            continue

        if pre:
            flush()
        para.append(line.strip())

    flush()
    return "\n".join(blocks)


def build_page(src_name, out_name, title):
    lines = (SRC / src_name).read_text(encoding="utf-8").splitlines()

    # Pull the two date lines out for the header, drop the ALL-CAPS title line
    dates = [l for l in lines[:6] if l.startswith(("Last updated", "Effective date"))]
    dates_html = (
        '<p class="dates">' + "<br>".join(inline(d) for d in dates) + "</p>"
        if dates else ""
    )

    body_lines = strip_internal_note(lines)
    body_lines = [
        l for l in body_lines
        if not l.startswith(("HAVEN —", "Last updated", "Effective date"))
    ]

    page = SHELL.format(
        title=title, css=CSS, dates=dates_html, body=render(body_lines)
    )
    (ROOT / out_name).write_text(page, encoding="utf-8")
    print(f"  {src_name} -> {out_name} ({len(page):,} bytes)")


def build_index():
    body = """
<p>Haven is a luxury residential real estate platform serving Amman, Jordan.
These are the policies that govern use of our platform.</p>
<ul>
  <li><a href="./privacy.html">Privacy Policy</a> — what data we collect, why, and your rights under Jordan's Personal Data Protection Law.</li>
  <li><a href="./terms.html">Terms of Service</a> — the terms on which we provide the platform, including listing and advertising terms for property owners.</li>
</ul>
"""
    page = SHELL.format(title="Legal", css=CSS, dates="", body=body)
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print(f"  index.html ({len(page):,} bytes)")


if __name__ == "__main__":
    print("Building Haven legal pages:")
    for args in PAGES:
        build_page(*args)
    build_index()

    remaining = sum(
        len(re.findall(r"\[[A-Z][^\]]*\]", (SRC / s).read_text(encoding="utf-8")))
        for s, _, _ in PAGES
    )
    print(f"\nDone. {remaining} unfilled [PLACEHOLDER]s remain in src/.")
