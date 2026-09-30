"""
Document Compiler Agent: Code generation, formatting, and multi-format publication (PDF, DOCX, PPTX).
"""

from typing import Dict, Any, Optional
import os
import sys
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "skills" / "professional-researcher" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from export_engine import convert_file, parse_presentation_slides
    from pptx_builder import PptxReportBuilder
except ImportError as e:
    convert_file = None
    parse_presentation_slides = None
    PptxReportBuilder = None

from ..core.state import ResearchState


class DocumentCompilerAgent:
    """
    Autonomous compiler agent responsible for formatting and producing publication-grade
    PDF reports, Word documents, and PowerPoint slide decks.
    """

    def __init__(self, name: str = "DocumentCompiler"):
        self.name = name

    def compile_deliverables(
        self,
        state: ResearchState,
        report_markdown_path: Optional[str] = None,
        presentation_markdown_path: Optional[str] = None,
        formats: Optional[list] = None
    ) -> Dict[str, str]:
        """
        Compiles the state's markdown sources into publication-grade documents (PDF, DOCX, PPTX).
        """
        formats = formats or ["pptx", "pdf", "docx"]
        out_dir = Path(state.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        state.log(f"[{self.name}] Initiating multi-format publication in: {out_dir}")

        generated = {}

        # 1. Compile Presentation Deck
        if presentation_markdown_path and os.path.exists(presentation_markdown_path):
            state.log(f"[{self.name}] Compiling Presentation Deck from: {presentation_markdown_path}")
            deck_base = out_dir / (Path(presentation_markdown_path).stem)

            pptx_target = str(deck_base) + ".pptx" if "pptx" in formats else None
            pdf_target = str(deck_base) + ".pdf" if "pdf" in formats else None
            docx_target = str(deck_base) + ".docx" if "docx" in formats else None

            if convert_file:
                try:
                    res = convert_file(
                        input_path=presentation_markdown_path,
                        pdf_path=pdf_target,
                        docx_path=docx_target,
                        pptx_path=pptx_target,
                        primary_color=state.palette.primary,
                        accent_color=state.palette.accent,
                        logo_path=state.logo_path,
                        archetype=state.archetype
                    )
                    for fmt, path in res.items():
                        if path and os.path.exists(path):
                            generated[f"presentation_{fmt}"] = path
                            state.log(f"[{self.name}] Generated Presentation [{fmt.upper()}]: {path}")
                except Exception as e:
                    state.log(f"[{self.name}] Error compiling presentation: {e}")

        # 2. Compile Research Report
        if report_markdown_path and os.path.exists(report_markdown_path):
            state.log(f"[{self.name}] Compiling Technical Research Report from: {report_markdown_path}")
            rep_base = out_dir / (Path(report_markdown_path).stem)

            pdf_target = str(rep_base) + ".pdf" if "pdf" in formats else None
            docx_target = str(rep_base) + ".docx" if "docx" in formats else None

            if convert_file:
                try:
                    res = convert_file(
                        input_path=report_markdown_path,
                        pdf_path=pdf_target,
                        docx_path=docx_target,
                        pptx_path=None,
                        primary_color=state.palette.primary,
                        accent_color=state.palette.accent,
                        logo_path=state.logo_path,
                        archetype=state.archetype
                    )
                    for fmt, path in res.items():
                        if path and os.path.exists(path):
                            generated[f"report_{fmt}"] = path
                            state.log(f"[{self.name}] Generated Report [{fmt.upper()}]: {path}")
                except Exception as e:
                    state.log(f"[{self.name}] Error compiling report: {e}")

        state.generated_files = generated
        return generated
