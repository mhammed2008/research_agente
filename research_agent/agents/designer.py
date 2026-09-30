"""
Presentation Architect Agent: Creative direction, brand color synthesis, and dynamic layout architecture.
"""

from typing import List, Dict, Any, Optional
import os
import sys
from pathlib import Path

# Add skills/professional-researcher/scripts to path if needed for color_synthesizer
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "skills" / "professional-researcher" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from color_synthesizer import synthesize_palette
except ImportError:
    synthesize_palette = None

from ..core.state import ResearchState, ColorPalette, SlideLayoutSpec


class PresentationArchitectAgent:
    """
    Autonomous visual designer and slide architect.
    Derives authentic brand palettes from logos and structures slides into domain-adaptive layouts.
    """

    def __init__(self, name: str = "PresentationArchitect"):
        self.name = name

    def resolve_branding_and_palette(self, state: ResearchState) -> ColorPalette:
        """Derives the exact brand color palette from a logo or structural archetype."""
        state.log(f"[{self.name}] Synthesizing brand visual identity...")

        # 1. Logo Priority Extraction
        if state.logo_path and os.path.exists(state.logo_path) and synthesize_palette:
            state.log(f"[{self.name}] Extracting brand colors directly from logo: '{state.logo_path}'")
            try:
                raw_pal = synthesize_palette(
                    logo_path=state.logo_path,
                    archetype=state.archetype
                )
                palette = ColorPalette(
                    primary=raw_pal.get("primary_hex") or raw_pal.get("primary", "#0A0F1D"),
                    accent=raw_pal.get("accent_hex") or raw_pal.get("accent", "#E8A828"),
                    secondary=raw_pal.get("secondary_hex") or raw_pal.get("secondary", "#334155"),
                    bg_light=raw_pal.get("bg_light_hex") or raw_pal.get("bg_light", "#0A0F1D"),
                    card_bg=raw_pal.get("card_bg_hex") or raw_pal.get("card_bg", "#151E2E"),
                    card_border=raw_pal.get("card_border_hex") or raw_pal.get("card_border", "#2A3854"),
                    text_color=raw_pal.get("body_hex") or raw_pal.get("body", "#F8FAFC"),
                    muted_text=raw_pal.get("muted_hex") or raw_pal.get("muted", "#94A3B8"),
                    is_dark=raw_pal.get("is_dark", True),
                    derived_from_logo=True
                )
                state.palette = palette
                state.log(f"[{self.name}] Derived Palette -> Primary: {palette.primary}, Accent: {palette.accent}, Dark: {palette.is_dark}")
                return palette
            except Exception as e:
                state.log(f"[{self.name}] Warning: Logo extraction failed ({e}), using archetype palette.")

        # 2. Archetype Mapping Fallback
        archetype_map = {
            "modern_dark": ColorPalette(primary="#0A0F1D", accent="#E8A828", bg_light="#0A0F1D", card_bg="#151E2E", card_border="#2A3854", is_dark=True),
            "consulting_grid": ColorPalette(primary="#0F172A", accent="#2563EB", bg_light="#F8FAFC", card_bg="#FFFFFF", card_border="#E2E8F0", text_color="#1E293B", muted_text="#64748B", is_dark=False),
            "minimal_editorial": ColorPalette(primary="#111827", accent="#000000", bg_light="#FFFFFF", card_bg="#FFFFFF", card_border="#F3F4F6", text_color="#111827", muted_text="#4B5563", is_dark=False),
            "warm_organic": ColorPalette(primary="#1C2D27", accent="#059669", bg_light="#FBF9F4", card_bg="#FFFFFF", card_border="#E5E7EB", text_color="#1C2D27", muted_text="#6B7280", is_dark=False),
            "vibrant_bold": ColorPalette(primary="#0F172A", accent="#F43F5E", bg_light="#0F172A", card_bg="#1E293B", card_border="#334155", is_dark=True),
        }

        palette = archetype_map.get(state.archetype, archetype_map["modern_dark"])
        state.palette = palette
        state.log(f"[{self.name}] Applied Archetype '{state.archetype}' -> Primary: {palette.primary}, Accent: {palette.accent}")
        return palette

    def map_domain_archetype(self, domain: str) -> str:
        """Selects the optimal presentation design archetype based on domain expectations."""
        d_lower = domain.lower()
        if any(w in d_lower for w in ["fintech", "payment", "crypto", "web3", "ai", "cloud", "security"]):
            return "modern_dark"
        elif any(w in d_lower for w in ["luxury", "editorial", "architecture", "fashion", "legal"]):
            return "minimal_editorial"
        elif any(w in d_lower for w in ["banking", "consulting", "governance", "m&a", "corporate"]):
            return "consulting_grid"
        elif any(w in d_lower for w in ["health", "animal", "rescue", "ngo", "nature", "sustainability"]):
            return "warm_organic"
        elif any(w in d_lower for w in ["pitch", "seed", "marketing", "launch", "consumer"]):
            return "vibrant_bold"
        return "modern_dark"

    def compose_dynamic_slide_deck_architecture(self, state: ResearchState) -> List[SlideLayoutSpec]:
        """
        Dynamically sequences slide structures based on the discovered domain template
        to guarantee industry authenticity and prevent repetitive 'card-box' monotony.
        """
        state.log(f"[{self.name}] Synthesizing bespoke presentation architecture...")

        # If a domain template was discovered, derive the deck structure from its narrative flow
        if state.domain_template and state.domain_template.narrative_flow:
            deck_plan = []
            for item in state.domain_template.narrative_flow:
                layout = item.get("layout", "content")
                role = item.get("role", "Slide")
                focus = item.get("focus", "")
                title = state.topic if layout == "title" else f"{role}: {focus}" if focus else role
                deck_plan.append(
                    SlideLayoutSpec(
                        title=title,
                        layout=layout,
                        category=role,
                        subtitle=focus
                    )
                )
            state.slides = deck_plan
            state.log(f"[{self.name}] Applied Domain Template '{state.domain_template.domain}' -> Composed {len(deck_plan)} slides across {len(set(s.layout for s in deck_plan))} layout paradigms.")
            return deck_plan
        
        # Strategic fallback narrative sequence with diverse layout paradigms
        deck_plan = [
            SlideLayoutSpec(title=state.topic, layout="title", category="Cover"),
            SlideLayoutSpec(title="Strategic Executive Agenda", layout="split-hero", category="Overview"),
            SlideLayoutSpec(title="Market Disruption: Legacy Challenges vs. Strategic Innovation", layout="versus", category="Market Dynamics"),
            SlideLayoutSpec(title="Target System & Operational Architecture", layout="architecture", category="Architecture"),
            SlideLayoutSpec(title="Core Technical Thesis & Security Paradigm", layout="callout", category="Security"),
            SlideLayoutSpec(title="End-to-End Operational Execution Pipeline", layout="timeline", category="Process Flow"),
            SlideLayoutSpec(title="Multi-Layered Defense & Feature Matrix", layout="grid", category="Technical Pillars"),
            SlideLayoutSpec(title="Dual Acceptance Architecture & Integration Modes", layout="two-column", category="Integration"),
            SlideLayoutSpec(title="Quantitative Performance Benchmarks & KPIs", layout="metrics", category="Telemetry"),
            SlideLayoutSpec(title="Ecosystem Infrastructure & Hardware Rollout", layout="grid", category="Infrastructure"),
            SlideLayoutSpec(title="Comparative Competitive Benchmark", layout="table", category="Benchmark"),
            SlideLayoutSpec(title="Horizontal Phased Rollout Roadmap", layout="timeline", category="Roadmap"),
            SlideLayoutSpec(title="Executive Partnership Next Steps", layout="closing", category="Conclusion"),
        ]

        state.slides = deck_plan
        state.log(f"[{self.name}] Composed {len(deck_plan)} slides across {len(set(s.layout for s in deck_plan))} distinct layout paradigms.")
        return deck_plan
