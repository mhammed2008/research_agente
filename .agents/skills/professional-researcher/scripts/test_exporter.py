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
    parse_presentation_slides,
)
from pptx_builder import PptxReportBuilder


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



# =============================================================================
# Presentation (.pptx) Unit & Integration Tests
# =============================================================================

class TestSlideParsing:
    """Tests for markdown-to-presentation slide segmentation and layout inference."""

    def test_slide_segmentation_hr(self):
        md = "# Main Presentation\nIntro\n---\n## Slide 2\nContent\n---\n## Slide 3\nClosing"
        slides = parse_presentation_slides(md)
        assert len(slides) == 3
        assert slides[0]["title"] == "Main Presentation"
        assert slides[1]["title"] == "Slide 2"
        assert slides[2]["title"] == "Slide 3"

    def test_slide_segmentation_h2(self):
        md = "## Overview\nBullet 1\n\n## Deep Dive\nDetails\n\n## Next Steps\nWrap up"
        slides = parse_presentation_slides(md)
        assert len(slides) == 3
        assert slides[0]["title"] == "Overview"
        assert slides[1]["title"] == "Deep Dive"
        assert slides[2]["title"] == "Next Steps"

    def test_layout_directives(self):
        md = "## Architecture\n<!-- layout: two-column -->\n<!-- category: Infrastructure -->\n### Cloud\n- AWS\n### Edge\n- Cloudflare"
        slides = parse_presentation_slides(md)
        assert len(slides) == 1
        assert slides[0]["layout"] == "two-column"
        assert slides[0]["category"] == "Infrastructure"
        assert slides[0]["col1_title"] == "Cloud"
        assert slides[0]["col2_title"] == "Edge"

    def test_metrics_inference(self):
        md = "## Benchmark Results\n- **99.99%** High Availability | Multi-region\n- **<50ms** Latency | Fast response\n- **3.5x** ROI | Annual savings"
        slides = parse_presentation_slides(md)
        assert len(slides) == 1
        assert slides[0]["layout"] == "metrics"
        assert len(slides[0]["metrics"]) == 3
        assert slides[0]["metrics"][0]["value"] == "99.99%"
        assert slides[0]["metrics"][0]["label"] == "High Availability"
        assert slides[0]["metrics"][0]["sub"] == "Multi-region"


class TestPptxBuilder:
    """Tests for PptxReportBuilder shape, table, and RTL generation."""

    def test_pptx_deck_creation(self, tmp_path):
        out_file = str(tmp_path / "test_deck.pptx")
        builder = PptxReportBuilder(
            filename=out_file,
            title="Enterprise AI Architecture",
            subtitle="Strategic Implementation Roadmap",
            author="Lead Architect",
            organization="TeknoKeys",
            theme="emerald"
        )
        builder.add_title_slide()
        builder.add_agenda_slide(items=["System Overview", "Security Review", "Cost Analysis"])
        builder.add_content_slide(
            title="Core Tenets",
            blocks=[{"type": "bullet", "text": "Zero-trust network model", "indent": 0}],
            category="SECURITY"
        )
        builder.add_two_column_slide(
            title="Framework Evaluation",
            col1_title="Framework A",
            col1_blocks=[{"type": "paragraph", "text": "Lightweight"}],
            col2_title="Framework B",
            col2_blocks=[{"type": "paragraph", "text": "Feature-rich"}],
            category="EVALUATION"
        )
        builder.add_metrics_slide(
            title="Key Performance Metrics",
            metrics=[{"value": "10k+", "label": "Active Nodes", "sub": "Globally distributed"}],
            category="SCALE"
        )
        builder.add_callout_slide(
            title="Compliance Mandate",
            callout_type="important",
            callout_title="PCI DSS v4.0",
            text="Mandatory end-to-end tokenization enforced.",
            category="COMPLIANCE"
        )
        builder.add_table_slide(
            title="Vendor Matrix",
            headers=["Platform", "Latency", "Compliance"],
            rows=[["Platform A", "12ms", "Certified"], ["Platform B", "45ms", "Pending"]],
            category="BENCHMARK"
        )
        builder.add_code_slide(
            title="Runtime Hook",
            code_text="def authenticate(token):\n    return verify_jwt(token)",
            category="SECURITY"
        )
        builder.add_closing_slide()
        builder.save()

        assert os.path.exists(out_file)
        assert os.path.getsize(out_file) > 15000

    def test_pptx_arabic_rtl(self, tmp_path):
        out_file = str(tmp_path / "test_arabic.pptx")
        builder = PptxReportBuilder(
            filename=out_file,
            title="الذكاء الاصطناعي في قطاع المدفوعات",
            subtitle="دراسة معمارية شاملة",
            author="خبير النظم المالية",
            organization="شركة التقنية المتقدمة"
        )
        assert builder.is_rtl_doc is True
        s = builder.add_title_slide()
        tf = next((shp.text_frame for shp in s.shapes if shp.has_text_frame and len(shp.text_frame.paragraphs) > 1), s.shapes[1].text_frame)
        p = tf.paragraphs[1]
        pPr = p._p.get_or_add_pPr()
        assert pPr.get("rtl") == "1"

        builder.add_closing_slide(title="الخاتمة والتوصيات الاستراتيجية")
        builder.save()
        assert os.path.exists(out_file)
        assert os.path.getsize(out_file) > 10000


