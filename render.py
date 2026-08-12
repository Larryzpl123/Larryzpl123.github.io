#!/usr/bin/env python3
"""
render.py — pre-render content.txt into the HTML files.

WHY THIS EXISTS
    index.html used to build its whole body from content.txt with fetch() at
    load time. Anything that does not run JavaScript -- link-preview bots,
    Bing, most LLM/agent crawlers, and any tool someone uses to look you up --
    saw an empty shell with five nav anchors and no text.

    This script writes the rendered HTML directly into the files, between
    <!--R:key--> and <!--/R--> markers, so the content is in the source.
    content.txt stays the only file you edit.

CONTRACT WITH THE BROWSER
    Every run stamps sha256(content.txt) onto <html data-content-hash="...">.
    At load time the page fetches content.txt and re-hashes it:
        hash matches   -> keep the pre-rendered DOM, do nothing
        hash differs   -> re-render from content.txt (content.txt always wins)
                          and show a red STALE banner + console.error
        fetch fails    -> keep the pre-rendered DOM
    So if you edit content.txt and forget to run this, the live site is still
    correct -- it just yells at you until you re-run it.

USAGE
    python3 render.py            rewrite the HTML files in place
    python3 render.py --check    exit 1 if the files are stale (for CI / hooks)

No dependencies. Python 3.8+.
"""

import hashlib
import html as _html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
CONTENT = ROOT / "content.txt"
INDEX = ROOT / "index.html"
WORKS = ROOT / "works" / "index.html"

# Which content.txt section feeds which <section id="..."> on index.html.
# Used to hide a whole section when its content is empty, exactly like the JS did.
SECTION_PARENTS = {
    "about": "about",
    "currently": "currently",
    "research-interests": "research",
    "works": "writing",
    "selected-work": "projects",
    "awards": "awards",
    "contacts": "contact",
}

ROMANS = ["I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII."]

# Order of <section> elements in index.html, by their id.
INDEX_SECTION_ORDER = [
    "about",
    "currently",
    "research",
    "writing",
    "projects",
    "awards",
    "contact",
]


# ---------------------------------------------------------------- parsing
# These four functions are a straight port of the JS in index.html.
# If you change one, change the other, or the two renderers will drift.

