# Professional Researcher Skill (`professional-researcher`) v2.0

> Autonomous, publication-grade research and dual-export publishing engine for **PDF** and **Microsoft Word (.docx)** documents with nested bullets, images, TOC, rich inline formatting, and multilingual RTL support.

## 🚀 Overview

The **Professional Researcher** skill transforms research prompts and unstructured notes into executive-ready, publication-grade documents. It incorporates a formal 5-phase research methodology (Scoping, Retrieval, Triangulation, Synthesis, and Publishing) alongside native Python exporters that generate:
- **PDF Documents**: Styled with ReportLab Platypus, featuring dedicated executive cover pages, auto-generated Table of Contents, running headers/footers with dynamic "Page X of Y" counters, zebra-striped data matrices, color-coded callouts, embedded images with captions, and nested bullet indentation.
- **Word Documents (`.docx`)**: Styled with `python-docx` and custom OpenXML, featuring rich inline formatting (bold, italic, code as separate Word Runs with Consolas font + shading), heading hierarchy mapped to the Word Navigation Pane, formatted tables, styled callout boxes, blockquotes, and embedded images.

## 📦 Quick Start

### 1. Install Dependencies
```bash
pip install -r .agents/skills/professional-researcher/requirements.txt
```

### 2. Generate PDF & Word from Markdown
```bash
python .agents/skills/professional-researcher/scripts/export_engine.py \
  --input my_report.md \
  --pdf my_report.pdf \
  --docx my_report.docx
```

### 3. Run Test Suite
```bash
pytest .agents/skills/professional-researcher/scripts/test_exporter.py -v
```

## 📋 Markdown Frontmatter Support

Add YAML frontmatter to your markdown file to automatically populate document cover pages:

```yaml
---
title: "Autonomous AI Agents in Enterprise FinTech"
subtitle: "Architectural Benchmarks, Security Attestation, and Operational ROI"
author: "Senior AI & Security Researcher"
organization: "TeknoKeys Enterprise Intelligence"
date: "September 2026"
---
```

## 🖼️ v2.0 New Markdown Syntax

### Nested Bullets
```markdown
- Top level item
  - Sub-item (indent 2-4 spaces)
      - Sub-sub-item (indent 5+ spaces)
```

### Images with Captions
```markdown
![Architecture diagram](images/architecture.png)
```

### Blockquotes (distinct from callouts)
```markdown
> This renders as a plain quote with a gray accent bar.
```

### Rich Inline Formatting (preserved in DOCX)
- `**bold text**` → Bold Word Run
- `*italic text*` → Italic Word Run
- `` `code text` `` → Consolas font with gray background shading

## 🏷️ Callout Alert Syntax

In your markdown text, use GitHub-style callouts:
- `> [!NOTE]` — General operational insights (Blue)
- `> [!TIP]` — Strategic recommendations (Emerald)
- `> [!IMPORTANT]` — Regulatory compliance & security mandates (Rose/Red)
- `> [!WARNING]` — High-risk technical gotchas & vendor traps (Amber)

## 📁 Directory Layout

- `scripts/`: Exporter CLI and rendering engines (`export_engine.py`, `pdf_builder.py`, `docx_builder.py`, `test_exporter.py`).
- `templates/`: Pre-structured research report templates (`research_report_template.md`, `executive_brief_template.md`, `technical_deep_dive.md`, `report_schema.json`).
- `references/`: Methodology guidelines (`research_protocol.md`, `visual_styling_guide.md`, `multilingual_guide.md`, `export_api_reference.md`).
- `examples/`: Ready-to-compile sample input reports and pre-compiled PDF/DOCX outputs.

## 🧪 Testing

The test suite includes 30+ tests covering:
- Parser unit tests (headings, bullets, nested bullets, images, blockquotes, callouts, tables, code blocks)
- Inline run parser (bold, italic, code segmentation)
- Frontmatter extraction
- Numbered list false-positive prevention
- Full English and Arabic integration exports

```bash
pytest .agents/skills/professional-researcher/scripts/test_exporter.py -v
```
