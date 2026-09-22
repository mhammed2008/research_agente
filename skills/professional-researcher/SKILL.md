---
name: professional-researcher
description: >-
  Autonomous deep research, fact verification, and publication-grade document generation engine (v2.0).
  Activates when the user requests comprehensive research, market/technical analysis, architectural evaluation,
  or asks to export/compile research into polished PDF and Microsoft Word (.docx) documents with executive
  covers, Table of Contents, callouts, blockquotes, inline formatting, embedded images,
  nested bullets, and data comparison tables in any language (including Arabic, English, etc.).
  Enforces a strict ≥90% accuracy gate with multi-source triangulation.
---

# Professional Researcher Skill (`professional-researcher`) v2.0

An end-to-end, high-rigor autonomous research and multi-format publishing engine. It orchestrates systematic problem decomposition, multi-source web/standards/codebase investigation, strict **≥90% fact verification and triangulation**, and automatically compiles, formats, and exports publication-grade **PDF documents** and **Microsoft Word documents (`.docx`)** in **any language** (including full Right-to-Left Arabic/Hebrew support).

---

## 🆕 v2.0 Enhancements

- **Nested bullet support** with indent levels (0, 1, 2) in both PDF and DOCX
- **Rich inline DOCX formatting** — bold, italic, and code render as proper Word Runs (not stripped)
- **Image/figure embedding** — `![alt](path)` syntax detects and embeds images with captions
- **Blockquote rendering** — plain `>` quotes distinguished from `[!NOTE]` callouts, rendered with gray accent bar
- **Table of Contents** — automatically generated after cover page in both PDF and DOCX
- **Cross-platform fonts** — Windows, macOS, and Linux font paths probed
- **Code language detection** — ` ```python ` blocks capture the language identifier
- **Error handling** — graceful error messages for missing images, failed exports
- **Improved parser** — fixed numbered list false-positive ("3 years later" no longer becomes a bullet)
- **pytest test suite** — 30+ unit tests covering all parser functions

---

## 🎯 When to Activate This Skill

Use this skill whenever:
1. The user asks to **conduct deep research**, write an executive whitepaper, or evaluate an unknown technology, system, or market.
2. The user requires **rigorous fact-checking with at least 90% data accuracy** and multi-source corroboration.
3. The user needs to **search for anything** across arbitrary domains (kernel, hardware, AI, cryptography, law, economics, telecom, etc.).
4. The user requests **exporting or generating PDF or Microsoft Word (`.docx`) reports** in **English, Arabic, or any other language**.
5. The user wants to convert existing notes or analyses into high-impact executive deliverables.

---

## 🛡️ The ≥ 90% Accuracy & Fact-Verification Protocol

To guarantee that research deliverables achieve **at least 90% verified factual precision**, the agent strictly adheres to the following evidence rules:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       3-TIER SOURCE HIERARCHY                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ • TIER 1 [High Confidence 95-100%]: Primary specifications (ISO, PCI, IEEE, │
│   IETF RFCs, NIST), regulatory filings, official vendor datasheets/manuals, │
│   primary API documentation, and official GitHub source releases.           │
│                                                                             │
│ • TIER 2 [Medium Confidence 85-94%]: Peer-reviewed whitepapers, reputable   │
│   industry analyst reports (Gartner, Forrester, IDC), established technical │
│   journalism (Ars Technica, Reuters, Bloomberg), active developer telemetry.│
│                                                                             │
│ • TIER 3 [Cautionary <75%]: Marketing landing pages, vendor brochures, SEO  │
│   listicles, uncorroborated forum threads. NEVER use alone as evidence.     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mandatory Rules for High-Fidelity Research:
1. **The 2-Source Triangulation Rule**: Any quantitative claim (pricing, transaction latency, battery capacity, throughput, memory overhead) or architectural assertion MUST be corroborated by at least **two independent sources** before being stated as fact.
2. **Explicit Confidence Ratings**: Tag critical findings, data points, or tables with verification levels:
   - `🟢 [VERIFIED: HIGH CONFIDENCE (≥90%)]`: Directly confirmed by Tier 1 primary sources or multiple independent benchmarks.
   - `🟡 [PROVISIONAL: MEDIUM CONFIDENCE (75-89%)]`: Plausible from reputable secondary sources, awaiting direct production telemetry.
   - `🔴 [UNVERIFIED / CONTESTED (<75%)]`: Divergent vendor claims or conflicting data.
3. **Discrepancy Resolution (Never Mask Conflicting Data)**: If source A claims 1,500 TPS and source B claims 500 TPS, state both and identify the discrepancy (e.g. *"Vendor lab test with zero encryption vs. real-world TLS 1.3 overhead"*).
4. **Zero-Hallucination Fallback**: If an exact parameter (e.g. chip pinout, wholesale interchange fee) is unpublished, write *"Unpublished by OEM / Pending laboratory test"* instead of inventing plausible approximations.

---

## 🌐 Universal Search & Investigation Strategy

The skill can investigate **any domain or technology** by synthesizing targeted, multi-perspective search queries:

1. **Foundational Specifications & RFCs**:
   - `"[technology]" ("specification" OR "whitepaper" OR "RFC" OR "architecture")`
2. **Security & Vulnerability Intelligence**:
   - `"[technology]" ("CVE" OR "vulnerability" OR "attestation" OR "audit report" OR "exploit")`
3. **Hardware & Systems Datasheets**:
   - `"[chip/OEM model]" ("datasheet" OR "pinout" OR "block diagram" OR "firmware")`
4. **Financial, Unit Economics & Regulatory**:
   - `"[market/fintech]" ("fee schedule" OR "interchange" OR "basis points" OR "compliance")`
5. **Open Source & Implementation Inspection**:
   - `site:github.com "[protocol/library]" ("README" OR "releases" OR "issues")`

---

## 🌍 Multilingual & Multi-Language Publishing (PDF & Word)

The rendering engines are pre-configured to output publication-grade deliverables in **any language**:

### 1. Arabic & Right-to-Left (RTL) Support:
- **PDF Engine (`pdf_builder.py`)**: Automatically detects Arabic/Hebrew Unicode characters, applies Arabic contextual glyph reshaping via `arabic_reshaper`, applies BiDi reordering via `bidi.algorithm`, switches alignment to right-to-left, and subsets Windows/macOS/Linux system Unicode TrueType fonts (`Arial`, `Segoe UI`, `Tahoma`, `Liberation Sans`, `DejaVu Sans`).
- **Word Engine (`docx_builder.py`)**: Injects OpenXML `<w:bidi/>` into paragraph properties, `<w:rtl/>` into character run properties, mirrors table cell borders, and right-aligns headings.

### 2. English & Left-to-Right (LTR) Support:
- Crisp corporate styling, deep navy primary accents (`#0F172A`), royal blue highlights (`#2563EB`), zebra row shading, and two-pass `Page X of Y` running headers/footers.

