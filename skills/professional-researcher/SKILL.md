---
name: professional-researcher
description: >-
  Autonomous deep research, fact verification, and publication-grade document and presentation generation engine (v3.0).
  Activates when the user requests comprehensive research, market/technical analysis, architectural evaluation,
  or asks to export/compile research into polished PDF, Microsoft Word (.docx), and PowerPoint (.pptx) presentation decks
  with executive covers, Table of Contents, callouts, blockquotes, inline formatting, embedded images,
  nested bullets, KPI metric cards, two-column layouts, data comparison tables, custom brand logos,
  and dynamic non-hardcoded color palettes in any language (including Arabic, English, etc.).
  Enforces a strict ≥90% accuracy gate with multi-source triangulation and an adaptive intake questionnaire.
---

# Professional Researcher & Presentation Engine (`professional-researcher`) v3.0

An end-to-end, high-rigor autonomous multi-agent research and multi-format publishing engine. It orchestrates systematic problem decomposition, multi-source web/standards/codebase investigation, strict **≥90% fact verification and triangulation**, dynamic domain template benchmarking, brand visual identity extraction, and automatically compiles, formats, and exports publication-grade **PDF documents**, **Microsoft Word documents (`.docx`)**, and **PowerPoint presentations (`.pptx`)** in **any language** (including full Right-to-Left Arabic/Hebrew support).

---

## 🚀 The Multi-Agent Pipeline Architecture (v3.0)

`research_agente` operates as an autonomous multi-agent system comprising **6 specialized agent roles**:

```
                       ┌──────────────────────────────────────────────┐
                       │          Lead Orchestrator Agent             │
                       │    (Lifecycle & Problem Decomposition)       │
                       └──────────────────────┬───────────────────────┘
                                              │
           ┌──────────────────────────────────┼──────────────────────────────────┐
           │                                  │                                  │
           ▼                                  ▼                                  ▼
┌──────────────────────┐          ┌──────────────────────┐          ┌──────────────────────┐
│ Deep Fact            │          │ Domain Template      │          │ High-Fidelity        │
│ Investigator Agent   │          │ Researcher Agent     │          │ Document Compiler    │
│ (≥90% Triangulation) │          │ (Benchmark Scouring) │          │ (PDF, DOCX, PPTX)    │
└──────────┬───────────┘          └──────────┬───────────┘          └──────────┬───────────┘
           │                                  │                                  │
           └──────────────────────────────────┼──────────────────────────────────┘
                                              │
                                              ▼
                               ┌──────────────────────────────┐
                               │ Creative Presentation        │
                               │ Architect Agent              │
                               │ (Dynamic Layout & Branding)  │
                               └──────────────┬───────────────┘
                                              │
                                              ▼
                               ┌──────────────────────────────┐
                               │ Multimodal Visual Critic     │
                               │ (COM Vision QA & Critique)   │
                               └──────────────────────────────┘
```

### The 6 Specialized Autonomous Roles:
1. **Lead Orchestrator Agent (`ResearchOrchestrator`)**:
   - Manages state machine progression: Intake $\rightarrow$ Decomposition $\rightarrow$ Investigation $\rightarrow$ Design $\rightarrow$ Compilation $\rightarrow$ Visual Audit $\rightarrow$ Completed.
   - Decomposes mandates into 5 core hypotheses.
2. **Deep Fact Investigator Agent (`FactInvestigatorAgent`)**:
   - Decomposes research topics into hypotheses, parses quantitative claims, categorizes sources into 3 tiers, and enforces the **strict ≥90% accuracy triangulation gate**.
3. **Domain Template Researcher Agent (`DomainTemplateResearcherAgent`)**:
   - Autonomously researches real-world presentation designs, visual hierarchy, and narrative benchmarks in the subject domain (e.g. Stripe, Square, CrowdStrike, Datadog) before synthesizing the deck.
4. **Presentation Architect Agent (`PresentationArchitectAgent`)**:
   - Extracts authentic brand primary and accent colors directly from brand logos without artificial darkening.
   - Sequences structurally diverse slide layouts (`split-hero`, `versus`, `architecture`, `timeline`, `grid`, `metrics`, `table`) to eliminate repetitive box monotony.
5. **Document Compiler Agent (`DocumentCompilerAgent`)**:
   - Compiles markdown sources into publication-grade **PowerPoint (.pptx)**, **PDF**, and **Word (.docx)**.
   - Injects OpenXML `<a:pPr rtl="1"/>` and complex script Arabic fonts for seamless Right-to-Left (RTL) support.
6. **Multimodal Visual Critic Agent (`VisualCriticAgent`)**:
   - Renders slides to high-resolution PNG images via PowerPoint COM automation.
   - Visually inspects geometry, margins, text length, and formatting defects (e.g., catching line-wrapping in badges).
   - Mandates automated self-correction before final delivery.

---

## 📁 Workspace & Deliverables Management (`researches/` Mandate)