class TestPptxExportIntegration:
    """Integration test: Full markdown to PPTX export."""

    def test_english_presentation_export(self, tmp_path):
        md_file = tmp_path / "pres.md"
        pptx_file = str(tmp_path / "pres.pptx")
        md_content = """---
title: "Modern AI Engineering"
subtitle: "Production Patterns"
author: "AI Research Team"
organization: "TeknoKeys"
theme: "slate"
---

## Executive Summary
<!-- category: Overview -->
- Multi-agent orchestration architectures
- High-efficiency context pruning
- Real-time attestation and governance

---

## Architectural Comparison
<!-- layout: two-column -->
<!-- category: Architecture -->
### Client Architecture
- Edge rendering
- Local cache

### Cloud Architecture
- Distributed workers
- Vector search

---

## Performance Targets
<!-- layout: metrics -->
<!-- category: Telemetry -->
- **99.9%** Availability | Production uptime
- **<20ms** Latency | P99 API response
- **5.2x** Throughput | Concurrent scale
"""
        md_file.write_text(md_content, encoding="utf-8")
        res = convert_file(input_path=str(md_file), pptx_path=pptx_file)
        assert os.path.exists(pptx_file)
        assert os.path.getsize(pptx_file) > 20000

    def test_arabic_presentation_export(self, tmp_path):
        md_file = tmp_path / "arabic_pres.md"
        pptx_file = str(tmp_path / "arabic_pres.pptx")
        md_content = """---
title: "التحول الرقمي في المدفوعات المالية"
subtitle: "مستقبل المحافظ الرقمية والتقنيات اللاتلامسية"
author: "مستشار التقنية المالية"
organization: "مجموعة جيب المالية"
theme: "emerald"
---

## نظرة عامة على النظام
<!-- category: الملخص التنفيذي -->
- نمو المعاملات اللاتلامسية بنسبة تتجاوز 40% سنوياً
- اعتماد معايير الأمان العالمية PCI MPoC
- تكامل سلس مع منصات التجارة الإلكترونية

---

## مؤشرات الأداء الرئيسية
<!-- layout: metrics -->
<!-- category: المؤشرات -->
- **45%** نمو سنوي | في حجم العمليات
- **99.99%** جاهزية الخدمة | دون توقف
- **<1.2s** زمن تنفيذ العملية | تجربة فائقة السرعة
"""
        md_file.write_text(md_content, encoding="utf-8")
        res = convert_file(input_path=str(md_file), pptx_path=pptx_file)
        assert os.path.exists(pptx_file)
        assert os.path.getsize(pptx_file) > 20000



# =============================================================================
# Dynamic Styles & Brand Logo Integration Tests
# =============================================================================

