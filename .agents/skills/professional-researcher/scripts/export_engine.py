"""
Unified Export Engine for Professional Researcher (v2.1).
Parses Markdown (with frontmatter) or JSON and renders publication-grade
PDF documents, Microsoft Word (.docx) documents, and PowerPoint (.pptx) presentations.

v2.1 Upgrades:
- Microsoft PowerPoint (.pptx) Presentation Engine with 16:9 widescreen canvas
- Multilingual & RTL Arabic/Hebrew support in PPTX via OpenXML <a:pPr rtl="1"/>
- Slide catalog: Cover, Agenda, Content, Two-Column, Metrics, Callout, Table, Code, Image, Closing
- Color Themes: Corporate Navy, FinTech Emerald, Modern Slate, Crimson
- Markdown slide delimiters: '---' or '## Heading' with layout inference
- Triple export CLI: --pdf, --docx, and --pptx simultaneously

v2.0 Upgrades:
- Nested bullet support with indent levels
- Image/figure block detection (![alt](path))
- Blockquote vs. callout distinction
- Numbered list false-positive fix
- Rich inline run parser for DOCX (bold/italic/code as Word Runs)
- Table of Contents generation
- Improved error handling

Usage via CLI:
    python export_engine.py --input report.md --pdf report.pdf --docx report.docx --pptx presentation.pptx
    python export_engine.py --input presentation.md --pptx presentation.pptx --theme emerald
"""

import os
import sys
import re
import json
import argparse
import datetime
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure scripts dir is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from pdf_builder import PDFReportBuilder
from docx_builder import DocxReportBuilder
from pptx_builder import PptxReportBuilder
from html_builder import HTMLReportBuilder
from style_wizard import run_intake_wizard, load_style_config


def is_arabic_text(text):
    """Detects presence of Arabic/RTL Unicode characters."""
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', text))


def find_headless_browser():
    """Locates a local headless Chromium binary (Edge or Chrome) for vector diagram PDF rendering."""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None



def parse_frontmatter(content):
    """Extracts YAML frontmatter if present and returns (metadata_dict, remaining_content)."""
    meta = {}
    if content.startswith("---"):
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if match:
            raw_yaml = match.group(1)
            remaining = content[match.end():]
            for line in raw_yaml.split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    meta[key.strip().lower()] = val.strip().strip('"').strip("'")
            return meta, remaining
    return meta, content


def _get_indent_level(line):
    """Returns the indent level of a line based on leading whitespace.
    0 spaces = level 0, 2-4 spaces = level 1, 5+ spaces = level 2."""
    stripped = line.lstrip()
    if not stripped:
        return 0
    indent = len(line) - len(stripped)
    if indent >= 5:
        return 2
    elif indent >= 2:
        return 1
    return 0


def parse_markdown_blocks(text, input_dir=None):
    """
    Parses markdown text into structured semantic blocks:
    - heading: level, text
    - paragraph: text
    - bullet: text, indent (0, 1, 2)
    - callout: type (note, warning, important, tip), title, text
    - blockquote: text (plain > without [!TAG])
    - table: headers (list), rows (list of lists)
    - code: text, language
    - image: path, alt
    - hr: bool
    """
    lines = text.split("\n")
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # 1. Code block
        if line.strip().startswith("```"):
            lang_match = re.match(r"^```(\w+)?", line.strip())
            language = lang_match.group(1) if lang_match and lang_match.group(1) else ""
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({
                "type": "code",
                "text": "\n".join(code_lines),
                "language": language
            })
            i += 1
            continue

        # 2. Callouts & Blockquotes (> [!NOTE], > [!WARNING], etc. OR plain > quote)
        if line.strip().startswith(">"):
            callout_lines = []
            callout_type = None
            callout_title = None

            first_line = line.strip().lstrip(">").strip()
            # Check for GitHub-style alerts: [!NOTE], [!WARNING], [!IMPORTANT], [!TIP], [!CAUTION]
            alert_match = re.match(r"^\[!(NOTE|WARNING|IMPORTANT|TIP|CAUTION)\](?:\s*(.*))?", first_line, re.IGNORECASE)
            if alert_match:
                tag = alert_match.group(1).upper()
                custom_title = alert_match.group(2)
                type_map = {
                    "NOTE": ("note", "NOTE"),
                    "TIP": ("tip", "PRO TIP"),
                    "IMPORTANT": ("important", "CRITICAL NOTICE"),
                    "WARNING": ("warning", "STRATEGIC WARNING"),
                    "CAUTION": ("warning", "CAUTION"),
                }
                callout_type, default_title = type_map.get(tag, ("note", tag))
                callout_title = custom_title if custom_title else default_title
            else:
                # Plain blockquote — not a GitHub alert
                callout_lines.append(first_line)

            i += 1
            while i < n and lines[i].strip().startswith(">"):
                sub_line = lines[i].strip().lstrip(">").strip()
                if sub_line:
                    callout_lines.append(sub_line)
                i += 1

            if callout_type is not None:
                # GitHub-style alert callout
                blocks.append({
                    "type": "callout",
                    "callout_type": callout_type,
                    "title": callout_title,
                    "text": " ".join(callout_lines)
                })
            else:
                # Plain blockquote
                blocks.append({
                    "type": "blockquote",
                    "text": " ".join(callout_lines)
                })
            continue

        # 3. Headings
        heading_match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            blocks.append({
                "type": "heading",
                "level": level,
                "text": heading_text
            })
            i += 1
            continue

        # 4. Horizontal rule
        if re.match(r"^(\-{3,}|\*{3,}|_{3,})$", line.strip()):
            blocks.append({"type": "hr"})
            i += 1
            continue

        # 5. Image/figure: ![alt text](path)
        image_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line.strip())
        if image_match:
            alt_text = image_match.group(1)
            img_path = image_match.group(2)
            # Resolve relative paths against input file directory
            if input_dir and not os.path.isabs(img_path):
                img_path = os.path.join(input_dir, img_path)
            blocks.append({
                "type": "image",
                "alt": alt_text,
                "path": img_path
            })
            i += 1
            continue

        # 6. Markdown table
        if "|" in line and line.strip().startswith("|") and line.strip().endswith("|"):
            table_lines = []
            while i < n and "|" in lines[i] and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            if len(table_lines) >= 2:
                # First line is headers
                headers = [c.strip() for c in table_lines[0].split("|")[1:-1]]
                rows = []
                # Check if second line is separator (e.g. |---|---|)
                start_row = 2 if re.match(r"^\|(\s*:?-+:?\s*\|)+$", table_lines[1]) else 1
                for tl in table_lines[start_row:]:
                    row_cells = [c.strip() for c in tl.split("|")[1:-1]]
                    # Pad or truncate row_cells to match header length
                    while len(row_cells) < len(headers):
                        row_cells.append("")
                    rows.append(row_cells[:len(headers)])

                blocks.append({
                    "type": "table",
                    "headers": headers,
                    "rows": rows
                })
            continue

        # 7. Bullets (- or * or numbered 1.) with indent support
        # Use raw line (not stripped) to detect indent level
        bullet_match = re.match(r"^(\s*)([\*\-]|\d+\.)\s+(.*)$", line)
        if bullet_match:
            indent_str = bullet_match.group(1)
            bullet_text = bullet_match.group(3).strip()
            indent_level = _get_indent_level(line)
            blocks.append({
                "type": "bullet",
                "text": bullet_text,
                "indent": indent_level
            })
            i += 1
            continue

        # 8. Blank lines
        if not line.strip():
            i += 1
            continue

        # 9. Paragraphs (accumulate multi-line paragraphs)
        para_lines = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not lines[i].strip().startswith(("#", ">", "```", "|")) \
                and not re.match(r"^(\s*)([\*\-]|\d+\.)\s+", lines[i]) \
                and not re.match(r"^!\[", lines[i].strip()):
            para_lines.append(lines[i].strip())
            i += 1

        blocks.append({
            "type": "paragraph",
            "text": " ".join(para_lines)
        })

    return blocks


