"""Specialized autonomous agents for the Research Agent System."""

from .investigator import FactInvestigatorAgent
from .template_researcher import DomainTemplateResearcherAgent
from .designer import PresentationArchitectAgent
from .compiler import DocumentCompilerAgent
from .auditor import VisualCriticAgent

__all__ = [
    "FactInvestigatorAgent",
    "DomainTemplateResearcherAgent",
    "PresentationArchitectAgent",
    "DocumentCompilerAgent",
    "VisualCriticAgent",
]
