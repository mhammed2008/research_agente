"""
Unified Export Engine for Professional Researcher (v2.0).
Parses Markdown (with frontmatter) or JSON and renders both publication-grade
PDF and Microsoft Word (.docx) documents.

v2.0 Upgrades:
- Nested bullet support with indent levels
- Image/figure block detection (![alt](path))
- Blockquote vs. callout distinction
- Numbered list false-positive fix
- Rich inline run parser for DOCX (bold/italic/code as Word Runs)
- Table of Contents generation
- Improved error handling

Usage via CLI:
    python export_engine.py --input report.md --pdf report.pdf --docx report.docx
    python export_engine.py --input report.json --pdf report.pdf --docx report.docx
"""

import os
import sys
import re
import json
import argparse
import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure scripts dir is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from pdf_builder import PDFReportBuilder
from docx_builder import DocxReportBuilder


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
    # Pattern matches **bold**, *italic*, or `code` segments
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


class DocumentExporter:
    def __init__(self, title, subtitle="", author="", organization="", date_str="", input_dir=None):
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.organization = organization
        self.date_str = date_str or datetime.date.today().strftime("%B %d, %Y")
        self.input_dir = input_dir or os.getcwd()

    def export(self, blocks, pdf_path=None, docx_path=None):
        results = {}

        # 1. Export PDF
        if pdf_path:
            try:
                pdf_builder = PDFReportBuilder(
                    filename=pdf_path,
                    title=self.title,
                    subtitle=self.subtitle,
                    author=self.author,
                    organization=self.organization,
                    date_str=self.date_str
                )
                pdf_builder.build_cover_page()
                pdf_builder.add_table_of_contents(blocks, self.title)

                for blk in blocks:
                    b_type = blk["type"]
                    if b_type == "heading":
                        # Suppress duplicate top-level title if it matches cover
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

        # 2. Export Word (.docx)
        if docx_path:
            try:
                docx_builder = DocxReportBuilder(
                    filename=docx_path,
                    title=self.title,
                    subtitle=self.subtitle,
                    author=self.author,
                    organization=self.organization,
                    date_str=self.date_str
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
                        # Clean each cell
                        clean_rows = [[clean_markdown_for_docx(str(cell)) for cell in r] for r in blk["rows"]]
                        clean_headers = [clean_markdown_for_docx(h) for h in blk["headers"]]
                        docx_builder.add_table(clean_headers, clean_rows)
                    elif b_type == "code":
                        docx_builder.add_code_block(blk["text"])
                    elif b_type == "image":
                        docx_builder.add_image(blk["path"], blk.get("alt", ""))

                docx_builder.save()
                results["docx"] = docx_path
            except Exception as e:
                print(f"  [ERROR] DOCX generation failed: {e}", file=sys.stderr)
                raise

        return results


def convert_file(input_path, pdf_path=None, docx_path=None, title=None, author=None, org=None, date_str=None):
    """Converts a Markdown or JSON file to PDF and/or DOCX."""
    with open(input_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    input_dir = os.path.dirname(os.path.abspath(input_path))
    meta = {}
    blocks = []

    if input_path.endswith(".json"):
        data = json.loads(raw_content)
        meta = data.get("metadata", {})
        blocks = data.get("blocks", [])
    else:
        # Markdown
        meta, md_text = parse_frontmatter(raw_content)
        blocks = parse_markdown_blocks(md_text, input_dir=input_dir)

    doc_title = title or meta.get("title") or "Executive Research Report"
    doc_subtitle = meta.get("subtitle", "")
    doc_author = author or meta.get("author", "Principal Research Analyst")
    doc_org = org or meta.get("organization") or meta.get("org", "TeknoKeys Strategic Research")
    doc_date = date_str or meta.get("date", datetime.date.today().strftime("%B %d, %Y"))

    exporter = DocumentExporter(
        title=doc_title,
        subtitle=doc_subtitle,
        author=doc_author,
        organization=doc_org,
        date_str=doc_date,
        input_dir=input_dir
    )

    # Derive default output paths if neither provided
    base_name, _ = os.path.splitext(input_path)
    if not pdf_path and not docx_path:
        pdf_path = f"{base_name}.pdf"
        docx_path = f"{base_name}.docx"

    return exporter.export(blocks, pdf_path=pdf_path, docx_path=docx_path)


def main():
    parser = argparse.ArgumentParser(description="Professional Research Report Exporter v2.0 (PDF & DOCX)")
    parser.add_argument("--input", "-i", required=True, help="Input Markdown (.md) or JSON (.json) file")
    parser.add_argument("--pdf", "-p", help="Output PDF file path")
    parser.add_argument("--docx", "-d", help="Output Microsoft Word (.docx) file path")
    parser.add_argument("--title", "-t", help="Override document title")
    parser.add_argument("--author", "-a", help="Override author name")
    parser.add_argument("--org", "-o", help="Override organization")
    parser.add_argument("--date", help="Override report date")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"[+] Processing research report: {args.input}")
    res = convert_file(
        input_path=args.input,
        pdf_path=args.pdf,
        docx_path=args.docx,
        title=args.title,
        author=args.author,
        org=args.org,
        date_str=args.date
    )

    for fmt, path in res.items():
        size_kb = os.path.getsize(path) / 1024
        print(f"  -> Generated {fmt.upper()}: {path} ({size_kb:.1f} KB)")
    print("[✓] Dual export completed successfully.")


if __name__ == "__main__":
    main()