def clean_markdown_inline(text):
    """Converts common inline markdown (bold, italic, code) to clean text or HTML tags for Platypus."""
    # Convert bold **text** to <b>text</b>
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    # Convert italic *text* or _text_ to <i>text</i>
    text = re.sub(r"(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    # Convert `code` to <font name="Courier">\1</font>
    text = re.sub(r"`(.*?)`", r'<font name="Courier">\1</font>', text)
    return text


def clean_markdown_for_docx(text):
    """Strips HTML or markdown tags for pure text rendering in DOCX."""
    # Remove bold/italic tags
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"<[^<]+?>", "", text)
    return text


def parse_inline_runs(text):
    """Parses inline markdown into a list of run descriptors for rich DOCX rendering.

    Returns a list of dicts: {"text": str, "bold": bool, "italic": bool, "code": bool}
    Handles **bold**, *italic*, and `code` patterns without stripping them.
    """
    runs = []
    # Tokenize: split on bold, italic, and code markers
    pattern = re.compile(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)')
    parts = pattern.split(text)

    for part in parts:
        if not part:
            continue

        if part.startswith("**") and part.endswith("**"):
            inner = part[2:-2]
            if inner:
                runs.append({"text": inner, "bold": True, "italic": False, "code": False})
        elif part.startswith("*") and part.endswith("*") and not part.startswith("**"):
            inner = part[1:-1]
            if inner:
                runs.append({"text": inner, "bold": False, "italic": True, "code": False})
        elif part.startswith("`") and part.endswith("`"):
            inner = part[1:-1]
            if inner:
                runs.append({"text": inner, "bold": False, "italic": False, "code": True})
        else:
            if part:
                runs.append({"text": part, "bold": False, "italic": False, "code": False})

    return runs if runs else [{"text": text, "bold": False, "italic": False, "code": False}]


def parse_metrics_bullets(blocks):
    """
    Attempts to extract metric items from blocks.
    Looks for bullets with pattern: **<value>** <label> [| <sub>] or **<value>**: <label>
    Returns list of dicts: [{"value": ..., "label": ..., "sub": ...}]
    """
    metrics = []
    metric_pat = re.compile(r'^\*\*([^*]+)\*\*\s*(?::\s*|\s*\|\s*|\s+)(.*)$')
    for b in blocks:
        if b.get("type") == "bullet":
            text = b.get("text", "").strip()
            m = metric_pat.match(text)
            if m:
                val = m.group(1).strip()
                rest = m.group(2).strip()
                sub = ""
                if "|" in rest:
                    parts = rest.split("|", 1)
                    label = parts[0].strip()
                    sub = parts[1].strip()
                else:
                    label = rest
                metrics.append({"value": val, "label": label, "sub": sub})
    return metrics


def parse_two_column_blocks(blocks):
    """
    Extracts two columns from blocks if level-3 headings (###) are used as column delimiters.
    Returns (col1_title, col1_blocks, col2_title, col2_blocks) or None.
    """
    h3_indices = [idx for idx, b in enumerate(blocks) if b.get("type") == "heading" and b.get("level") == 3]
    if len(h3_indices) == 2:
        idx1, idx2 = h3_indices
        col1_title = blocks[idx1]["text"]
        col1_blocks = blocks[idx1 + 1:idx2]
        col2_title = blocks[idx2]["text"]
        col2_blocks = blocks[idx2 + 1:]
        return col1_title, col1_blocks, col2_title, col2_blocks
    return None


