"""
State definitions and data models for the Autonomous Research Agent System.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
import json


class ResearchPhase(str, Enum):
    INTAKE = "INTAKE"
    DECOMPOSITION = "DECOMPOSITION"
    INVESTIGATION = "INVESTIGATION"
    DESIGN = "DESIGN"
    COMPILATION = "COMPILATION"
    AUDIT = "AUDIT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SourceTier(str, Enum):
    TIER_1_PRIMARY = "TIER_1_PRIMARY"        # ISO, PCI, IEEE, NIST, Official SDKs/RFCs (95-100%)
    TIER_2_SECONDARY = "TIER_2_SECONDARY"    # Peer-reviewed papers, Gartner, Reuters, Tech Telemetry (85-94%)
    TIER_3_CAUTIONARY = "TIER_3_CAUTIONARY"  # Marketing blogs, unverified articles (<75%)


@dataclass
class FactVerificationItem:
    claim: str
    sources: List[str] = field(default_factory=list)
    tier: SourceTier = SourceTier.TIER_2_SECONDARY
    confidence_score: float = 0.85
    is_corroborated: bool = False
    verification_notes: str = ""

    def validate_gate(self) -> bool:
        """Enforces ≥90% accuracy gate for high-confidence quantitative claims."""
        if len(self.sources) >= 2 and self.tier in [SourceTier.TIER_1_PRIMARY, SourceTier.TIER_2_SECONDARY]:
            self.is_corroborated = True
            self.confidence_score = max(self.confidence_score, 0.95)
        elif self.tier == SourceTier.TIER_1_PRIMARY:
            self.is_corroborated = True
            self.confidence_score = max(self.confidence_score, 0.92)
        else:
            self.is_corroborated = False
        return self.is_corroborated


@dataclass
class SlideLayoutSpec:
    title: str
    layout: str = "content"  # split-hero, versus, architecture, timeline, grid, metrics, table, etc.
    category: Optional[str] = None
    subtitle: Optional[str] = None
    content_blocks: List[Any] = field(default_factory=list)
    custom_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ColorPalette:
    primary: str = "#0F172A"       # Obsidian / Deep Slate
    accent: str = "#E8A828"        # Brand Accent Gold
    secondary: str = "#334155"
    bg_light: str = "#0A0F1D"      # Dark or light canvas
    card_bg: str = "#151E2E"
    card_border: str = "#2A3854"
    text_color: str = "#F8FAFC"
    muted_text: str = "#94A3B8"
    is_dark: bool = True
    derived_from_logo: bool = False


@dataclass
class AuditFeedback:
    slide_index: int
    layout_type: str
    status: str = "PASS"  # PASS, WARNING, DEFECT
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    preview_image_path: Optional[str] = None


@dataclass
class DomainTemplate:
    domain: str
    benchmark_sources: List[str] = field(default_factory=list)
    narrative_flow: List[Dict[str, str]] = field(default_factory=list)
    recommended_archetype: str = "minimal_editorial"
    card_framing: str = "frameless"
    design_directives: List[str] = field(default_factory=list)
    typography_guide: Dict[str, str] = field(default_factory=dict)
    key_metrics_style: str = "oversized_typographic"
    search_queries_used: List[str] = field(default_factory=list)


@dataclass
class ResearchState:
    session_id: str
    topic: str
    domain: str = "General"
    archetype: str = "modern_dark"
    phase: ResearchPhase = ResearchPhase.INTAKE
    logo_path: Optional[str] = None
    palette: ColorPalette = field(default_factory=ColorPalette)
    domain_template: Optional[DomainTemplate] = None
    hypotheses: List[str] = field(default_factory=list)
    facts: List[FactVerificationItem] = field(default_factory=list)
    slides: List[SlideLayoutSpec] = field(default_factory=list)
    report_markdown: str = ""
    presentation_markdown: str = ""
    output_dir: str = "researches/output"
    generated_files: Dict[str, str] = field(default_factory=dict)
    audit_results: List[AuditFeedback] = field(default_factory=list)
    history_log: List[str] = field(default_factory=list)

    def log(self, message: str):
        self.history_log.append(message)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)
