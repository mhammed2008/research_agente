"""
Master Orchestrator for the Autonomous Research Agent System.
Drives the 5-phase multi-agent pipeline and enforces rigor and visual quality gates.
"""

from typing import Dict, Any, Optional, List
import uuid
import os
from pathlib import Path

from .state import ResearchState, ResearchPhase, ColorPalette
from ..agents.investigator import FactInvestigatorAgent
from ..agents.template_researcher import DomainTemplateResearcherAgent
from ..agents.designer import PresentationArchitectAgent
from ..agents.compiler import DocumentCompilerAgent
from ..agents.auditor import VisualCriticAgent


class ResearchOrchestrator:
    """
    Master agent that directs specialized subagents through the research,
    design, compilation, and visual verification lifecycle.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.investigator = FactInvestigatorAgent()
        self.template_researcher = DomainTemplateResearcherAgent()
        self.designer = PresentationArchitectAgent()
        self.compiler = DocumentCompilerAgent()
        self.auditor = VisualCriticAgent()

    def run_pipeline(
        self,
        topic: str,
        domain: str = "General",
        archetype: Optional[str] = None,
        logo_path: Optional[str] = None,
        report_markdown_path: Optional[str] = None,
        presentation_markdown_path: Optional[str] = None,
        output_dir: str = "researches/output",
        formats: Optional[List[str]] = None,
        render_visual_previews: bool = True
    ) -> ResearchState:
        """
        Executes the autonomous end-to-end research and presentation generation pipeline.
        """
        formats = formats or ["pptx", "pdf", "docx"]

        # Initialize State
        state = ResearchState(
            session_id=self.session_id,
            topic=topic,
            domain=domain,
            archetype=archetype or self.designer.map_domain_archetype(domain),
            logo_path=logo_path,
            output_dir=output_dir,
            phase=ResearchPhase.INTAKE
        )
        state.log(f"[Orchestrator] Session initialized: {self.session_id} for '{topic}'")

        # ----------------------------------------------------
        # Phase 1: Problem Decomposition
        # ----------------------------------------------------
        state.phase = ResearchPhase.DECOMPOSITION
        state.log(f"[Orchestrator] Phase 1 -> Decomposing research vectors...")
        self.investigator.decompose_topic(state)

        # ----------------------------------------------------
        # Phase 2: Fact Investigation & Triangulation Gate
        # ----------------------------------------------------
        state.phase = ResearchPhase.INVESTIGATION
        state.log(f"[Orchestrator] Phase 2 -> Fact verification and triangulation...")
        if report_markdown_path and os.path.exists(report_markdown_path):
            with open(report_markdown_path, "r", encoding="utf-8") as f:
                content = f.read()
                state.report_markdown = content
                state.facts = self.investigator.extract_and_verify_claims(content)
                self.investigator.audit_research_rigor(state)

        # ----------------------------------------------------
        # Phase 3: Domain Template Discovery & Visual Identity Architecture
        # ----------------------------------------------------
        state.phase = ResearchPhase.DESIGN
        state.log(f"[Orchestrator] Phase 3 -> Domain template discovery & visual identity synthesis...")
        self.template_researcher.research_domain_templates(state)
        self.designer.resolve_branding_and_palette(state)
        self.designer.compose_dynamic_slide_deck_architecture(state)

        # ----------------------------------------------------
        # Phase 4: Multi-Format Document Compilation
        # ----------------------------------------------------
        state.phase = ResearchPhase.COMPILATION
        state.log(f"[Orchestrator] Phase 4 -> Compiling deliverables...")
        self.compiler.compile_deliverables(
            state=state,
            report_markdown_path=report_markdown_path,
            presentation_markdown_path=presentation_markdown_path,
            formats=formats
        )

        # ----------------------------------------------------
        # Phase 5: Multimodal Visual Audit
        # ----------------------------------------------------
        state.phase = ResearchPhase.AUDIT
        state.log(f"[Orchestrator] Phase 5 -> Multimodal visual inspection & quality gate...")
        slide_previews = []
        pptx_path = state.generated_files.get("presentation_pptx")
        if render_visual_previews and pptx_path and os.path.exists(pptx_path):
            state.log(f"[Orchestrator] Rendering slide previews via PowerPoint COM...")
            preview_dir = str(Path(state.output_dir) / "slides_preview")
            slide_previews = self.auditor.render_slide_previews(pptx_path, preview_dir)

        self.auditor.audit_slide_layouts(state, slide_previews)

        # ----------------------------------------------------
        # Phase 6: Completion
        # ----------------------------------------------------
        state.phase = ResearchPhase.COMPLETED
        state.log(f"[Orchestrator] Pipeline completed successfully. Artifacts ready in: {state.output_dir}")

        return state