def parse_presentation_slides(text, input_dir=None):
    """
    Parses markdown text into individual presentation slide specifications:
    [
        {
            "title": str,
            "category": str or None,
            "layout": str ("content", "agenda", "two-column", "metrics", "callout", "table", "code", "image", "closing"),
            "blocks": list of AST blocks,
            "metrics": list of dicts (if layout == "metrics"),
            "col1_title": str, "col1_blocks": list, "col2_title": str, "col2_blocks": list (if two-column),
            "callout_type": str, "callout_title": str, "callout_text": str, "bullets": list,
            "table_headers": list, "table_rows": list,
            "code_text": str, "code_lang": str,
            "image_path": str, "image_caption": str
        }
    ]
    """
    # Split slides by horizontal rule (--- or *** or ___)
    if re.search(r'\n(?:\s*---+\s*|\s*___+\s*|\s*\*\*\*+\s*)\n', text):
        raw_chunks = re.split(r'\n(?:\s*---+\s*|\s*___+\s*|\s*\*\*\*+\s*)\n', text.strip())
    else:
        # Split by ## Heading 2
        raw_chunks = re.split(r'(?m)^(?=##\s+)', text.strip())

    slides = []

    for chunk in raw_chunks:
        c_clean = chunk.strip()
        if not c_clean:
            continue

        # Extract layout directive: <!-- layout: (\w+) -->
        layout_match = re.search(r'<!--\s*layout:\s*([a-zA-Z0-9_-]+)\s*-->', c_clean, re.IGNORECASE)
        explicit_layout = layout_match.group(1).lower() if layout_match else None

        # Extract category directive: <!-- category: (.*?) -->
        cat_match = re.search(r'<!--\s*category:\s*(.*?)\s*-->', c_clean, re.IGNORECASE)
        category = cat_match.group(1).strip() if cat_match else None

        # Strip html comment directives from content before parsing
        clean_text = re.sub(r'<!--.*?-->', '', c_clean).strip()
        blocks = parse_markdown_blocks(clean_text, input_dir=input_dir)
        if not blocks:
            continue

        # Extract slide title from the first heading or first paragraph
        title = ""
        content_blocks = []
        for b in blocks:
            if not title and b.get("type") == "heading":
                title = b.get("text", "")
            else:
                content_blocks.append(b)

        if not title:
            if content_blocks and content_blocks[0].get("type") == "paragraph":
                title = content_blocks[0].get("text", "")
                content_blocks = content_blocks[1:]
            else:
                title = "Executive Summary"

        slide_spec = {
            "title": title,
            "category": category,
            "blocks": content_blocks,
            "layout": explicit_layout or "content"
        }

        # Auto-detect layout if not explicitly set
        if not explicit_layout:
            title_lower = title.lower()
            if any(k in title_lower for k in ["conclusion", "summary & next steps", "q&a", "خاتمة", "التوصيات", "الخطوات القادمة"]):
                slide_spec["layout"] = "closing"
            elif any(k in title_lower for k in ["agenda", "table of contents", "جدول الأعمال", "فهرس"]):
                slide_spec["layout"] = "agenda"
                slide_spec["items"] = [b.get("text", "") for b in content_blocks if b.get("type") == "bullet"]
            else:
                two_cols = parse_two_column_blocks(content_blocks)
                if two_cols:
                    slide_spec["layout"] = "two-column"
                    slide_spec["col1_title"], slide_spec["col1_blocks"], slide_spec["col2_title"], slide_spec["col2_blocks"] = two_cols
                else:
                    metrics = parse_metrics_bullets(content_blocks)
                    if len(metrics) >= 2 and len(metrics) == len([b for b in content_blocks if b.get("type") == "bullet"]):
                        slide_spec["layout"] = "metrics"
                        slide_spec["metrics"] = metrics
                    elif len(content_blocks) == 1 and content_blocks[0].get("type") == "table":
                        slide_spec["layout"] = "table"
                        slide_spec["table_headers"] = content_blocks[0]["headers"]
                        slide_spec["table_rows"] = content_blocks[0]["rows"]
                    elif len(content_blocks) == 1 and content_blocks[0].get("type") == "code":
                        slide_spec["layout"] = "code"
                        slide_spec["code_text"] = content_blocks[0]["text"]
                        slide_spec["code_lang"] = content_blocks[0].get("language", "")
                    elif len(content_blocks) == 1 and content_blocks[0].get("type") == "image":
                        slide_spec["layout"] = "image"
                        slide_spec["image_path"] = content_blocks[0]["path"]
                        slide_spec["image_caption"] = content_blocks[0].get("alt", "")
                    elif len(content_blocks) == 1 and content_blocks[0].get("type") == "callout":
                        slide_spec["layout"] = "callout"
                        c_blk = content_blocks[0]
                        slide_spec["callout_type"] = c_blk.get("callout_type", "note")
                        slide_spec["callout_title"] = c_blk.get("title", "")
                        slide_spec["callout_text"] = c_blk.get("text", "")
        else:
            if explicit_layout == "two-column":
                two_cols = parse_two_column_blocks(content_blocks)
                if two_cols:
                    slide_spec["col1_title"], slide_spec["col1_blocks"], slide_spec["col2_title"], slide_spec["col2_blocks"] = two_cols
                else:
                    half = len(content_blocks) // 2
                    slide_spec["col1_title"] = "Overview"
                    slide_spec["col1_blocks"] = content_blocks[:half]
                    slide_spec["col2_title"] = "Analysis"
                    slide_spec["col2_blocks"] = content_blocks[half:]
            elif explicit_layout == "metrics":
                slide_spec["metrics"] = parse_metrics_bullets(content_blocks)
            elif explicit_layout == "agenda":
                slide_spec["items"] = [b.get("text", "") for b in content_blocks if b.get("type") == "bullet"]
            elif explicit_layout == "callout":
                slide_bullets = []
                for b in content_blocks:
                    if b.get("type") == "callout":
                        slide_spec["callout_type"] = b.get("callout_type", "note")
                        slide_spec["callout_title"] = b.get("title", "")
                        slide_spec["callout_text"] = b.get("text", "")
                    elif b.get("type") == "blockquote":
                        slide_spec["callout_type"] = "note"
                        slide_spec["callout_title"] = "KEY INSIGHT"
                        slide_spec["callout_text"] = b.get("text", "")
                    elif b.get("type") == "paragraph" and not slide_spec.get("callout_text"):
                        slide_spec["callout_text"] = b.get("text", "")
                    elif b.get("type") == "bullet":
                        slide_bullets.append(b.get("text", ""))
                if slide_bullets:
                    slide_spec["bullets"] = slide_bullets
            elif explicit_layout == "table":
                for b in content_blocks:
                    if b.get("type") == "table":
                        slide_spec["table_headers"] = b["headers"]
                        slide_spec["table_rows"] = b["rows"]
                        break
            elif explicit_layout == "code":
                for b in content_blocks:
                    if b.get("type") == "code":
                        slide_spec["code_text"] = b["text"]
                        slide_spec["code_lang"] = b.get("language", "")
                        break
            elif explicit_layout in ["showcase", "app-showcase", "mobile-showcase"]:
                slide_spec["layout"] = "app-showcase"
                specs = []
                for b in content_blocks:
                    if b.get("type") == "image":
                        slide_spec["image_path"] = b["path"]
                        slide_spec["image_caption"] = b.get("alt", "")
                    else:
                        specs.append(b)
                slide_spec["specs"] = specs
            elif explicit_layout == "image":
                for b in content_blocks:
                    if b.get("type") == "image":
                        slide_spec["image_path"] = b["path"]
                        slide_spec["image_caption"] = b.get("alt", "")
                        break
            elif explicit_layout in ["versus", "comparison"]:
                two_cols = parse_two_column_blocks(content_blocks)
                if two_cols:
                    slide_spec["col1_title"], slide_spec["col1_blocks"], slide_spec["col2_title"], slide_spec["col2_blocks"] = two_cols
                else:
                    half = len(content_blocks) // 2
                    slide_spec["col1_title"] = "Status Quo"
                    slide_spec["col1_blocks"] = content_blocks[:half]
                    slide_spec["col2_title"] = "Innovation"
                    slide_spec["col2_blocks"] = content_blocks[half:]
            elif explicit_layout == "split-hero":
                hero_title = "Strategic Direction"
                hero_text = ""
                items = []
                for b in content_blocks:
                    if b.get("type") == "heading" and b.get("level") == 3 and not hero_text:
                        hero_title = b.get("text", "")
                    elif b.get("type") in ["paragraph", "blockquote"] and not hero_text:
                        hero_text = b.get("text", "")
                    elif b.get("type") == "bullet":
                        items.append(b.get("text", ""))
                slide_spec["hero_title"] = hero_title
                slide_spec["hero_text"] = hero_text
                slide_spec["items"] = items
            elif explicit_layout in ["timeline", "process", "roadmap"]:
                steps = []
                cur_step = None
                for b in content_blocks:
                    if b.get("type") == "heading" and b.get("level") == 3:
                        if cur_step:
                            steps.append(cur_step)
                        cur_step = {"title": b["text"], "phase": f"W0{len(steps)+1}", "bullets": []}
                    elif b.get("type") == "bullet":
                        raw = b.get("text", "")
                        m = re.match(r'^\*\*([^*:]+)(?::\s*([^*]+))?\*\*(?::\s*(.*))?', raw)
                        if m and not cur_step:
                            p_tag = m.group(1).strip()
                            t_txt = m.group(2).strip() if m.group(2) else p_tag
                            d_txt = m.group(3).strip() if m.group(3) else ""
                            steps.append({"phase": p_tag, "title": t_txt, "desc": d_txt, "bullets": [d_txt] if d_txt else []})
                        elif cur_step:
                            cur_step["bullets"].append(raw)
                        else:
                            steps.append({"title": raw, "phase": f"0{len(steps)+1}", "bullets": []})
                    elif b.get("type") == "paragraph" and cur_step:
                        cur_step["bullets"].append(b["text"])
                if cur_step:
                    steps.append(cur_step)
                slide_spec["steps"] = steps
            elif explicit_layout in ["grid", "matrix", "quadrant"]:
                cards = []
                cur_card = None
                for b in content_blocks:
                    if b.get("type") == "heading" and b.get("level") == 3:
                        if cur_card:
                            cards.append(cur_card)
                        cur_card = {"title": b["text"], "badge": f"0{len(cards)+1}", "desc": ""}
                    elif b.get("type") in ["bullet", "paragraph"]:
                        raw = b.get("text", "")
                        if cur_card:
                            cur_card["desc"] = (cur_card["desc"] + " • " + raw).strip(" •")
                        else:
                            cards.append({"title": raw[:30], "desc": raw, "badge": f"0{len(cards)+1}"})
                if cur_card:
                    cards.append(cur_card)
                slide_spec["cards"] = cards
            elif explicit_layout in ["architecture", "stack", "layers"]:
                layers = []
                cur_layer = None
                for b in content_blocks:
                    if b.get("type") == "heading" and b.get("level") == 3:
                        if cur_layer:
                            layers.append(cur_layer)
                        cur_layer = {"tag": f"TIER 0{len(layers)+1}", "title": b["text"], "desc": ""}
                    elif b.get("type") in ["bullet", "paragraph"]:
                        raw = b.get("text", "")
                        if cur_layer:
                            cur_layer["desc"] = (cur_layer["desc"] + " | " + raw).strip(" |")
                        else:
                            layers.append({"tag": f"TIER 0{len(layers)+1}", "title": raw[:35], "desc": raw})
                if cur_layer:
                    layers.append(cur_layer)
                slide_spec["layers"] = layers

        slides.append(slide_spec)

    return slides


