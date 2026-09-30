#!/usr/bin/env python3
"""
Autonomous Research & Presentation Agent System CLI (`run_agent.py`).
Unified entry point for multi-agent research orchestration, domain-adaptive design,
multi-format compilation, and multimodal visual critique.
"""

import argparse
import sys
import os
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from research_agent.core.orchestrator import ResearchOrchestrator
from research_agent.core.state import ResearchPhase


def print_banner():
    banner = r"""
  ╔═══════════════════════════════════════════════════════════════════╗
  ║   RESEARCH_AGENTE : AUTONOMOUS MULTI-AGENT SYSTEM (v3.0)          ║
  ║   Deep Research • Fact Gate • Dynamic Design • Multimodal Vision  ║
  ╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="Autonomous Research & Presentation Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("topic", nargs="?", default="Autonomous Enterprise Research", help="Research mandate or presentation topic")
    parser.add_argument("--domain", "-d", default="General", help="Industry domain (e.g. FinTech, CyberSecurity, BioTech)")
    parser.add_argument("--archetype", "-a", choices=["modern_dark", "consulting_grid", "minimal_editorial", "warm_organic", "vibrant_bold"], help="Structural design archetype")
    parser.add_argument("--logo", "-l", help="Path to brand logo image (PNG/JPG/SVG)")
    parser.add_argument("--report", "-r", help="Path to research report markdown file")
    parser.add_argument("--presentation", "-p", help="Path to presentation deck markdown file")
    parser.add_argument("--output-dir", "-o", default="researches/output", help="Directory where artifacts and previews will be saved")
    parser.add_argument("--formats", "-f", default="pptx,pdf,docx", help="Comma-separated formats to compile: pptx,pdf,docx")
    parser.add_argument("--no-render", action="store_true", help="Skip rendering slide PNG previews via PowerPoint COM")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive intake session")

    args = parser.parse_args()

    formats = [fmt.strip().lower() for fmt in args.formats.split(",") if fmt.strip()]

    print(f"[*] Mandate: {args.topic}")
    print(f"[*] Domain: {args.domain}")
    if args.logo:
        print(f"[*] Brand Logo: {args.logo}")
    print(f"[*] Output Directory: {args.output_dir}")
    print(f"[*] Target Formats: {', '.join(formats).upper()}\n")

    orchestrator = ResearchOrchestrator()

    try:
        state = orchestrator.run_pipeline(
            topic=args.topic,
            domain=args.domain,
            archetype=args.archetype,
            logo_path=args.logo,
            report_markdown_path=args.report,
            presentation_markdown_path=args.presentation,
            output_dir=args.output_dir,
            formats=formats,
            render_visual_previews=not args.no_render
        )

        print("\n" + "=" * 65)
        print(f"  PIPELINE EXECUTION STATUS: {state.phase.value}")
        print("=" * 65)
        print(f"• Research Hypotheses: {len(state.hypotheses)}")
        print(f"• Facts Evaluated: {len(state.facts)}")
        if state.domain_template:
            print(f"• Discovered Domain Template: '{state.domain_template.domain}'")
            print(f"• Domain Benchmark Decks: {', '.join(state.domain_template.benchmark_sources[:2])}")
            print(f"• Template Style: Archetype='{state.domain_template.recommended_archetype}', Framing='{state.domain_template.card_framing}'")
        print(f"• Brand Primary Color: {state.palette.primary} (From Logo: {state.palette.derived_from_logo})")
        print(f"• Brand Accent Color: {state.palette.accent}")
        print(f"• Slide Deck Plan: {len(state.slides)} slides composed across {len(set(s.layout for s in state.slides))} layouts")
        print(f"• Visual Quality Audits: {len(state.audit_results)} slides checked")

        print("\nAgent Pipeline Execution Log:")
        for log_line in state.history_log:
            print(f"  {log_line}")

        print("\nGenerated Deliverables:")
        for key, path in state.generated_files.items():
            print(f"  ✔ [{key.upper()}]: {path}")

        print("\n[✓] Agent System run completed successfully.")
        return 0

    except Exception as e:
        print(f"\n[!] Pipeline Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
