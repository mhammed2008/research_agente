"""
Comprehensive test suite for the Autonomous Research & Presentation Agent System.
Tests state machine transitions, multi-agent role handoffs, fact triangulation,
brand color extraction priority, and visual quality auditing.
"""

import pytest
import os
import json
from pathlib import Path

from research_agent.core.state import (
    ResearchState,
    ResearchPhase,
    FactVerificationItem,
    SourceTier,
    SlideLayoutSpec,
    ColorPalette,
    AuditFeedback,
)
from research_agent.agents.investigator import FactInvestigatorAgent
from research_agent.agents.designer import PresentationArchitectAgent
from research_agent.agents.compiler import DocumentCompilerAgent
from research_agent.agents.auditor import VisualCriticAgent
from research_agent.core.orchestrator import ResearchOrchestrator


class TestStateModels:
    def test_research_state_initialization(self):
        state = ResearchState(session_id="test-123", topic="Quantum Cryptography in Banking")
        assert state.session_id == "test-123"
        assert state.phase == ResearchPhase.INTAKE
        assert state.domain == "General"
        state.log("Initialized test state")
        assert len(state.history_log) == 1

    def test_state_json_serialization(self):
        state = ResearchState(session_id="test-456", topic="NFC Payments")
        json_str = state.to_json()
        data = json.loads(json_str)
        assert data["session_id"] == "test-456"
        assert data["phase"] == "INTAKE"

    def test_fact_verification_gate(self):
        # Claim with only 1 source should fail ≥90% gate
        f1 = FactVerificationItem(claim="TPS is 50,000", sources=["Vendor Brochure"], tier=SourceTier.TIER_3_CAUTIONARY)
        assert not f1.validate_gate()
        assert not f1.is_corroborated

        # Claim with 2 independent sources should pass
        f2 = FactVerificationItem(
            claim="NTAG 424 DNA supports AES-128 CMAC",
            sources=["NXP AN12196 Datasheet", "ISO/IEC 7816-4 Specification"],
            tier=SourceTier.TIER_1_PRIMARY
        )
        assert f2.validate_gate()
        assert f2.is_corroborated
        assert f2.confidence_score >= 0.90


class TestFactInvestigatorAgent:
    def setup_method(self):
        self.investigator = FactInvestigatorAgent()

    def test_topic_decomposition(self):
        state = ResearchState(session_id="test-vec", topic="Offline CBDC Protocols", domain="FinTech")
        vectors = self.investigator.decompose_topic(state)
        assert len(vectors) == 5
        assert any("Technical Mechanisms" in v for v in vectors)
        assert len(state.hypotheses) == 5

    def test_claim_extraction_and_triangulation(self):
        sample_md = """
        The core engine processes up to 15000 TPS with <0.3s latency [ISO 8583] [PCI DSS].
        Under heavy load, system uptime exceeds >99.9% across distributed nodes.
        Unrelated narrative line without quantitative numbers.
        """
        facts = self.investigator.extract_and_verify_claims(sample_md)
        assert len(facts) >= 2
        # Verify ISO 8583 claim got marked as Tier 1 Primary and corroborated
        iso_fact = next(f for f in facts if "15000 TPS" in f.claim)
        assert iso_fact.tier == SourceTier.TIER_1_PRIMARY
        assert iso_fact.is_corroborated

    def test_rigor_audit_gate(self):
        state = ResearchState(session_id="test-rigor", topic="Payment Gateways")
        state.facts = [
            FactVerificationItem(claim="Fact 1", sources=["S1", "S2"], tier=SourceTier.TIER_1_PRIMARY, is_corroborated=True),
            FactVerificationItem(claim="Fact 2", sources=["S3", "S4"], tier=SourceTier.TIER_2_SECONDARY, is_corroborated=True),
        ]
        audit = self.investigator.audit_research_rigor(state)
        assert audit["status"] == "PASSED"
        assert audit["pass_rate"] == 1.0


