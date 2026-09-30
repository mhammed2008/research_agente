"""Core orchestration and state models for the Research Agent System."""

from .state import (
    ResearchPhase,
    SourceTier,
    FactVerificationItem,
    SlideLayoutSpec,
    AuditFeedback,
    ColorPalette,
    ResearchState,
)
from .orchestrator import ResearchOrchestrator

__all__ = [
    "ResearchPhase",
    "SourceTier",
    "FactVerificationItem",
    "SlideLayoutSpec",
    "AuditFeedback",
    "ColorPalette",
    "ResearchState",
    "ResearchOrchestrator",
]