class TestDynamicStylesAndBranding:
    """Tests for customizable palettes, custom hex colors, and logo embedding."""

    def test_custom_hex_palette_export(self, tmp_path):
        md_file = tmp_path / "custom_style.md"
        pdf_file = str(tmp_path / "custom.pdf")
        docx_file = str(tmp_path / "custom.docx")
        pptx_file = str(tmp_path / "custom.pptx")
        md_content = """---
title: "Custom Brand Evaluation"
subtitle: "Tailored Corporate Identity"
author: "Design Lead"
organization: "Brand Labs"
---

## Executive Overview
- Custom color token application
- Independent primary and accent palettes
"""
        md_file.write_text(md_content, encoding="utf-8")
        res = convert_file(
            input_path=str(md_file),
            pdf_path=pdf_file,
            docx_path=docx_file,
            pptx_path=pptx_file,
            primary_color="#7C3AED",
            accent_color="#10B981"
        )
        assert os.path.exists(pdf_file)
        assert os.path.exists(docx_file)
        assert os.path.exists(pptx_file)
        assert os.path.getsize(pdf_file) > 5000
        assert os.path.getsize(docx_file) > 10000
        assert os.path.getsize(pptx_file) > 15000

    def test_logo_embedding_all_formats(self, tmp_path):
        from PIL import Image, ImageDraw
        logo_path = str(tmp_path / "test_logo.png")
        img = Image.new("RGBA", (300, 100), color=(15, 23, 42, 255))
        d = ImageDraw.Draw(img)
        d.text((20, 35), "BRAND LOGO", fill=(255, 255, 255, 255))
        img.save(logo_path)

        md_file = tmp_path / "logo_report.md"
        pdf_file = str(tmp_path / "logo.pdf")
        docx_file = str(tmp_path / "logo.docx")
        pptx_file = str(tmp_path / "logo.pptx")
        md_content = """---
title: "Branded Report with Custom Logo"
subtitle: "Corporate Identity Integration"
author: "Principal Analyst"
organization: "Enterprise Co"
---

## Key Achievements
- Verified logo embedding on Cover Pages and Slide Headers
- Maintained exact aspect ratio scaling
"""
        md_file.write_text(md_content, encoding="utf-8")
        res = convert_file(
            input_path=str(md_file),
            pdf_path=pdf_file,
            docx_path=docx_file,
            pptx_path=pptx_file,
            logo_path=logo_path
        )
        assert os.path.exists(pdf_file)
        assert os.path.exists(docx_file)
        assert os.path.exists(pptx_file)
        assert os.path.getsize(pdf_file) > 5000
        assert os.path.getsize(docx_file) > 10000
        assert os.path.getsize(pptx_file) > 15000

    def test_style_wizard_loading(self, tmp_path):
        import json
        from style_wizard import load_style_config
        cfg_file = tmp_path / "style.json"
        cfg_data = {
            "style_id": "luxury-violet",
            "primary_color": "#2E1065",
            "accent_color": "#7C3AED"
        }
        cfg_file.write_text(json.dumps(cfg_data), encoding="utf-8")

        loaded = load_style_config(str(cfg_file))
        assert loaded["style_id"] == "luxury-violet"
        assert loaded["primary_color"] == "#2E1065"

        loaded_dict = load_style_config(cfg_data)
        assert loaded_dict["accent_color"] == "#7C3AED"

    def test_color_synthesizer_palette_extraction(self, tmp_path):
        from PIL import Image
        from color_synthesizer import synthesize_palette, hex_to_rgb

        # Create emerald test badge
        logo_path = str(tmp_path / "emerald_logo.png")
        img = Image.new("RGBA", (200, 200), (6, 78, 59, 255))
        img.save(logo_path)

        palette = synthesize_palette(logo_path=logo_path)
        assert "primary" in palette
        assert "accent" in palette
        assert "bg_light" in palette
        assert "card_border" in palette
        assert palette["primary_hex"].startswith("#")
        assert palette["accent_hex"].startswith("#")

    def test_pptx_clean_geometry_and_callout_brackets(self, tmp_path):
        from pptx_builder import PptxReportBuilder
        pptx_path = str(tmp_path / "clean_deck.pptx")
        builder = PptxReportBuilder(
            filename=pptx_path,
            title="Clean Consultant Deck",
            theme="emerald"
        )
        builder.add_title_slide()
        # Test two column slide
        builder.add_two_column_slide(
            title="Comparison",
            col1_title="Left Perspective",
            col1_blocks=[{"type": "bullet", "text": "Bullet 1"}],
            col2_title="Right Perspective",
            col2_blocks=[{"type": "bullet", "text": "Bullet 2"}]
        )
        # Test callout slide - brackets should be removed
        builder.add_callout_slide(
            title="Strategic Mandate",
            callout_type="important",
            callout_title="[CRITICAL DIRECTIVE]",
            text="Executive takeaway without bracket clutter."
        )
        builder.save()
        assert os.path.exists(pptx_path)
        assert os.path.getsize(pptx_path) > 10000


