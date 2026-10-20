"""tools/markdown_lite.py — a tiny, dependency-free Markdown-to-HTML renderer for the
dashboard's report pages (headings, paragraphs, bullet lists, pipe tables, bold, inline
code, fenced code). Everything is HTML-escaped first; there is no raw-HTML passthrough.
Not a full Markdown implementation on purpose: the learning-loop reports only use this
subset, and the page must never break on a report it cannot parse (unknown lines become
paragraphs)."""
from __future__ import annotations

import html
import re

_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`]+)`")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def _inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = _CODE.sub(r"<code>\1</code>", out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _LINK.sub(r'<a href="\2">\1</a>', out)
    return out


def _is_table_sep(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and set(s.replace("|", "").replace(":", "").strip()) <= {"-", " "} and "-" in s


def _cells(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def render(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    in_list = False
    para: list[str] = []

    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + " ".join(_inline(x) for x in para) + "</p>")
            para = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            flush_para(); close_list()
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(lines[j]); j += 1
            out.append("<pre><code>" + html.escape("\n".join(buf), quote=False) + "</code></pre>")
            i = j + 1
            continue
        if not s:
            flush_para(); close_list(); i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            flush_para(); close_list()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{_inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        if s.startswith("|") and i + 1 < len(lines) and _is_table_sep(lines[i + 1]):
            flush_para(); close_list()
            head = _cells(s)
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(_cells(lines[j])); j += 1
            t = ["<table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in head) + "</tr></thead><tbody>"]
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            i = j
            continue
        m = re.match(r"^[-*]\s+(.*)$", s)
        if m:
            flush_para()
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{_inline(m.group(1))}</li>")
            i += 1
            continue
        if s.startswith("_") and s.endswith("_") and len(s) > 2:
            flush_para(); close_list()
            out.append(f"<p><em>{_inline(s[1:-1])}</em></p>")
            i += 1
            continue
        close_list()
        para.append(s)
        i += 1
    flush_para(); close_list()
    return "\n".join(out)