def escape_html(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_inline(t):
    h = escape_html(t)
    h = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', h)
    h = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", h)
    h = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", h)
    return h


def render_prose(t):
    paras = [p.strip() for p in re.split(r"\n\s*\n", t)]
    return "".join("<p>%s</p>" % render_inline(p) for p in paras if p)


def parse_entries(t):
    out = []
    for block in re.split(r"\n\s*\n", t):
        block = block.strip()
        if not block:
            continue
        o = {}
        k = None
        for line in block.split("\n"):
            m = re.match(r"^([A-Z][A-Z_]*):\s*(.*)$", line)
            if m:
                k = m.group(1)
                o[k] = m.group(2).strip()
            elif k:
                o[k] += " " + line.strip()
        out.append(o)
    return out


def split_sections(text):
    m = {}
    cur, buf = None, []

    def flush():
        if cur is not None:
            m[cur] = "\n".join(buf).strip()

    for line in text.split("\n"):
        hdr = re.match(r"^===\s*(.+?)\s*===\s*$", line)
        if hdr:
            flush()
            buf = []
            cur = hdr.group(1).strip().lower()
        elif cur is not None:
            buf.append(line)
    flush()
    return m


# ---------------------------------------------------------------- blocks

def project_block(e):
    title = escape_html(e.get("TITLE", ""))
    link = e.get("LINK", "")
    h3 = ('<h3><a href="%s" target="_blank" rel="noopener">%s</a></h3>'
          % (escape_html(link), title)) if link else "<h3>%s</h3>" % title
    return ('<div class="project"><div class="project-tag">%s</div>%s<p>%s</p></div>'
            % (escape_html(e.get("TAG", "")), h3,
               render_inline(e.get("DESCRIPTION", ""))))


def award_block(e):
    name = escape_html(e.get("NAME", ""))
    link = e.get("LINK", "")
    if link:
        name = ('<a href="%s" target="_blank" rel="noopener">%s</a>'
                % (escape_html(link), name))
    return ('<li><span class="award-year">%s</span>'
            '<span class="award-name">%s</span>'
            '<span class="award-detail">%s</span></li>'
            % (escape_html(e.get("YEAR", "")), name,
               escape_html(e.get("DETAIL", ""))))


def contact_block(e):
    value = render_inline(e.get("VALUE", ""))
    link = e.get("LINK", "")
    if link:
        value = '<a href="%s">%s</a>' % (escape_html(link), value)
    return ('<div class="contact-item"><div class="contact-label">%s</div>'
            '<div class="contact-value">%s</div></div>'
            % (escape_html(e.get("LABEL", "")), value))


def works_list_block(e):
    """The flatter row layout used by works/index.html."""
    title = escape_html(e.get("TITLE", ""))
    link = e.get("LINK", "")
    h3 = ('<h3><a href="%s" target="_blank" rel="noopener">%s</a></h3>'
          % (escape_html(link), title)) if link else "<h3>%s</h3>" % title
    return ('<div class="item"><div class="tag">%s</div>%s<p>%s</p></div>'
            % (escape_html(e.get("TAG", "")), h3,
               render_inline(e.get("DESCRIPTION", ""))))


# ---------------------------------------------------------------- writing

MARKER = r"(<!--R:%s-->)(.*?)(<!--/R-->)"


def put(doc, key, inner):
    pat = MARKER % re.escape(key)
    if not re.search(pat, doc, re.S):
        raise SystemExit(
            "render.py: no <!--R:%s--> ... <!--/R--> marker found. "
            "The HTML file has drifted from what this script expects." % key)
    return re.sub(pat, lambda m: m.group(1) + inner + m.group(3), doc, flags=re.S)


def set_hash(doc, digest):
    if re.search(r'<html([^>]*)\sdata-content-hash="[^"]*"', doc):
        return re.sub(r'(<html[^>]*\sdata-content-hash=")[^"]*(")',
                      r"\g<1>%s\g<2>" % digest, doc)
    return re.sub(r"<html(\s|>)",
                  lambda m: '<html data-content-hash="%s"%s' % (digest, m.group(1)),
                  doc, count=1)


def hide_section(doc, sec_id, hidden):
    """Add or remove style="display:none" on <section id="...">."""
    pat = r'(<section id="%s")((?:\s+style="[^"]*")?)' % re.escape(sec_id)
    repl = r'\1 style="display:none"' if hidden else r"\1"
    return re.sub(pat, repl, doc)


def renumber(doc, visible_ids):
    """Rewrite the .section-num roman numerals over only the visible sections."""
    n = {sid: ROMANS[i] if i < len(ROMANS) else ""
         for i, sid in enumerate(visible_ids)}

    def one(m):
        sid = m.group(1)
        if sid not in n:
            return m.group(0)
        return re.sub(r'(<div class="section-num">)[^<]*(</div>)',
                      lambda x: x.group(1) + n[sid] + x.group(2),
                      m.group(0), count=1)

    return re.sub(r'<section id="([^"]+)".*?</section>', one, doc, flags=re.S)


# ---------------------------------------------------------------- main

def build():
    text = CONTENT.read_bytes().decode("utf-8-sig")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    S = split_sections(text)

    def has(k):
        return bool(S.get(k, "").strip())

    # ---- index.html
    doc = INDEX.read_text(encoding="utf-8")

    doc = put(doc, "intro",
              render_inline(S["intro"].strip()) if has("intro") else "")
    for k in ("about", "currently", "research-interests"):
        doc = put(doc, k, render_prose(S[k]) if has(k) else "")
    for k in ("works", "selected-work"):
        doc = put(doc, k,
                  "".join(project_block(e) for e in parse_entries(S[k]))
                  if has(k) else "")
    doc = put(doc, "awards",
              "".join(award_block(e) for e in parse_entries(S["awards"]))
              if has("awards") else "")
    doc = put(doc, "contacts",
              "".join(contact_block(e) for e in parse_entries(S["contacts"]))
              if has("contacts") else "")

    hidden = {SECTION_PARENTS[k] for k in SECTION_PARENTS if not has(k)}
    for sid in INDEX_SECTION_ORDER:
        doc = hide_section(doc, sid, sid in hidden)
    doc = renumber(doc, [s for s in INDEX_SECTION_ORDER if s not in hidden])
    doc = set_hash(doc, digest)

    # ---- works/index.html
    wdoc = WORKS.read_text(encoding="utf-8")
    wdoc = put(wdoc, "works",
               "".join(works_list_block(e) for e in parse_entries(S["works"]))
               if has("works") else "")
    wdoc = set_hash(wdoc, digest)

    return {INDEX: doc, WORKS: wdoc}, digest


def main():
    check = "--check" in sys.argv
    files, digest = build()
    stale = [p for p, new in files.items()
             if p.read_text(encoding="utf-8") != new]

    if check:
        if stale:
            print("STALE: " + ", ".join(str(p.relative_to(ROOT)) for p in stale))
            print("content.txt sha256 = %s" % digest)
            print("Run:  python3 render.py")
            return 1
        print("OK — pre-rendered HTML matches content.txt (%s)" % digest[:12])
        return 0

    for p, new in files.items():
        p.write_text(new, encoding="utf-8")
        print(("updated  " if p in stale else "unchanged ") +
              str(p.relative_to(ROOT)))
    print("content.txt sha256 = %s" % digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