class TestDomainAdaptivePresentationArchetypes:
    """Tests for the 5 structural presentation archetypes and dynamic style parser."""

    def test_archetypes_palette_synthesis(self):
        from color_synthesizer import synthesize_palette

        # 1. Modern Dark
        p_dark = synthesize_palette(archetype="modern_dark")
        assert p_dark["is_dark_canvas"] is True
        assert p_dark["card_framing"] == "translucent"
        # Canvas should be very dark (near black/navy)
        assert p_dark["bg_light"][0] < 30 and p_dark["bg_light"][1] < 30 and p_dark["bg_light"][2] < 40

        # 2. Minimal Editorial
        p_min = synthesize_palette(archetype="minimal_editorial")
        assert p_min["is_dark_canvas"] is False
        assert p_min["card_framing"] == "frameless"
        assert p_min["bg_light"] == (255, 255, 255)

        # 3. Consulting Grid
        p_cg = synthesize_palette(archetype="consulting_grid")
        assert p_cg["card_framing"] == "sharp_card"

        # 4. Warm Organic
        p_warm = synthesize_palette(archetype="warm_organic")
        assert p_warm["card_framing"] == "rounded_card"
        assert p_warm["bg_light"][0] >= 245 and p_warm["bg_light"][1] >= 245 and p_warm["bg_light"][2] >= 240

        # 5. Vibrant Bold
        p_vib = synthesize_palette(archetype="vibrant_bold")
        assert p_vib["card_framing"] == "flat_tile"

    def test_style_prompt_parser(self):
        from style_wizard import parse_style_prompt

        # Dark / Cyber
        res_dark = parse_style_prompt("Please make a sleek obsidian dark theme with cyan neon accents for an AI dev deck")
        assert res_dark["archetype"] == "modern_dark"
        assert res_dark["is_dark_canvas"] is True
        assert res_dark["accent_color"] is not None

        # Minimal / Swiss
        res_min = parse_style_prompt("Clean minimal monochrome black and white Swiss typography, zero cards")
        assert res_min["archetype"] == "minimal_editorial"
        assert res_min["card_framing"] == "frameless"

        # Consulting BCG
        res_cons = parse_style_prompt("Executive corporate McKinsey BCG consulting grid deck with sharp borders and navy tone")
        assert res_cons["archetype"] == "consulting_grid"
        assert res_cons["card_framing"] == "sharp_card"

        # Warm Organic
        res_warm = parse_style_prompt("Earthy warm organic cream canvas with terracotta and sage green colors")
        assert res_warm["archetype"] == "warm_organic"

        # Vibrant Bold
        res_vib = parse_style_prompt("High-energy fintech startup presentation with vibrant bold electric purple")
        assert res_vib["archetype"] == "vibrant_bold"

    def test_pptx_archetype_generation(self, tmp_path):
        from pptx_builder import PptxReportBuilder

        for arch in ["modern_dark", "minimal_editorial", "warm_organic", "vibrant_bold", "consulting_grid"]:
            pptx_path = str(tmp_path / f"deck_{arch}.pptx")
            builder = PptxReportBuilder(
                filename=pptx_path,
                title=f"Sample {arch.replace('_', ' ').title()} Deck",
                subtitle="Domain-Adaptive Style Test",
                author="Senior Architect",
                archetype=arch
            )
            builder.add_title_slide()
            builder.add_agenda_slide([
                {"number": "01", "title": "Market Dynamics", "desc": "Global industry shifts"},
                {"number": "02", "title": "Core Methodology", "desc": "Empirical validation architecture"},
            ])
            builder.add_metrics_slide(
                title="Key Performance Metrics",
                metrics=[
                    {"number": "99.8%", "label": "Accuracy Gate", "desc": "Zero hallucinatory data"},
                    {"number": "4.2x", "label": "Throughput", "desc": "Accelerated synthesis pipeline"},
                ]
            )
            builder.add_two_column_slide(
                title="Comparative Architecture",
                col1_title="Legacy Static Approach",
                col1_blocks=[{"type": "bullet", "text": "Rigid light gray canvas with identical rounded cards"}],
                col2_title="Domain-Adaptive Archetype",
                col2_blocks=[{"type": "bullet", "text": "Tailored structural canvas, typography, and card framing"}]
            )
            builder.add_callout_slide(
                title="Strategic Recommendation",
                callout_type="important",
                callout_title="Mandate",
                text="Adopt archetype synthesis across all executive client decks."
            )
            builder.add_closing_slide()
            builder.save()

            assert os.path.exists(pptx_path)
            assert os.path.getsize(pptx_path) > 12000

    def test_export_engine_archetype_frontmatter(self, tmp_path):
        from export_engine import convert_file

        md_file = tmp_path / "dark_deck.md"
        pptx_file = str(tmp_path / "dark_deck.pptx")
        md_content = """---
title: "Autonomous Agent Security"
subtitle: "AI Safety & Governance"
archetype: "modern_dark"
style_prompt: "dark theme with cyber neon green accents"
---

## Core Findings
- Zero unauthorized privilege escalation
- Real-time telemetry monitoring

| Metric | Target | Result |
|---|---|---|
| Latency | <50ms | 18ms |
| F1 Score | >0.95 | 0.98 |
"""
        md_file.write_text(md_content, encoding="utf-8")
        res = convert_file(
            input_path=str(md_file),
            pptx_path=pptx_file,
            archetype="modern_dark"
        )
        assert os.path.exists(pptx_file)
        assert os.path.getsize(pptx_file) > 15000