All research mandates, project workspaces, and generated deliverables **must be organized under `researches/`**:

```text
researches/
└── <research_topic_slug>/
    ├── report/                      # Comprehensive technical research reports (Markdown, PDF, DOCX)
    ├── presentation/                # Executive slide decks (Markdown, PPTX, PDF)
    │   └── slides_preview/          # High-resolution slide PNG preview images
    ├── assets/                      # Brand logos, architectural diagrams, screenshots
    └── agent_system_output/         # Autonomous pipeline execution artifacts and logs
```

- **Git-Ignored Protection**: `researches/` is explicitly declared in `.gitignore` to prevent client research deliverables and large binary presentations from polluting version control.
- **Repository Root Cleanliness**: Never output loose research files in the root workspace.

---

## 🎨 Domain-Adaptive Archetypes (5 Visual Paradigms)

Styling is dynamically selected based on industry benchmarks:
1. `modern_dark`: Deep obsidian/charcoal canvas (`#0A0F1D`), dark translucent cards (`#151E2E`), subtle hairline borders (`#2A3854`), glowing accent titles, high-contrast white text, tech badges (ideal for AI, CyberSec, Web3, Cloud).
2. `minimal_editorial`: Pure white/milk canvas (`#FFFFFF`), **frameless / borderless layout** without container box cages, asymmetric split columns, 52pt+ oversized numbers, bold Swiss typography (ideal for Luxury, Architecture, High-Level Strategy).
3. `consulting_grid`: Soft slate canvas (`#F8FAFC`), crisp white container cards with subtle borders, structured grids, category breadcrumbs (ideal for Corporate Governance, Banking, M&A).
4. `warm_organic`: Soft cream/sand canvas (`#FBF9F4`), warm card containers, rounded pill badges, earthy palette tones (ideal for NGOs, Veterinary/Wildlife, Healthcare, Sustainability).
5. `vibrant_bold`: High-energy contrast, solid color metric tiles, bold header banners, contrasting dark/bright breaker cards (ideal for Pitch Decks, Marketing, Product Launches).

---

## 🏛️ Structural Slide Diversity (Zero Card-Box Monotony)

Repetitive container boxes are strictly forbidden. The system sequences varied structures:
- `split-hero`: 35% strategic quote panel + 65% clean numbered items with hairline divider rules.
- `versus`: Asymmetric problem vs. solution battle layout with central floating `VS` badge.
- `architecture`: 3-tier system topology stack with vertical flow indicators.
- `timeline` / `process` / `roadmap`: Real horizontal milestone stepper with connecting guideline and numbered circular node pills (`word_wrap=False`, 0 margins).
- `grid`: 2x2 balanced feature matrix with colored side indicator bars.
- `metrics`: Clean floating KPI cards (`<0.3s`, `>99.9%`, `0% Fraud`).
- `table`: High-contrast comparative evaluation matrix.
- `agenda`: Executive numbered item sequence.

---

## 🛡️ The ≥ 90% Accuracy & Fact-Verification Protocol

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
│                                                                             │
│ ==> MANDATE: Quantitative claims (TPS, latency, cost) require 2-source      │
│     triangulation and explicit confidence rating tags.                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌍 Multilingual & Multi-Language Publishing (PDF, Word & PowerPoint)

### 1. Arabic & Right-to-Left (RTL) Support:
- **PowerPoint Engine (`pptx_builder.py`)**: Automatically detects Arabic/Hebrew Unicode characters, injects OpenXML `<a:pPr rtl="1"/>` into paragraph properties, assigns complex script font `<a:cs typeface="Arial"/>`, right-aligns text, and mirrors geometry (card order, badge positions).
- **PDF Engine (`pdf_builder.py`)**: Automatically detects Arabic/Hebrew characters, applies Arabic contextual glyph reshaping via `arabic_reshaper`, applies BiDi reordering via `bidi.algorithm`, switches alignment to right-to-left, and subsets system Unicode TrueType fonts.
- **Word Engine (`docx_builder.py`)**: Injects OpenXML `<w:bidi/>` into paragraph properties, `<w:rtl/>` into character run properties, mirrors table cell borders, and right-aligns headings.

### 2. English & Left-to-Right (LTR) Support:
- Crisp corporate styling, deep navy primary accents (`#0F172A`), royal blue highlights (`#2563EB`), zebra row shading, and two-pass `Page X of Y` running headers/footers.

---

## 📊 Architectural Diagrams & Visual Engineering in PDF