---

## 🖼️ Markdown Syntax Reference

### Images
```markdown
![Descriptive caption](path/to/image.png)
```
Images are embedded in both PDF and DOCX with automatic aspect ratio preservation and centered caption.

### Nested Bullets
```markdown
- Top level item
  - Second level item
      - Third level item
```

### Blockquotes (plain quotes, NOT callouts)
```markdown
> This is a simple blockquote rendered with a gray accent bar.
```

### Callout Alerts (GitHub-style)
- `> [!NOTE]` — General operational insights & background context (Blue tint)
- `> [!TIP]` — Strategic recommendations & cost-saving tactics (Emerald tint)
- `> [!IMPORTANT]` — Regulatory compliance, security mandates & critical findings (Rose tint)
- `> [!WARNING]` — High-risk technical gotchas, vendor traps & failure modes (Amber tint)

### Inline Formatting (DOCX-aware)
- `**bold**` — Renders as bold Word Run in DOCX
- `*italic*` — Renders as italic Word Run in DOCX
- `` `code` `` — Renders in Consolas with gray background shading in DOCX

---

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r .agents/skills/professional-researcher/requirements.txt
```

### 2. Automated Dual-Export (CLI)
```bash
# Convert an English or Arabic research report into both PDF and Word (.docx)
python .agents/skills/professional-researcher/scripts/export_engine.py \
  --input my_report.md \
  --pdf my_report.pdf \
  --docx my_report.docx

# With custom metadata overrides
python .agents/skills/professional-researcher/scripts/export_engine.py \
  --input report.md \
  --pdf final.pdf \
  --docx final.docx \
  --title "Custom Strategic Title" \
  --author "Lead Researcher" \
  --org "TeknoKeys Enterprise"
```

### 3. Python API Integration
```python
from export_engine import convert_file

convert_file(
    input_path="analysis.md",
    pdf_path="analysis.pdf",
    docx_path="analysis.docx",
    title="Executive Briefing",
    author="Research Director",
    org="TeknoKeys Intelligence"
)
```

### 4. Run Test Suite
```bash
pytest .agents/skills/professional-researcher/scripts/test_exporter.py -v
```

---

## 📁 Skill Architecture

```text
skills/professional-researcher/
├── SKILL.md                          # Master skill instructions and rules
├── README.md                         # Quick-start guide
├── package.json                      # Metadata (v2.0)
├── requirements.txt                  # Python dependencies [NEW]
├── scripts/
│   ├── export_engine.py              # Unified CLI, parser, inline run parser [UPGRADED]
│   ├── pdf_builder.py                # Cross-platform PDF engine w/ TOC, images, blockquotes [UPGRADED]
│   ├── docx_builder.py               # Rich-format DOCX engine w/ TOC, images, blockquotes [UPGRADED]
│   └── test_exporter.py              # pytest test suite (30+ tests) [UPGRADED]
├── templates/
│   ├── research_report_template.md   # Standard comprehensive report template
│   ├── executive_brief_template.md   # 2-3 page executive brief
│   ├── technical_deep_dive.md        # Deep architectural blueprint
│   └── report_schema.json            # Structured JSON schema (v2.0) [UPGRADED]
├── references/
│   ├── research_protocol.md          # ≥90% accuracy & triangulation rules
│   ├── visual_styling_guide.md       # Typography, palette, and table styling
│   ├── multilingual_guide.md         # Multilingual & RTL formatting guide
│   └── export_api_reference.md       # Python API reference
└── examples/
    ├── sample_research_input.md      # Full English research report
    ├── sample_arabic_research.md     # Full Arabic research report
    ├── sample_research_output.pdf    # Compiled English PDF
    ├── sample_research_output.docx   # Compiled English DOCX
    ├── sample_arabic_research.pdf    # Compiled Arabic PDF
    └── sample_arabic_research.docx   # Compiled Arabic DOCX
```