class DocumentExporter:
    """Unified exporter orchestrating PDF, Word (.docx), and PowerPoint (.pptx) builds."""

    def __init__(self, title, subtitle="", author="", organization="", date_str="",
                 theme="navy", style=None, logo_path=None, input_dir=None):
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.organization = organization
        self.date_str = date_str or datetime.date.today().strftime("%B %d, %Y")
        self.theme = theme or "navy"
        self.style = style or {}
        self.logo_path = logo_path or self.style.get("logo_path")
        self.input_dir = input_dir or os.getcwd()

    def export(self, blocks, html_path=None, pdf_path=None, docx_path=None, pptx_path=None, slides=None):
        results = {}

        # Detect RTL
        is_rtl = is_arabic_text(self.title) or is_arabic_text(self.subtitle)
        if not is_rtl:
            for blk in blocks[:15]:
                if is_arabic_text(blk.get("text", "")) or is_arabic_text(blk.get("title", "")):
                    is_rtl = True
                    break

        # Check for Mermaid architectural diagrams and find browser
        has_mermaid = any(blk.get("type") == "code" and blk.get("language", "").strip().lower() == "mermaid" for blk in blocks)
        browser_exe = find_headless_browser()
        effective_html_path = html_path
        temp_html_created = False

        # Build HTML if requested OR needed for headless browser PDF (vector diagrams or web printing)
        if html_path or (pdf_path and (has_mermaid or is_rtl) and browser_exe):
            if not effective_html_path:
                base_name, _ = os.path.splitext(pdf_path)
                effective_html_path = f"{base_name}_temp.html"
                temp_html_created = True

            html_builder = HTMLReportBuilder(
                title=self.title,
                subtitle=self.subtitle,
                author=self.author,
                organization=self.organization,
                date_str=self.date_str,
                is_rtl=is_rtl
            )

            for blk in blocks:
                b_type = blk["type"]
                if b_type == "heading":
                    if blk["level"] == 1 and blk["text"].strip().lower() == self.title.strip().lower():
                        continue
                    html_builder.add_heading(blk["text"], level=blk["level"])
                elif b_type == "paragraph":
                    html_builder.add_paragraph(blk["text"])
                elif b_type == "bullet":
                    html_builder.add_bullet(blk["text"], indent=blk.get("indent", 0))
                elif b_type == "callout":
                    html_builder.add_callout(
                        text=blk["text"],
                        title=blk.get("title", "KEY INSIGHT"),
                        callout_type=blk.get("callout_type", "note")
                    )
                elif b_type == "blockquote":
                    html_builder.add_blockquote(blk["text"])
                elif b_type == "table":
                    html_builder.add_table(blk["headers"], blk["rows"])
                elif b_type == "code":
                    html_builder.add_code_block(blk["text"], language=blk.get("language", ""))
                elif b_type == "image":
                    html_builder.add_image(blk["path"], blk.get("alt", ""))
                elif b_type == "hr":
                    html_builder.add_hr()

            with open(effective_html_path, "w", encoding="utf-8") as hf:
                hf.write(html_builder.render())

            if html_path:
                results["html"] = html_path

        # 1. Export PDF
        if pdf_path:
            pdf_rendered = False
            # Prefer headless Chromium for documents with Mermaid vector diagrams or rich web rendering
            if (has_mermaid or is_rtl) and browser_exe and effective_html_path and os.path.exists(effective_html_path):
                try:
                    abs_html = os.path.abspath(effective_html_path).replace("\\", "/")
                    abs_pdf = os.path.abspath(pdf_path)
                    cmd = [
                        browser_exe,
                        "--headless=new",
                        "--disable-gpu",
                        "--no-pdf-header-footer",
                        "--run-all-compositor-stages-before-draw",
                        "--virtual-time-budget=6000",
                        f"--print-to-pdf={abs_pdf}",
                        f"file:///{abs_html}"
                    ]
                    res = subprocess.run(cmd, capture_output=True, timeout=35)
                    if res.returncode == 0 and os.path.exists(abs_pdf) and os.path.getsize(abs_pdf) > 1000:
                        results["pdf"] = pdf_path
                        pdf_rendered = True
                except Exception as e:
                    print(f"  [WARN] Headless browser PDF failed ({e}), falling back to ReportLab...", file=sys.stderr)

            if not pdf_rendered:
                try:
                    pdf_builder = PDFReportBuilder(
                        filename=pdf_path,
                        title=self.title,
                        subtitle=self.subtitle,
                        author=self.author,
                        organization=self.organization,
                        date_str=self.date_str,
                        style=self.style,
                        logo_path=self.logo_path
                    )
                    pdf_builder.build_cover_page()
                    pdf_builder.add_table_of_contents(blocks, self.title)

                    for blk in blocks:
                        b_type = blk["type"]
                        if b_type == "heading":
                            if blk["level"] == 1 and blk["text"].strip().lower() == self.title.strip().lower():
                                continue
                            pdf_builder.add_heading(blk["text"], level=blk["level"])
                        elif b_type == "paragraph":
                            pdf_builder.add_paragraph(clean_markdown_inline(blk["text"]))
                        elif b_type == "bullet":
                            pdf_builder.add_bullet(
                                clean_markdown_inline(blk["text"]),
                                indent=blk.get("indent", 0)
                            )
                        elif b_type == "callout":
                            pdf_builder.add_callout(
                                text=clean_markdown_inline(blk["text"]),
                                title=blk.get("title", "KEY INSIGHT"),
                                callout_type=blk.get("callout_type", "note")
                            )
                        elif b_type == "blockquote":
                            pdf_builder.add_blockquote(clean_markdown_inline(blk["text"]))
                        elif b_type == "table":
                            pdf_builder.add_table(blk["headers"], blk["rows"])
                        elif b_type == "code":
                            pdf_builder.add_code_block(blk["text"])
                        elif b_type == "image":
                            pdf_builder.add_image(blk["path"], blk.get("alt", ""))
                        elif b_type == "hr":
                            pdf_builder.add_horizontal_rule()

                    pdf_builder.save()
                    results["pdf"] = pdf_path
                except Exception as e:
                    print(f"  [ERROR] PDF generation failed: {e}", file=sys.stderr)
                    raise

            # Cleanup temp html if only created for PDF
            if temp_html_created and os.path.exists(effective_html_path):
                try:
                    os.remove(effective_html_path)
                except Exception:
                    pass

        # 2. Export Word (.docx)
        if docx_path:
            try:
                docx_builder = DocxReportBuilder(
                    filename=docx_path,
                    title=self.title,
                    subtitle=self.subtitle,
                    author=self.author,
                    organization=self.organization,
                    date_str=self.date_str,
                    style=self.style,
                    logo_path=self.logo_path
                )
                docx_builder.build_cover_page()
                docx_builder.add_table_of_contents(blocks, self.title)

                for blk in blocks:
                    b_type = blk["type"]
                    if b_type == "heading":
                        if blk["level"] == 1 and blk["text"].strip().lower() == self.title.strip().lower():
                            continue
                        docx_builder.add_heading(clean_markdown_for_docx(blk["text"]), level=blk["level"])
                    elif b_type == "paragraph":
                        docx_builder.add_rich_paragraph(parse_inline_runs(blk["text"]))
                    elif b_type == "bullet":
                        docx_builder.add_rich_bullet(
                            parse_inline_runs(blk["text"]),
                            indent=blk.get("indent", 0)
                        )
                    elif b_type == "callout":
                        docx_builder.add_callout(
                            text=clean_markdown_for_docx(blk["text"]),
                            title=blk.get("title", "KEY INSIGHT"),
                            callout_type=blk.get("callout_type", "note")
                        )
                    elif b_type == "blockquote":
                        docx_builder.add_blockquote(clean_markdown_for_docx(blk["text"]))
                    elif b_type == "table":
                        clean_rows = [[clean_markdown_for_docx(str(cell)) for cell in r] for r in blk["rows"]]
                        clean_headers = [clean_markdown_for_docx(h) for h in blk["headers"]]
                        docx_builder.add_table(clean_headers, clean_rows)
                    elif b_type == "code":
                        lang = blk.get("language", "").strip().lower()
                        if lang == "mermaid":
                            docx_builder.add_mermaid_block(blk["text"])
                        else:
                            docx_builder.add_code_block(blk["text"])
                    elif b_type == "image":
                        docx_builder.add_image(blk["path"], blk.get("alt", ""))

                docx_builder.save()
                results["docx"] = docx_path
            except Exception as e:
                print(f"  [ERROR] DOCX generation failed: {e}", file=sys.stderr)
                raise

        # 3. Export PowerPoint (.pptx)
        if pptx_path:
            try:
                pptx_builder = PptxReportBuilder(
                    filename=pptx_path,
                    title=self.title,
                    subtitle=self.subtitle,
                    author=self.author,
                    organization=self.organization,
                    date_str=self.date_str,
                    theme=self.theme,
                    style=self.style,
                    logo_path=self.logo_path,
                    archetype=self.style.get("archetype", "consulting_grid")
                )

                # Add Cover Slide
                pptx_builder.add_title_slide()

                presentation_slides = slides if slides is not None else []
                has_closing = False

                for s in presentation_slides:
                    s_layout = s.get("layout", "content")
                    s_title = s.get("title", "")
                    s_cat = s.get("category")

                    if s_layout == "agenda":
                        pptx_builder.add_agenda_slide(
                            title=s_title,
                            items=s.get("items", []),
                            category=s_cat or "AGENDA"
                        )
                    elif s_layout in ["versus", "comparison"]:
                        pptx_builder.add_versus_slide(
                            title=s_title,
                            col1_title=s.get("col1_title", "Perspective A"),
                            col1_blocks=s.get("col1_blocks", []),
                            col2_title=s.get("col2_title", "Perspective B"),
                            col2_blocks=s.get("col2_blocks", []),
                            category=s_cat
                        )
                    elif s_layout == "split-hero":
                        pptx_builder.add_split_hero_slide(
                            title=s_title,
                            hero_title=s.get("hero_title", "Key Strategic Vision"),
                            hero_text=s.get("hero_text", ""),
                            items=s.get("items", []),
                            category=s_cat
                        )
                    elif s_layout in ["timeline", "process", "roadmap"]:
                        pptx_builder.add_timeline_slide(
                            title=s_title,
                            steps=s.get("steps", []),
                            category=s_cat
                        )
                    elif s_layout in ["grid", "matrix", "quadrant"]:
                        pptx_builder.add_grid_slide(
                            title=s_title,
                            cards=s.get("cards", []),
                            category=s_cat
                        )
                    elif s_layout in ["architecture", "stack", "layers"]:
                        pptx_builder.add_architecture_slide(
                            title=s_title,
                            layers=s.get("layers", []),
                            category=s_cat
                        )
                    elif s_layout == "two-column":
                        pptx_builder.add_two_column_slide(
                            title=s_title,
                            col1_title=s.get("col1_title", "Perspective A"),
                            col1_blocks=s.get("col1_blocks", []),
                            col2_title=s.get("col2_title", "Perspective B"),
                            col2_blocks=s.get("col2_blocks", []),
                            category=s_cat
                        )
                    elif s_layout == "metrics":
                        pptx_builder.add_metrics_slide(
                            title=s_title,
                            metrics=s.get("metrics", []),
                            category=s_cat
                        )
                    elif s_layout == "callout":
                        pptx_builder.add_callout_slide(
                            title=s_title,
                            callout_type=s.get("callout_type", "note"),
                            callout_title=s.get("callout_title"),
                            text=s.get("callout_text", ""),
                            bullets=s.get("bullets", []),
                            category=s_cat
                        )
                    elif s_layout == "table":
                        pptx_builder.add_table_slide(
                            title=s_title,
                            headers=s.get("table_headers", []),
                            rows=s.get("table_rows", []),
                            category=s_cat
                        )
                    elif s_layout == "code":
                        pptx_builder.add_code_slide(
                            title=s_title,
                            code_text=s.get("code_text", ""),
                            language=s.get("code_lang"),
                            category=s_cat
                        )
                    elif s_layout in ["showcase", "app-showcase", "mobile-showcase"]:
                        pptx_builder.add_app_showcase_slide(
                            title=s_title,
                            image_path=s.get("image_path", ""),
                            specs=s.get("specs", []) or s.get("blocks", []),
                            category=s_cat
                        )
                    elif s_layout == "image":
                        pptx_builder.add_image_slide(
                            title=s_title,
                            image_path=s.get("image_path", ""),
                            caption=s.get("image_caption"),
                            category=s_cat
                        )
                    elif s_layout == "closing":
                        has_closing = True
                        pptx_builder.add_closing_slide(
                            title=s_title,
                            subtitle=s.get("subtitle") or self.subtitle,
                            contact_info=s.get("contact") or (f"{self.author} • {self.organization}" if self.author or self.organization else None)
                        )
                    else:
                        pptx_builder.add_content_slide(
                            title=s_title,
                            blocks=s.get("blocks", []),
                            category=s_cat
                        )

                # Add closing slide if not explicitly defined
                if not has_closing:
                    pptx_builder.add_closing_slide(
                        title="Strategic Summary & Recommendations",
                        subtitle=self.subtitle,
                        contact_info=f"{self.author} • {self.organization}" if self.author or self.organization else None
                    )

                pptx_builder.save()
                results["pptx"] = pptx_path
            except Exception as e:
                print(f"  [ERROR] PPTX generation failed: {e}", file=sys.stderr)
                raise

        return results