class TestPresentationArchitectAgent:
    def setup_method(self):
        self.architect = PresentationArchitectAgent()

    def test_domain_archetype_mapping(self):
        assert self.architect.map_domain_archetype("FinTech Payments") == "modern_dark"
        assert self.architect.map_domain_archetype("Luxury Fashion Brand") == "minimal_editorial"
        assert self.architect.map_domain_archetype("Corporate Governance & M&A") == "consulting_grid"
        assert self.architect.map_domain_archetype("Animal Rescue & Wildlife") == "warm_organic"
        assert self.architect.map_domain_archetype("Seed Stage Pitch Deck") == "vibrant_bold"

    def test_logo_color_extraction_priority(self):
        logo_path = os.path.abspath("researches/jaib_nfc_partnership_proposal/assets/teknokeys_logo.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.abspath("jaib_nfc_partnership_proposal/assets/teknokeys_logo.png")
        state = ResearchState(
            session_id="test-logo",
            topic="TeknoKeys NFC",
            logo_path=logo_path if os.path.exists(logo_path) else None
        )
        pal = self.architect.resolve_branding_and_palette(state)
        if os.path.exists(logo_path):
            assert pal.derived_from_logo
            # Should have extracted real gold accent (not default blue)
            assert pal.accent.upper().startswith("#E8") or pal.accent.upper().startswith("#F") or pal.accent.upper().startswith("#D")

    def test_dynamic_layout_architecture_composition(self):
        state = ResearchState(session_id="test-arch", topic="Autonomous Payments")
        slides = self.architect.compose_dynamic_slide_deck_architecture(state)
        assert len(slides) >= 10
        layouts = [s.layout for s in slides]
        # Must contain diverse layouts, NOT all content
        assert "split-hero" in layouts
        assert "versus" in layouts
        assert "architecture" in layouts
        assert "timeline" in layouts
        assert "grid" in layouts
        assert "metrics" in layouts


class TestVisualCriticAgent:
    def setup_method(self):
        self.critic = VisualCriticAgent()

    def test_audit_slide_layouts_detects_risk(self):
        state = ResearchState(session_id="test-audit", topic="Audit Test")
        state.slides = [
            SlideLayoutSpec(title="Short Title", layout="title"),
            SlideLayoutSpec(title="A" * 120, layout="versus"),  # Very long title should trigger warning
            SlideLayoutSpec(title="Roadmap", layout="timeline"),
        ]
        feedbacks = self.critic.audit_slide_layouts(state)
        assert len(feedbacks) == 3
        # Slide 2 should have WARNING for title length
        assert feedbacks[1].status == "WARNING"
        assert any("title exceeds" in issue.lower() for issue in feedbacks[1].issues)


class TestDomainTemplateResearcherAgent:
    def setup_method(self):
        from research_agent.agents.template_researcher import DomainTemplateResearcherAgent
        self.researcher = DomainTemplateResearcherAgent()

    def test_fintech_template_discovery(self):
        state = ResearchState(session_id="test-tpl-fintech", topic="Jaib NFC Contactless", domain="FinTech NFC Contactless Payments")
        template = self.researcher.research_domain_templates(state)
        assert template.domain == "FinTech NFC & Payment Systems"
        assert len(template.benchmark_sources) >= 4
        assert any("Stripe" in s for s in template.benchmark_sources)
        assert any("Square" in s for s in template.benchmark_sources)
        assert any("SoftPOS" in s for s in template.benchmark_sources)
        assert template.recommended_archetype == "modern_dark"
        assert template.card_framing == "cards"
        assert len(template.narrative_flow) >= 10
        assert state.domain_template is not None
        assert state.archetype == "modern_dark"

    def test_cybersecurity_template_discovery(self):
        state = ResearchState(session_id="test-tpl-sec", topic="Zero Trust Edge", domain="CyberSecurity Zero Trust")
        template = self.researcher.research_domain_templates(state)
        assert template.domain == "CyberSecurity & Cloud Infrastructure"
        assert any("CrowdStrike" in s for s in template.benchmark_sources)
        assert template.recommended_archetype == "modern_dark"

    def test_architect_uses_discovered_domain_template(self):
        state = ResearchState(session_id="test-tpl-arch", topic="Mobile Tap-to-Pay", domain="FinTech Payments")
        self.researcher.research_domain_templates(state)
        architect = PresentationArchitectAgent()
        deck = architect.compose_dynamic_slide_deck_architecture(state)
        assert len(deck) == len(state.domain_template.narrative_flow)
        layouts = [s.layout for s in deck]
        assert "split-hero" in layouts
        assert "versus" in layouts
        assert "metrics" in layouts
        assert "grid" in layouts
        assert "timeline" in layouts


class TestFullAgentOrchestrator:
    def test_end_to_end_pipeline_execution(self):
        orchestrator = ResearchOrchestrator(session_id="test-e2e")
        state = orchestrator.run_pipeline(
            topic="AI Agentic Payment Gateways",
            domain="FinTech",
            report_markdown_path=None,
            presentation_markdown_path=None,
            output_dir="scratch/test_agent_output",
            formats=["pptx"],
            render_visual_previews=False
        )
        assert state.phase == ResearchPhase.COMPLETED
        assert state.domain_template is not None
        assert len(state.hypotheses) == 5
        assert len(state.slides) >= 10
        assert len(state.audit_results) >= 10
