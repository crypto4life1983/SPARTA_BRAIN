import sys

sys.path.insert(0, r"C:\SPARTA_BRAIN")
from tools import markdown_lite as ml  # noqa: E402


def test_headings_bullets_and_paragraphs():
    h = ml.render("# Title\n\nSome **bold** and `code`.\n\n- one\n- two\n\nnext para")
    assert "<h1>Title</h1>" in h and "<strong>bold</strong>" in h and "<code>code</code>" in h
    assert "<ul>\n<li>one</li>\n<li>two</li>\n</ul>" in h and "<p>next para</p>" in h


def test_pipe_table_renders_with_header_and_rows():
    md = "| a | b |\n|---|---|\n| 1 | **2** |\n| 3 | 4 |\n\ntail"
    h = ml.render(md)
    assert h.count("<tr>") == 3 and "<th>a</th>" in h and "<td><strong>2</strong></td>" in h and "<p>tail</p>" in h


def test_html_is_escaped_and_fences_kept():
    h = ml.render("<script>x</script>\n\n```\na < b\n```")
    assert "<script>" not in h and "&lt;script&gt;" in h
    assert "<pre><code>a &lt; b</code></pre>" in h


def test_unknown_lines_never_raise():
    assert ml.render("") == ""
    assert "<p>" in ml.render("| not a table\njust text")