def convert_file(input_path, html_path=None, pdf_path=None, docx_path=None, pptx_path=None,
                 title=None, author=None, org=None, date_str=None, theme=None,
                 style=None, logo_path=None, primary_color=None, accent_color=None,
                 archetype=None, style_prompt=None):
    """Converts a Markdown or JSON file to HTML, PDF, DOCX, and/or PPTX with custom styling and branding."""
    with open(input_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    input_dir = os.path.dirname(os.path.abspath(input_path))
    meta = {}
    blocks = []
    slides = []

    if input_path.endswith(".json"):
        data = json.loads(raw_content)
        meta = data.get("metadata", {})
        blocks = data.get("blocks", [])
        slides = data.get("slides", [])
    else:
        # Markdown
        meta, md_text = parse_frontmatter(raw_content)
        blocks = parse_markdown_blocks(md_text, input_dir=input_dir)
        slides = parse_presentation_slides(md_text, input_dir=input_dir)

    doc_title = title or meta.get("title") or "Executive Research Report"
    doc_subtitle = meta.get("subtitle", "")
    doc_author = author or meta.get("author", "Principal Research Analyst")
    doc_org = org or meta.get("organization") or meta.get("org", "TeknoKeys Strategic Research")
    doc_date = date_str or meta.get("date", datetime.date.today().strftime("%B %d, %Y"))
    doc_theme = theme or meta.get("theme", "navy")

    # Load and merge style configuration
    loaded_style = load_style_config(style) if style else {}
    branding_meta = meta.get("branding", {})
    if isinstance(branding_meta, dict):
        for k, v in branding_meta.items():
            if k not in loaded_style:
                loaded_style[k] = v

    # Resolve Archetype and custom prompt
    active_prompt = style_prompt or loaded_style.get("style_prompt") or meta.get("style_prompt")
    if active_prompt:
        try:
            from .style_wizard import parse_style_prompt
        except ImportError:
            from style_wizard import parse_style_prompt
        parsed_p = parse_style_prompt(active_prompt)
        if not archetype:
            archetype = parsed_p.get("archetype")
        if not primary_color and parsed_p.get("primary"):
            primary_color = parsed_p.get("primary")
        if not accent_color and parsed_p.get("accent"):
            accent_color = parsed_p.get("accent")

    active_archetype = (archetype or loaded_style.get("archetype") or meta.get("archetype") or
                        meta.get("presentation_style") or meta.get("style_archetype") or "consulting_grid")
    active_archetype = active_archetype.lower().replace("-", "_")
    loaded_style["archetype"] = active_archetype
    loaded_style["style_archetype"] = active_archetype

    # Logo resolution
    resolved_logo = logo_path or loaded_style.get("logo_path") or loaded_style.get("logo") or meta.get("logo")
    if resolved_logo and input_dir and not os.path.isabs(resolved_logo) and not os.path.exists(resolved_logo):
        candidate = os.path.join(input_dir, resolved_logo)
        if os.path.exists(candidate):
            resolved_logo = candidate
    loaded_style["logo_path"] = resolved_logo

    # Synthesize 100% harmonized palette via color_synthesizer (archetype-aware)
    try:
        from .color_synthesizer import synthesize_palette
    except ImportError:
        from color_synthesizer import synthesize_palette

    if resolved_logo and os.path.exists(resolved_logo):
        # Allow logo to drive brand primary and accent colors directly
        p_in = primary_color
        a_in = accent_color
    else:
        p_in = primary_color or loaded_style.get("primary_color") or loaded_style.get("primary")
        a_in = accent_color or loaded_style.get("accent_color") or loaded_style.get("accent")

    synthesized = synthesize_palette(
        logo_path=resolved_logo,
        primary_hex=p_in,
        accent_hex=a_in,
        theme_preset=doc_theme,
        archetype=active_archetype
    )

    for k, v in synthesized.items():
        if k.endswith("_hex"):
            loaded_style[k] = v
    loaded_style["primary"] = synthesized["primary_hex"]
    loaded_style["primary_color"] = synthesized["primary_hex"]
    loaded_style["accent"] = synthesized["accent_hex"]
    loaded_style["accent_color"] = synthesized["accent_hex"]
    loaded_style["secondary"] = synthesized["secondary_hex"]
    loaded_style["bg_light"] = synthesized["bg_light_hex"]
    loaded_style["card_border"] = synthesized["card_border_hex"]
    loaded_style["body"] = synthesized["body_hex"]
    loaded_style["muted"] = synthesized["muted_hex"]
    loaded_style["logo_path"] = resolved_logo

    exporter = DocumentExporter(
        title=doc_title,
        subtitle=doc_subtitle,
        author=doc_author,
        organization=doc_org,
        date_str=doc_date,
        theme=doc_theme,
        style=loaded_style,
        logo_path=resolved_logo,
        input_dir=input_dir
    )

    base_name, _ = os.path.splitext(input_path)
    is_presentation_type = (
        meta.get("type") in ["presentation", "slides", "deck"] or
        input_path.endswith((".presentation.md", ".slides.md", ".deck.md"))
    )

    # Derive default output paths if none provided
    if not html_path and not pdf_path and not docx_path and not pptx_path:
        if is_presentation_type:
            pptx_path = f"{base_name}.pptx"
        else:
            pdf_path = f"{base_name}.pdf"
            docx_path = f"{base_name}.docx"

    return exporter.export(blocks, html_path=html_path, pdf_path=pdf_path, docx_path=docx_path, pptx_path=pptx_path, slides=slides)


def main():
    parser = argparse.ArgumentParser(description="Professional Research Exporter v3.0 (HTML, PDF, DOCX & PPTX)")
    parser.add_argument("--input", "-i", required=True, help="Input Markdown (.md) or JSON (.json) file")
    parser.add_argument("--html", help="Output standalone HTML file path (with interactive Mermaid diagrams)")
    parser.add_argument("--pdf", "-p", help="Output PDF file path")
    parser.add_argument("--docx", "-d", help="Output Microsoft Word (.docx) file path")
    parser.add_argument("--pptx", "-x", help="Output Microsoft PowerPoint (.pptx) presentation file path")
    parser.add_argument("--theme", choices=["navy", "emerald", "slate", "crimson"], default=None, help="Preset color theme")
    parser.add_argument("--archetype", choices=["consulting_grid", "modern_dark", "minimal_editorial", "warm_organic", "vibrant_bold"], default=None, help="Structural design archetype for presentation slides")
    parser.add_argument("--style-prompt", help="Natural language description of presentation style (e.g. 'dark cyber tech with neon cyan')")
    parser.add_argument("--domain", help="Target research domain for domain-adaptive design synthesis")
    parser.add_argument("--logo", "-l", help="Path to company or brand logo file (.png, .jpg, .svg)")
    parser.add_argument("--style", "-s", help="Path to style_config.json or inline JSON")
    parser.add_argument("--primary-color", help="Custom primary dark hex color (e.g. #0F172A)")
    parser.add_argument("--accent-color", help="Custom accent vibrant hex color (e.g. #2563EB)")
    parser.add_argument("--wizard", "--interactive", action="store_true", help="Launch interactive style & branding questionnaire")
    parser.add_argument("--title", "-t", help="Override document title")
    parser.add_argument("--author", "-a", help="Override author name")
    parser.add_argument("--org", "-o", help="Override organization")
    parser.add_argument("--date", help="Override report date")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    style_cfg = {}
    if args.wizard:
        style_cfg = run_intake_wizard()
    elif args.style:
        style_cfg = load_style_config(args.style)

    if args.archetype:
        style_cfg["archetype"] = args.archetype
    if args.style_prompt:
        style_cfg["style_prompt"] = args.style_prompt
    if args.domain:
        style_cfg["domain"] = args.domain

    print(f"[+] Processing input: {args.input}")
    res = convert_file(
        input_path=args.input,
        html_path=args.html,
        pdf_path=args.pdf,
        docx_path=args.docx,
        pptx_path=args.pptx,
        title=args.title,
        author=args.author,
        org=args.org,
        date_str=args.date,
        theme=args.theme,
        style=style_cfg,
        logo_path=args.logo,
        primary_color=args.primary_color,
        accent_color=args.accent_color,
        archetype=args.archetype,
        style_prompt=args.style_prompt
    )

    for fmt, path in res.items():
        size_kb = os.path.getsize(path) / 1024
        print(f"  -> Generated {fmt.upper()}: {path} ({size_kb:.1f} KB)")
    print("[✓] Export completed successfully.")


if __name__ == "__main__":
    main()