> [!IMPORTANT]
> **STRICT BAN ON ASCII / TEXT DIAGRAMS**
> - NEVER use ASCII art, unicode box-drawing characters (`│`, `┌─┐`, `└─┘`, `├──`, `└──`), or vertical arrows (`▼`, `▲`, `►`, `|`) inside code blocks or plaintext to illustrate a process, flowchart, or architecture.
> - Plaintext code blocks reverse and break Arabic letters, disconnect arrows, and look amateurish.
> - **ALWAYS** produce **REAL VISUAL DIAGRAMS** using **Mermaid (` ```mermaid `)**.

### PDF & Multi-Format Diagram Rendering Pipeline:
1. **Headless Vector Browser Pipeline (`html_builder.py` + Chromium)**:
   - When a research document contains ````mermaid```` blocks, `export_engine.py` builds an HTML intermediate with `HTMLReportBuilder` and compiles Mermaid.js diagrams with custom executive theme variables (Cairo/Inter typography, harmonious colors).
   - Renders pixel-perfect vector SVG diagrams directly into the PDF via Headless Chromium (`--headless=new`, `--virtual-time-budget=6000`, `--print-to-pdf`), preventing page breaks inside diagram cards (`break-inside: avoid;`).
   - If no browser is present, it falls back gracefully to ReportLab.
2. **Word (.docx) Diagram Cards**:
   - `DocxReportBuilder.add_mermaid_block()` wraps Mermaid specifications in an executive bordered card with an accent badge and clean monospace font.
3. **Standardized Mermaid `classDef` Palette Tokens**:
   - Flowcharts must include standardized semantic tokens:
     ```mermaid
     flowchart TD
         classDef startEnd fill:#1e293b,stroke:#0f172a,stroke-width:2px,color:#ffffff,font-weight:bold;
         classDef process fill:#eff6ff,stroke:#2563eb,stroke-width:1.5px,color:#1e3a8a;
         classDef decision fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f,font-weight:bold;
         classDef successNode fill:#ecfdf5,stroke:#059669,stroke-width:2px,color:#065f46,font-weight:bold;
         classDef rejectNode fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#991b1b;
     ```
   - Reference: [`references/diagrams_and_visuals_guide.md`](file:///d:/Maxcode/research_agente/skills/professional-researcher/references/diagrams_and_visuals_guide.md).

---

## 📦 Execution & CLI Reference

### 1. Unified Autonomous Multi-Agent Pipeline (`run_agent.py`)
```bash
python run_agent.py "Autonomous Enterprise AI Gateways" \
  --domain "FinTech" \
  --archetype "modern_dark" \
  --logo "researches/my_project/assets/logo.png" \
  --report "researches/my_project/report/report.md" \
  --presentation "researches/my_project/presentation/deck.md" \
  --output-dir "researches/my_project/agent_system_output" \
  --formats "pptx,pdf,docx"
```

### 2. Interactive Intake & Style Wizard
```bash
# Standalone CLI Style Questionnaire
python skills/professional-researcher/scripts/export_engine.py --wizard

# Direct Multi-Format Conversion with Custom Palette
python skills/professional-researcher/scripts/export_engine.py \
  --input my_report.md \
  --pdf my_report.pdf \
  --docx my_report.docx \
  --pptx my_presentation.pptx \
  --logo assets/logo.png \
  --primary-color "#0A0F1D" \
  --accent-color "#38BDF8"
```

### 3. Comprehensive Test Suite
```bash
python -m pytest tests/test_agent_system.py skills/professional-researcher/scripts/test_exporter.py -v
```
*(All 65 unit and integration tests pass cleanly)*

---

## 📁 System Architecture Map

```text
research_agente/
├── run_agent.py                      # Master CLI entry point for the Multi-Agent System
├── research_agent/                   # Autonomous Agent Core Package
│   ├── core/
│   │   ├── orchestrator.py           # 6-phase master orchestrator
│   │   └── state.py                  # State models (ResearchState, FactItem, Palette)
│   └── agents/
│       ├── investigator.py           # Deep research & fact-verification agent
│       ├── template_researcher.py    # Benchmark deck & domain template researcher
│       ├── designer.py               # Creative presentation architect & brand extractor
│       ├── compiler.py               # Multi-format document compiler
│       └── auditor.py                # Multimodal visual quality auditor
├── researches/                       # Dedicated research workspaces (git-ignored)
│   ├── jaib_nfc_partnership_proposal/
│   ├── jaib_nfc_poc_walkthrough/
│   └── yemen_dog_rescue_initiative/
├── skills/professional-researcher/   # Foundational SDK & exporter engines
│   ├── scripts/
│   │   ├── export_engine.py          # Unified CLI, Markdown parser, triple exporter
│   │   ├── color_synthesizer.py      # Logo color extraction & palette synthesis
│   │   ├── pptx_builder.py           # 16:9 Widescreen PPTX engine with RTL
│   │   ├── pdf_builder.py            # Platypus PDF engine with RTL & TOC
│   │   ├── docx_builder.py           # Word DOCX engine with RTL OpenXML
│   │   └── test_exporter.py          # Exporter test suite (51 tests)
│   └── templates/                    # Production-ready markdown templates
└── tests/
    └── test_agent_system.py          # Agent system unit & integration test suite (14 tests)
```
