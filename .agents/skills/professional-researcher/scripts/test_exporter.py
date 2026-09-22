"""
Automated Test Suite for Professional Researcher v2.0.
Tests:
1. Parser unit tests (nested bullets, images, blockquotes, inline runs, numbered list fix)
2. English full-scale document export (PDF + Word DOCX)
3. Arabic & Multilingual RTL document export (PDF + Word DOCX)
4. File sizes, structural validity, and block type correctness

Run with: pytest test_exporter.py -v
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "examples")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from export_engine import (
    parse_markdown_blocks,
    parse_frontmatter,
    parse_inline_runs,
    clean_markdown_inline,
    clean_markdown_for_docx,
    convert_file,
)


# =============================================================================
# Parser Unit Tests
# =============================================================================

class TestParseMarkdownBlocks:
    """Tests for the Markdown block parser."""

    def test_heading_levels(self):
        md = "# H1\n## H2\n### H3\n#### H4"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 4
        assert blocks[0] == {"type": "heading", "level": 1, "text": "H1"}
        assert blocks[1] == {"type": "heading", "level": 2, "text": "H2"}
        assert blocks[2] == {"type": "heading", "level": 3, "text": "H3"}
        assert blocks[3] == {"type": "heading", "level": 4, "text": "H4"}

    def test_paragraph(self):
        md = "This is a paragraph\nthat spans two lines."
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "paragraph"
        assert "This is a paragraph that spans two lines." == blocks[0]["text"]

    def test_code_block_with_language(self):
        md = "```python\ndef hello():\n    pass\n```"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "code"
        assert blocks[0]["language"] == "python"
        assert "def hello():" in blocks[0]["text"]

    def test_code_block_without_language(self):
        md = "```\nsome code\n```"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "code"
        assert blocks[0]["language"] == ""

    def test_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "table"
        assert blocks[0]["headers"] == ["A", "B"]
        assert blocks[0]["rows"] == [["1", "2"], ["3", "4"]]

    def test_horizontal_rule(self):
        md = "---"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "hr"


class TestNestedBullets:
    """Tests for nested bullet support with indent levels."""

    def test_flat_bullet(self):
        md = "- item one\n- item two"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 2
        assert all(b["type"] == "bullet" for b in blocks)
        assert blocks[0]["indent"] == 0
        assert blocks[1]["indent"] == 0

    def test_nested_bullet_level_1(self):
        md = "- parent\n  - child"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 2
        assert blocks[0]["indent"] == 0
        assert blocks[1]["indent"] == 1

    def test_nested_bullet_level_2(self):
        md = "- parent\n  - child\n      - grandchild"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 3
        assert blocks[0]["indent"] == 0
        assert blocks[1]["indent"] == 1
        assert blocks[2]["indent"] == 2

    def test_asterisk_bullets(self):
        md = "* item a\n  * item b"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 2
        assert blocks[0]["indent"] == 0
        assert blocks[1]["indent"] == 1

    def test_numbered_list(self):
        md = "1. first\n2. second"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 2
        assert all(b["type"] == "bullet" for b in blocks)
        assert blocks[0]["text"] == "first"


class TestImageBlock:
    """Tests for image/figure block detection."""

    def test_image_detected(self):
        md = "![My diagram](images/diagram.png)"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "image"
        assert blocks[0]["alt"] == "My diagram"
        assert blocks[0]["path"] == "images/diagram.png"

    def test_image_with_input_dir(self):
        md = "![Chart](chart.png)"
        blocks = parse_markdown_blocks(md, input_dir="/home/user/docs")
        assert len(blocks) == 1
        assert blocks[0]["type"] == "image"
        expected_path = os.path.join("/home/user/docs", "chart.png")
        assert blocks[0]["path"] == expected_path

    def test_image_with_absolute_path(self):
        md = "![Logo](/absolute/path/logo.png)"
        blocks = parse_markdown_blocks(md, input_dir="/other/dir")
        assert len(blocks) == 1
        assert blocks[0]["path"] == "/absolute/path/logo.png"

    def test_image_empty_alt(self):
        md = "![](pic.jpg)"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["alt"] == ""


class TestBlockquoteVsCallout:
    """Tests that plain blockquotes are distinguished from GitHub-style alert callouts."""

    def test_plain_blockquote(self):
        md = "> This is a simple quote."
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "blockquote"
        assert blocks[0]["text"] == "This is a simple quote."

    def test_callout_note(self):
        md = "> [!NOTE]\n> This is a note."
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "callout"
        assert blocks[0]["callout_type"] == "note"

    def test_callout_warning(self):
        md = "> [!WARNING]\n> Be careful!"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "callout"
        assert blocks[0]["callout_type"] == "warning"

    def test_callout_important(self):
        md = "> [!IMPORTANT]\n> Critical info."
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "callout"
        assert blocks[0]["callout_type"] == "important"

    def test_callout_tip(self):
        md = "> [!TIP]\n> Helpful advice."
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "callout"
        assert blocks[0]["callout_type"] == "tip"

    def test_multiline_blockquote(self):
        md = "> Line one\n> Line two"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "blockquote"
        assert "Line one" in blocks[0]["text"]
        assert "Line two" in blocks[0]["text"]


class TestNumberedListFalsePositive:
    """Tests that numbered list regex doesn't capture non-list content."""

    def test_sentence_with_number(self):
        """A sentence like '3 years later...' should NOT be a bullet."""
        md = "3 years later the project was completed."
        blocks = parse_markdown_blocks(md)
        # Should be a paragraph, not a bullet
        assert len(blocks) == 1
        assert blocks[0]["type"] == "paragraph"

    def test_real_numbered_list(self):
        md = "1. First item\n2. Second item"
        blocks = parse_markdown_blocks(md)
        assert len(blocks) == 2
        assert all(b["type"] == "bullet" for b in blocks)


