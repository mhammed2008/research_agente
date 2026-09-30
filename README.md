# Autonomous Research & Presentation Agent System (`research_agente`) v3.0

> **End-to-End Multi-Agent System** for autonomous deep technical research, ≥90% multi-source fact verification, brand visual identity synthesis, bespoke presentation architecture, multi-format compilation (**PDF, Microsoft Word .docx, PowerPoint .pptx**), and multimodal visual critique.

---

## 🚀 Overview

`research_agente` is a full autonomous multi-agent system designed for executive consulting, technical whitepapers, and presentation decks. Rather than operating as a passive script runner, it orchestrates **5 specialized autonomous agent roles** to take a raw mandate, conduct rigorous investigation, design a bespoke visual narrative, and visually audit the rendered deliverables.

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
│ Deep Fact            │          │ Creative             │          │ High-Fidelity        │
│ Investigator Agent   │          │ Presentation         │          │ Document Compiler    │
│                      │          │ Architect Agent      │          │ Engine               │
└──────────┬───────────┘          └──────────┬───────────┘          └──────────┬───────────┘
           │                                  │                                  │
           │ (≥90% Triangulation Gate)        │ (Brand Identity & Dynamic Deck)  │ (PDF, DOCX, PPTX)
           └──────────────────────────────────┼──────────────────────────────────┘
                                              │
                                              ▼
                               ┌──────────────────────────────┐
                               │ Multimodal Visual Critic     │
                               │   (Vision QA & Self-Correction)│
                               └──────────────────────────────┘
```

---

## 🤖 The 6 Specialized Autonomous Agent Roles

1. **Lead Orchestrator Agent (`ResearchOrchestrator`)**:
   - Manages state machine progression: Intake $\rightarrow$ Decomposition $\rightarrow$ Investigation $\rightarrow$ Design $\rightarrow$ Compilation $\rightarrow$ Visual Audit $\rightarrow$ Completed.
   - Decomposes complex mandates into structured technical investigation hypotheses.
2. **Deep Fact Investigator Agent (`FactInvestigatorAgent`)**:
   - Enforces the **strict ≥90% accuracy triangulation gate**.
   - Classifies sources by confidence tiers:
     - **Tier 1 (95–100%)**: Primary standards (ISO, PCI DSS, IEEE, NIST, IETF RFCs, vendor datasheets).
     - **Tier 2 (85–94%)**: Peer-reviewed papers, analyst reports (Gartner, IDC), technical journalism.
     - **Tier 3 (<75%)**: Marketing brochures and blogs (never used alone).
   - Triangulates quantitative metrics (TPS, latency, cost, security models).
3. **Domain Template Researcher Agent (`DomainTemplateResearcherAgent`)**:
   - Researches real-world presentation designs, visual hierarchy, and narrative benchmarks in the subject domain (e.g. Stripe, Square, CrowdStrike, Datadog) before synthesizing the deck.
   - Recommends the optimal structural archetype and narrative flow.
4. **Presentation Architect Agent (`PresentationArchitectAgent`)**:
   - **Brand Logo Priority**: Extracts authentic primary and accent colors directly from brand logos (e.g. TeknoKeys Amber Gold `#E8A828` and Obsidian `#0A0F1D`).
   - **Dynamic Domain Adaptation**: Maps industries to structural archetypes (`modern_dark`, `consulting_grid`, `minimal_editorial`, `warm_organic`, `vibrant_bold`).
   - **Structural Diversity (Zero Card-Box Monotony)**: Sequences diverse slide structures:
     - `split-hero`: 35% strategic quote panel + 65% clean numbered agenda items.
     - `versus`: Asymmetric problem vs. solution battle layout with central floating `VS` badge.
     - `architecture`: 3-tier system topology stack with vertical flow indicators.
     - `timeline`: Real horizontal milestone stepper with connecting guideline and circular node pills.
     - `grid`: 2x2 balanced feature matrix with colored side indicator bars.
     - `metrics`: Clean floating KPI cards (`<0.3s`, `>99.9%`, `0% Fraud`).
     - `table`: High-contrast comparative evaluation matrix.
5. **Document Compiler Agent (`DocumentCompilerAgent`)**:
   - Compiles markdown sources into publication-grade **PowerPoint (.pptx)**, **PDF**, and **Word (.docx)**.
   - Injects OpenXML `<a:pPr rtl="1"/>` and complex script Arabic fonts for seamless Right-to-Left (RTL) support.
   - Vector Mermaid diagram compilation in PDF via headless browser pipeline and executive diagram cards in DOCX.
6. **Multimodal Visual Critic Agent (`VisualCriticAgent`)**:
   - Renders slides to high-resolution PNG images via PowerPoint COM automation.
   - Inspects geometry, margins, text length, and formatting defects (e.g., catching and preventing line-wrapping in badges).
   - Mandates automated self-correction before final delivery.

---

## 📦 Quick Start & CLI Usage

### 1. Install Dependencies
```bash
pip install -r .agents/skills/professional-researcher/requirements.txt
```

### 2. Autonomous Execution (Unified CLI)
Run the full multi-agent pipeline from a single command:
```bash
python run_agent.py "Jaib Wallet & TeknoNFC Strategic Partnership" \
  --domain "FinTech" \
  --logo "researches/jaib_nfc_partnership_proposal/assets/teknokeys_logo.png" \
  --report "researches/jaib_nfc_partnership_proposal/report/jaib_nfc_technical_proposal.md" \
  --presentation "researches/jaib_nfc_partnership_proposal/presentation/jaib_nfc_presentation.md" \
  --output-dir "researches/jaib_nfc_partnership_proposal/agent_system_output" \
  --formats "pptx,pdf,docx"
```

### 3. Run Test Suite
Execute the full unit and integration test suite across all agents and exporters:
```bash
python -m pytest tests/test_agent_system.py skills/professional-researcher/scripts/test_exporter.py -v
```
*(All 66 tests pass cleanly in ~3.5s)*

---

## 🏛️ Project & Plugin Architecture

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
│       ├── compiler.py               # Document & slide deck compiler
│       └── auditor.py                # Multimodal visual quality auditor
├── researches/                       # Dedicated research workspaces (git-ignored)
│   ├── jaib_nfc_partnership_proposal/
│   ├── jaib_nfc_poc_walkthrough/
│   └── yemen_dog_rescue_initiative/
├── skills/professional-researcher/   # Foundational SDK & exporter engines
│   ├── scripts/
│   │   ├── export_engine.py          # Unified CLI, Markdown parser, triple exporter
│   │   ├── html_builder.py           # HTML & Mermaid.js vector diagram builder
│   │   ├── color_synthesizer.py      # Logo color extraction & palette synthesis
│   │   ├── pptx_builder.py           # 16:9 Widescreen PPTX engine with RTL
│   │   ├── pdf_builder.py            # Platypus PDF engine with RTL & TOC
│   │   ├── docx_builder.py           # Word DOCX engine with RTL OpenXML
│   │   └── test_exporter.py          # Exporter test suite (52 tests)
│   ├── references/
│   │   ├── diagrams_and_visuals_guide.md # Mermaid architecture & classDef standards
│   │   └── presentation_styling_guide.md # Archetypes and design tokens
│   └── templates/                    # Production-ready markdown templates
└── tests/
    └── test_agent_system.py          # Agent system unit & integration test suite (14 tests)
```
