# Professional Researcher Skill (`professional-researcher`) v2.2

> Autonomous, publication-grade research, dual-document and 16:9 presentation publishing engine for **PDF**, **Microsoft Word (.docx)**, and **PowerPoint (.pptx)** with dynamic non-hardcoded styling, custom logo branding, interactive intake wizard, nested bullets, images, TOC, rich inline formatting, and multilingual RTL support.

## 🚀 Overview

The **Professional Researcher** skill transforms research prompts and unstructured notes into executive-ready, publication-grade documents and presentations. It incorporates a formal 5-phase research methodology (Scoping, Retrieval, Triangulation, Synthesis, and Publishing) alongside native Python exporters that generate:
- **PDF Documents**: Styled with ReportLab Platypus, featuring dedicated executive cover pages, custom brand logos, auto-generated Table of Contents, running headers/footers with dynamic "Page X of Y" counters, zebra-striped data matrices, color-coded callouts, embedded images with captions, and nested bullet indentation.
- **Word Documents (`.docx`)**: Styled with `python-docx` and custom OpenXML, featuring custom brand logos, rich inline formatting (bold, italic, code as separate Word Runs with Consolas font + shading), heading hierarchy mapped to the Word Navigation Pane, formatted tables, styled callout boxes, blockquotes, and embedded images.
- **PowerPoint Presentations (`.pptx`)**: Modern 16:9 widescreen slides with dynamic color themes, custom brand logos on title slides and content headers, native OpenXML RTL attributes, pre-designed slide layouts (Agenda, 2-Column, KPI Metrics Cards, Alert Callouts, Data Tables, Code blocks, and Closing slides).

## 📦 Quick Start

### 1. Install Dependencies
```bash
pip install -r .agents/skills/professional-researcher/requirements.txt
```

### 2. Interactive Style & Requirements Wizard
Launch the questionnaire to configure custom palettes, verify brand logos, and specify research scope:
```bash
python .agents/skills/professional-researcher/scripts/export_engine.py --wizard
```

### 3. Generate PDF, Word & PowerPoint from Markdown
```bash
# Triple-export with custom colors and logo
python .agents/skills/professional-researcher/scripts/export_engine.py \
  --input my_report.md \
  --pdf my_report.pdf \
  --docx my_report.docx \
  --pptx my_presentation.pptx \
  --logo assets/logo.png \
  --primary-color "#064E3B" \
  --accent-color "#059669"
```

### 4. Run Test Suite
```bash
pytest .agents/skills/professional-researcher/scripts/test_exporter.py -v
```

## 📋 Markdown Frontmatter Support

Add YAML frontmatter to your markdown file to automatically populate document covers and apply custom branding:

```yaml
---
title: "Autonomous AI Agents in Enterprise FinTech"
subtitle: "Architectural Benchmarks, Security Attestation, and Operational ROI"
author: "Senior AI & Security Researcher"
organization: "TeknoKeys Enterprise Intelligence"
date: "September 2026"
branding:
  primary_color: "#064E3B"
  accent_color: "#059669"
  secondary_color: "#022C22"
  logo: "assets/logo.png"
  font_family: "Arial"
---
```

## 🎨 Curated Style Presets
- `corporate-navy` (`#0F172A` / `#2563EB`) — Institutional, whitepapers, banking
- `fintech-emerald` (`#064E3B` / `#059669`) — Modern fintech, sustainability, payments
- `minimal-slate` (`#0F172A` / `#475569`) — Modern engineering, developer architecture
- `executive-crimson` (`#881337` / `#E11D48`) — Defense, strategic audits, luxury
- `luxury-violet` (`#4C1D95` / `#7C3AED`) — Deep tech, AI labs, creative intelligence
- *Arbitrary Hex*: Pass any valid hex code directly via CLI or wizard

## 🖼️ Markdown Syntax Features

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

### Blockquotes
```markdown
> This renders as a plain quote with a colored accent bar.
```

### Rich Inline Formatting (preserved in DOCX)
- `**bold text**` → Bold Word Run
- `*italic text*` → Italic Word Run
- `` `code text` `` → Consolas font with background shading

## 🏷️ Callout Alert Syntax

In your markdown text, use GitHub-style callouts:
- `> [!NOTE]` — General operational insights (Blue)
- `> [!TIP]` — Strategic recommendations (Emerald)
- `> [!IMPORTANT]` — Regulatory compliance & security mandates (Rose/Red)
- `> [!WARNING]` — High-risk technical gotchas & vendor traps (Amber)

## 📁 Directory Layout

- `scripts/`: Exporter CLI, style wizard, and rendering engines (`export_engine.py`, `style_wizard.py`, `pdf_builder.py`, `docx_builder.py`, `pptx_builder.py`, `test_exporter.py`).
- `templates/`: Pre-structured research report and presentation templates (`presentation_template.md`, `research_report_template.md`, `executive_brief_template.md`, `technical_deep_dive.md`, `report_schema.json`).
- `references/`: Methodology guidelines (`presentation_styling_guide.md`, `research_protocol.md`, `visual_styling_guide.md`, `multilingual_guide.md`, `export_api_reference.md`).
- `examples/`: Ready-to-compile sample input reports and pre-compiled PDF/DOCX/PPTX outputs in English and Arabic.

## 🧪 Testing

The test suite includes 45 comprehensive unit and integration tests covering:
- AST parser unit tests (headings, bullets, nested bullets, images, blockquotes, callouts, tables, code blocks)
- Inline run parser (bold, italic, code segmentation)
- Frontmatter & branding block extraction
- Custom dynamic hex palettes and logo embedding across PDF, DOCX, and PPTX
- Numbered list false-positive prevention
- Full English and Arabic presentation and document exports

```bash
pytest .agents/skills/professional-researcher/scripts/test_exporter.py -v
```

