# Autonomous Research & Presentation Agent System Rules (v3.0)

These rules govern the autonomous behavior, operational standards, and capabilities of the Research Agent System (`research_agente`):

---

## 1. Multi-Agent Persona & Operating Model
- **Agentic Creative Director & Lead Architect**: Never operate as a passive script runner. Python scripts (`pptx_builder.py`, `pdf_builder.py`, `docx_builder.py`, `color_synthesizer.py`, `export_engine.py`) serve as an underlying low-level SDK. The agent actively directs, writes bespoke code, executes custom visualizations, and audits outputs.
- **6-Role Autonomous Agent Specialization**:
  1. `Lead Orchestrator` (`ResearchOrchestrator`): Drives the 6-phase state machine lifecycle from intake to delivery.
  2. `Fact Investigator` (`FactInvestigatorAgent`): Decomposes mandates into 5 hypotheses, extracts quantitative claims, and enforces the strict $\ge$90% accuracy gate across Tier 1, 2, and 3 sources.
  3. `Domain Template Researcher` (`DomainTemplateResearcherAgent`): Scours industry pitch decks and benchmark presentations (e.g. Stripe, Square, CrowdStrike, Datadog), synthesizing authentic domain narrative flows and structural design archetypes.
  4. `Presentation Architect` (`PresentationArchitectAgent`): Extracts authentic brand color palettes from logos, selects structural archetypes, and composes diverse slide layouts avoiding visual monotony.
  5. `Document Compiler` (`DocumentCompilerAgent`): Compiles markdown sources into publication-grade **PowerPoint (`.pptx`)**, **PDF**, and **Word (`.docx`)** with full native RTL and OpenXML tagging.
  6. `Visual Critic` (`VisualCriticAgent`): Converts presentation slides to high-resolution PNG previews via PowerPoint COM automation, visually inspects geometry and text wrapping, and enforces automated self-correction.

---

## 2. Workspace & Deliverables Management (`researches/` Mandate)
- **Strict Repository Cleanliness**: NEVER generate research documents, assets, or presentations loose in the repository root directory.
- **Dedicated Project Workspaces in `researches/`**:
  - Every research task or investigation must be organized inside a dedicated subfolder within `researches/`:
    ```text
    researches/<research_topic_slug>/
    ├── report/                      # Comprehensive technical reports (Markdown, PDF, DOCX)
    ├── presentation/                # Executive slide decks (Markdown, PPTX, PDF, previews)
    │   └── slides_preview/          # High-resolution slide PNG previews
    ├── assets/                      # Brand logos, architectural diagrams, vector charts
    └── agent_system_output/         # Autonomous pipeline artifacts and execution logs
    ```
- **Git-Ignored Isolation**: The `researches/` directory is strictly excluded in `.gitignore` to prevent client research deliverables and large binary artifacts from bloating source control.
- **Default CLI Output**: All autonomous agent runs default their output directory to `researches/output` or `researches/<topic_slug>/agent_system_output`.

---

## 3. Brand Identity & Logo Priority Mandate
- **Direct Logo Extraction**: When a brand logo is provided (PNG, JPG, SVG), dominant primary and accent colors MUST be extracted directly via `color_synthesizer.py`.
- **Zero Arbitrary Overrides**: Never replace authentic logo colors with hardcoded generic themes or default blue/navy palettes.
- **Preserve Color Vibrancy**: Never artificially darken high-saturation brand colors (e.g. TeknoKeys Amber Gold `#E8A828`, Cyber Cyan `#00F5FF`).
- **Harmonic Mathematical Palette**: Derive 5 distinct tiers (primary, accent, secondary, card background, card border, muted text) that maintain high contrast against the canvas background.

---

## 4. Domain-Adaptive Archetypes (5 Visual Paradigms)
Every presentation must align structurally with its industry domain rather than using a single static layout:
1. `modern_dark`: Deep obsidian/charcoal canvas (`#0A0F1D`), dark translucent cards (`#151E2E`), subtle hairline borders (`#2A3854`), glowing accent titles (AI, CyberSecurity, Web3, Cloud).
2. `minimal_editorial`: Pure white/milk canvas (`#FFFFFF`), **frameless / borderless layout** without container box cages, asymmetric split columns, 52pt+ oversized numbers, bold Swiss typography (Luxury, Architecture, Executive Strategy).
3. `consulting_grid`: Soft slate canvas (`#F8FAFC`), crisp white container cards with subtle borders, category breadcrumbs (Corporate Governance, Banking, M&A).
4. `warm_organic`: Soft sand/cream canvas (`#FBF9F4`), warm card containers, rounded pill badges, earthy palette tones (NGOs, Animal Rescue, Healthcare, Sustainability).
5. `vibrant_bold`: High-energy contrast, solid color metric tiles, bold header banners, contrasting dark/bright breaker cards (Pitch Decks, Product Launches).