class TestInlineRuns:
    """Tests for the parse_inline_runs() function."""

    def test_plain_text(self):
        runs = parse_inline_runs("Hello world")
        assert len(runs) == 1
        assert runs[0] == {"text": "Hello world", "bold": False, "italic": False, "code": False}

    def test_bold(self):
        runs = parse_inline_runs("This is **bold** text")
        assert len(runs) == 3
        assert runs[1]["text"] == "bold"
        assert runs[1]["bold"] is True

    def test_italic(self):
        runs = parse_inline_runs("This is *italic* text")
        assert len(runs) == 3
        assert runs[1]["text"] == "italic"
        assert runs[1]["italic"] is True

    def test_code(self):
        runs = parse_inline_runs("Use `kubectl` for this")
        assert len(runs) == 3
        assert runs[1]["text"] == "kubectl"
        assert runs[1]["code"] is True

    def test_mixed_formatting(self):
        runs = parse_inline_runs("**bold** and *italic* and `code`")
        bold_runs = [r for r in runs if r["bold"]]
        italic_runs = [r for r in runs if r["italic"]]
        code_runs = [r for r in runs if r["code"]]
        assert len(bold_runs) == 1
        assert len(italic_runs) == 1
        assert len(code_runs) == 1


class TestFrontmatter:
    """Tests for YAML frontmatter extraction."""

    def test_with_frontmatter(self):
        content = '---\ntitle: "My Report"\nauthor: "Analyst"\n---\n# Content'
        meta, remaining = parse_frontmatter(content)
        assert meta["title"] == "My Report"
        assert meta["author"] == "Analyst"
        assert remaining.strip() == "# Content"

    def test_without_frontmatter(self):
        content = "# Just content"
        meta, remaining = parse_frontmatter(content)
        assert meta == {}
        assert remaining == content


class TestCleanMarkdown:
    """Tests for inline markdown cleaning functions."""

    def test_clean_inline_bold(self):
        result = clean_markdown_inline("**bold**")
        assert "<b>bold</b>" in result

    def test_clean_for_docx_strips(self):
        result = clean_markdown_for_docx("**bold** and `code`")
        assert "**" not in result
        assert "`" not in result
        assert "bold" in result
        assert "code" in result


# =============================================================================
# Integration Tests (Full Export Pipeline)
# =============================================================================

class TestEnglishExport:
    """Integration test: English full-scale research deliverables."""

    def test_english_dual_export(self):
        en_input = os.path.join(EXAMPLES_DIR, "sample_research_input.md")
        en_pdf = os.path.join(EXAMPLES_DIR, "sample_research_output.pdf")
        en_docx = os.path.join(EXAMPLES_DIR, "sample_research_output.docx")

        assert os.path.exists(en_input), f"English sample input missing: {en_input}"

        res = convert_file(input_path=en_input, pdf_path=en_pdf, docx_path=en_docx)
        assert os.path.exists(en_pdf), "English PDF was not generated!"
        assert os.path.exists(en_docx), "English DOCX was not generated!"

        en_pdf_kb = os.path.getsize(en_pdf) / 1024
        en_docx_kb = os.path.getsize(en_docx) / 1024
        assert en_pdf_kb > 10, f"English PDF suspiciously small: {en_pdf_kb} KB"
        assert en_docx_kb > 10, f"English DOCX suspiciously small: {en_docx_kb} KB"
        print(f"  ✓ English PDF:  {en_pdf} ({en_pdf_kb:.1f} KB)")
        print(f"  ✓ English DOCX: {en_docx} ({en_docx_kb:.1f} KB)")


class TestArabicExport:
    """Integration test: Arabic & Multilingual RTL research deliverables."""

    def test_arabic_dual_export(self):
        ar_input = os.path.join(EXAMPLES_DIR, "sample_arabic_research.md")
        ar_pdf = os.path.join(EXAMPLES_DIR, "sample_arabic_research.pdf")
        ar_docx = os.path.join(EXAMPLES_DIR, "sample_arabic_research.docx")

        assert os.path.exists(ar_input), f"Arabic sample input missing: {ar_input}"

        res = convert_file(input_path=ar_input, pdf_path=ar_pdf, docx_path=ar_docx)
        assert os.path.exists(ar_pdf), "Arabic PDF was not generated!"
        assert os.path.exists(ar_docx), "Arabic DOCX was not generated!"

        ar_pdf_kb = os.path.getsize(ar_pdf) / 1024
        ar_docx_kb = os.path.getsize(ar_docx) / 1024
        assert ar_pdf_kb > 10, f"Arabic PDF suspiciously small: {ar_pdf_kb} KB"
        assert ar_docx_kb > 10, f"Arabic DOCX suspiciously small: {ar_docx_kb} KB"
        print(f"  ✓ Arabic PDF:  {ar_pdf} ({ar_pdf_kb:.1f} KB)")
        print(f"  ✓ Arabic DOCX: {ar_docx} ({ar_docx_kb:.1f} KB)")


# Legacy runner compatibility
def run_all_tests():
    """Legacy runner for backward compatibility. Prefer: pytest test_exporter.py -v"""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=False
    )
    return result.returncode


if __name__ == "__main__":
    run_all_tests()