class TestMermaidDiagramExport:
    def test_mermaid_vector_pdf_and_docx_export(self, tmp_path):
        from pathlib import Path
        from export_engine import convert_file

        md_file = tmp_path / "diagram_report.md"
        pdf_file = str(tmp_path / "diagram_report.pdf")
        docx_file = str(tmp_path / "diagram_report.docx")
        html_file = str(tmp_path / "diagram_report.html")

        md_content = """---
title: "Decentralized Ledger Architecture"
subtitle: "High-Throughput Cryptographic Pipeline"
---

## System Flow & Validation

Here is the operational lifecycle of an inbound transaction:

```mermaid
flowchart TD
    Start(["Inbound Transaction"]) --> Verify{"Valid Signature?"}
    Verify -- "Yes" --> Commit["ACID Ledger Commit"]
    Verify -- "No" --> Reject["Security Alert"]

    classDef startEnd fill:#1e293b,stroke:#0f172a,stroke-width:2px,color:#ffffff,font-weight:bold;
    classDef process fill:#eff6ff,stroke:#2563eb,stroke-width:1.5px,color:#1e3a8a;
    classDef decision fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f,font-weight:bold;

    class Start startEnd;
    class Commit process;
    class Verify decision;
```

## Summary
The transaction terminates with strict atomic integrity.
"""
        md_file.write_text(md_content, encoding="utf-8")
        res = convert_file(
            input_path=str(md_file),
            html_path=html_file,
            pdf_path=pdf_file,
            docx_path=docx_file
        )
        assert os.path.exists(html_file)
        assert "<pre class=\"mermaid\">" in Path(html_file).read_text(encoding="utf-8")
        assert os.path.exists(pdf_file)
        assert os.path.getsize(pdf_file) > 1000
        assert os.path.exists(docx_file)
        assert os.path.getsize(docx_file) > 1000


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