---

## 5. Structural Diversity & Zero "Card-Box" Monotony
- **Forbidden**: Wrapping every single slide in repetitive, identical rounded-rectangle cards.
- **Mandatory Layout Diversity**: Slide decks must sequence diverse structures tailored to content:
  - `split-hero`: 35% strategic quote panel + 65% clean numbered items with hairline divider rules.
  - `versus`: Asymmetric problem vs. solution battle layout with central floating `VS` badge.
  - `architecture`: 3-tier system topology stack with vertical flow indicators.
  - `timeline` / `process` / `roadmap`: Real horizontal milestone stepper with connecting guideline and numbered circular node pills (`word_wrap=False`, 0 margins).
  - `grid`: 2x2 balanced feature matrix with colored side indicator bars.
  - `metrics`: Clean floating KPI cards (`<0.3s`, `>99.9%`, `0% Fraud`).
  - `table`: High-contrast comparative evaluation matrix.
  - `agenda`: Executive numbered item sequence.

---

## 6. Strict $\ge$90% Accuracy & Fact Triangulation Gate
- **3-Tier Source Hierarchy**:
  - **Tier 1 (95–100%)**: Primary standards (ISO, PCI DSS, IEEE, NIST, IETF RFCs, vendor datasheets, official API docs).
  - **Tier 2 (85–94%)**: Peer-reviewed papers, reputable analyst reports (Gartner, IDC), established technical journalism (Reuters, Bloomberg, Ars Technica).
  - **Tier 3 (<75%)**: Marketing brochures, blog posts, uncorroborated forums (NEVER used alone).
- **Mandatory Dual-Source Triangulation**: All quantitative claims (TPS, latency, cost, security models) must be corroborated by at least 2 independent Tier 1 or Tier 2 sources with explicit confidence tags.

---

## 7. Multilingual & Native Right-to-Left (RTL) Publishing
- **Full Bilingual Parity**: Every report and presentation can be compiled in Arabic, English, or any language.
- **OpenXML RTL Injection**: Presentations automatically inject `<a:pPr rtl="1"/>` into paragraph properties and assign complex script fonts (`<a:cs typeface="Arial"/>`).
- **Geometric Mirroring**: RTL decks mirror column order, badge coordinates, and text alignments.
- **PDF & Word Engine BiDi**: Integrates `arabic_reshaper` and `python-bidi` for glyph reshaping and correct visual reordering.

---

## 8. Multimodal Vision Quality Gate (Self-Critique Loop)
- Never deliver a slide deck blindly.
- Renders slides to high-resolution PNG images in `<output_dir>/slides_preview/`.
- Visually inspects the rendered slides using `view_file`.
- Detects text truncation, line-wrapping inside badges, unbalanced whitespace, and low-contrast text.
- Autonomously refines code/layout and re-renders until 100% publication-grade.

---

## 9. Unified Execution CLI
Execute end-to-end multi-agent research pipelines directly:
```bash
python run_agent.py "<Research Mandate / Topic>" \
  --domain "<Domain>" \
  --logo "researches/<topic_slug>/assets/<logo>.png" \
  --report "researches/<topic_slug>/report/<report>.md" \
  --presentation "researches/<topic_slug>/presentation/<deck>.md" \
  --output-dir "researches/<topic_slug>/agent_system_output" \
  --formats "pptx,pdf,docx"
```

---

## 10. Visual Diagrams & Flowcharts Mandate (Strict Ban on ASCII/Text Diagrams)
- **Zero ASCII Art**: NEVER use ASCII art, unicode box-drawing characters (`│`, `┌─┐`, `└─┘`, `├──`, `└──`), or vertical arrows (`▼`, `▲`, `►`, `|`) inside code blocks or plaintext to illustrate a process, flowchart, decision tree, or architecture.
- **Mandatory Mermaid Formatting**: ALWAYS produce real visual diagrams using **Mermaid (` ```mermaid `)**.
- **Semantic Palette Tokens**: Flowcharts must include standardized semantic `classDef` tokens (`startEnd`, `process`, `decision`, `successNode`, `rejectNode`).
- **Vector PDF & Word Delivery**: In PDF, Mermaid diagrams are automatically compiled via the Headless Chromium pipeline into crisp vector SVGs inside styled `.mermaid-card` containers with page-break avoidance. In Word, diagrams are formatted in executive styled cards via `add_mermaid_block`.

