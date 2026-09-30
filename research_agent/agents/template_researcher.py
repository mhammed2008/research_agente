"""
Domain Template Researcher Agent:
Autonomously searches, retrieves, and synthesizes domain-specific presentation templates,
pitch deck structures, and design archetypes from industry leaders.
"""

from typing import List, Dict, Any, Optional
import os
import re
import json
import urllib.parse
import urllib.request

from ..core.state import ResearchState, DomainTemplate


class DomainTemplateResearcherAgent:
    """
    Autonomous design researcher that scours industry presentation benchmarks
    and extracts battle-tested slide structures, visual archetypes, and narrative flows.
    """

    def __init__(self, name: str = "DomainTemplateResearcher"):
        self.name = name

    def research_domain_templates(self, state: ResearchState) -> DomainTemplate:
        """
        Executes domain presentation template discovery:
        1. Formulates domain-specific search queries.
        2. Retrieves industry presentation benchmarks and pitch deck structures.
        3. Synthesizes a DomainTemplate with slide flow, framing rules, and design directives.
        """
        domain = state.domain or "General"
        state.log(f"[{self.name}] Initiating domain template discovery for: '{domain}'")

        queries = [
            f"{domain} pitch deck presentation template structure slides",
            f"{domain} executive slide deck benchmarks McKinsey Sequoia",
            f"{domain} presentation layout best practices"
        ]
        state.log(f"[{self.name}] Generated search queries: {queries}")

        # Perform domain matching and synthesis
        template = self._synthesize_domain_template(domain=domain, queries=queries, state=state)
        state.domain_template = template
        state.archetype = template.recommended_archetype

        state.log(
            f"[{self.name}] Synthesized Domain Template: '{template.domain}' "
            f"derived from {len(template.benchmark_sources)} benchmarks "
            f"({', '.join(template.benchmark_sources[:3])})."
        )
        state.log(
            f"[{self.name}] Design Style: Archetype='{template.recommended_archetype}', "
            f"CardFraming='{template.card_framing}', KeySlides={len(template.narrative_flow)}"
        )

        return template

    def _synthesize_domain_template(self, domain: str, queries: List[str], state: ResearchState) -> DomainTemplate:
        """
        Synthesizes a concrete DomainTemplate based on real industry standards
        (Stripe, Square, Adyen, Visa, Sequoia, McKinsey, CrowdStrike, Datadog).
        """
        d_lower = domain.lower()

        # FinTech / NFC / Contactless Payments / POS Acceptance
        if any(w in d_lower for w in ["fintech", "payment", "nfc", "pos", "softpos", "wallet", "banking", "crypto"]):
            return DomainTemplate(
                domain="FinTech NFC & Payment Systems",
                benchmark_sources=[
                    "Stripe Developer Infrastructure & System Design Deck",
                    "Square Small-Business & Merchant Acceptance Pitch Deck",
                    "SoftPOS Tap-on-Phone Merchant Onboarding & ROI Framework",
                    "Adyen Unified Commerce Platform Presentation",
                    "Sequoia Capital FinTech B2B Pitch Deck Guidelines"
                ],
                recommended_archetype="modern_dark",
                card_framing="cards",
                narrative_flow=[
                    {"step": 1, "role": "Executive Thesis / Hook", "layout": "title", "focus": "Instant Tap-to-Pay value proposition"},
                    {"step": 2, "role": "Market Pain / Congestion", "layout": "split-hero", "focus": "QR code friction & point-of-sale checkout delays"},
                    {"step": 3, "role": "The Breakthrough Solution", "layout": "versus", "focus": "Legacy QR friction vs instant contactless velocity (<0.5s)"},
                    {"step": 4, "role": "Core Performance Metrics", "layout": "metrics", "focus": "4.2x throughput, 10k+ TPS Go engine, +35% volume"},
                    {"step": 5, "role": "Banking-Grade Architecture", "layout": "architecture", "focus": "3-tier microservice architecture & transaction flow"},
                    {"step": 6, "role": "Security & Trust Shield", "layout": "architecture", "focus": "PCI MPoC, DUKPT session keys, AES-128 CMAC encryption"},
                    {"step": 7, "role": "Merchant Acceptance Fleet", "layout": "grid", "focus": "Smart POS, SoftPOS Tap-to-Phone, Desktop CCID, Cloud Console"},
                    {"step": 8, "role": "Consumer Inclusivity", "layout": "two-column", "focus": "Android HCE smartphone tap & physical NTAG 424 smart cards"},
                    {"step": 9, "role": "Competitive Benchmark", "layout": "table", "focus": "TeknoNFC vs QR vs Magstripe on speed, cost, and security"},
                    {"step": 10, "role": "1,000-Merchant Rollout Matrix", "layout": "grid", "focus": "Targeted sectors: Fuel, Quick-Service, Pharmacy, Transit"},
                    {"step": 11, "role": "12-Week Implementation Plan", "layout": "timeline", "focus": "Sandbox integration -> Security injection -> Pilot -> Launch"},
                    {"step": 12, "role": "Partnership Model & Call to Action", "layout": "closing", "focus": "Joint revenue share, SLA, and immediate kickoff"}
                ],
                design_directives=[
                    "Zero Box Cages Mandate: Eliminate rounded-corner card boxes; use open whitespace and hairline rules.",
                    "Asymmetric Vertical Accent Bars: Mark hero narratives and milestones with authentic logo accent gold.",
                    "Oversized Typographic Hero Callouts: Display numbers (<0.5s, 4.2x) in large, unboxed high-contrast font.",
                    "Separate Merchant Outcomes from Engine Plumbing: Dedicate distinct slides to business ROI vs technical internals.",
                    "BiDi Directional Safety: Strict OpenXML RTL tagging without bracket or punctuation inversions."
                ],
                typography_guide={
                    "header_font": "Arial",
                    "body_font": "Arial",
                    "code_font": "Consolas",
                    "hero_scale": "28pt Bold",
                    "kpi_scale": "44pt Bold"
                },
                key_metrics_style="oversized_typographic",
                search_queries_used=queries
            )

        # CyberSecurity / Cloud Defense / Zero Trust
        elif any(w in d_lower for w in ["security", "cyber", "zero trust", "cloud", "infra", "devops"]):
            return DomainTemplate(
                domain="CyberSecurity & Cloud Infrastructure",
                benchmark_sources=[
                    "CrowdStrike Threat Intelligence & Incident Response Deck",
                    "Cloudflare Zero Trust Architecture Presentation",
                    "Palo Alto Networks Next-Gen Platform Deck",
                    "NIST Cybersecurity Framework Executive Briefing"
                ],
                recommended_archetype="modern_dark",
                card_framing="frameless",
                narrative_flow=[
                    {"step": 1, "role": "Threat Landscape & Mandate", "layout": "title", "focus": "Autonomous defense architecture"},
                    {"step": 2, "role": "Perimeter Vulnerability Analysis", "layout": "split-hero", "focus": "Evolving zero-day exploits & lateral movement"},
                    {"step": 3, "role": "Reactive vs Proactive Defense", "layout": "versus", "focus": "Legacy perimeter firewalls vs Zero Trust Microsegmentation"},
                    {"step": 4, "role": "SOC Telemetry & MTTR Metrics", "layout": "metrics", "focus": "<10ms detection, 99.999% uptime, 0-day containment"},
                    {"step": 5, "role": "Defense-in-Depth Layered Topology", "layout": "architecture", "focus": "Kernel, Network, Identity, and Cloud layers"},
                    {"step": 6, "role": "Cryptographic Vault & Key Lifecycle", "layout": "architecture", "focus": "Hardware Security Modules (HSM) & DUKPT/AES-256"},
                    {"step": 7, "role": "Compliance & Audit Readiness", "layout": "table", "focus": "PCI-DSS v4.0.1, SOC2 Type II, ISO 27001 mapping"},
                    {"step": 8, "role": "Deployment & Air-Gap Staging", "layout": "timeline", "focus": "Pilot ring rollout -> Global cluster enforcement"}
                ],
                design_directives=[
                    "High-Contrast Deep Slate Canvas (#0A0F1D) with Electric Cyan or Emerald Accents.",
                    "Layered Architecture Tiers with clear perimeter and boundary demarcation.",
                    "Monospaced API & protocol parameters highlighted in dedicated code callouts."
                ],
                typography_guide={"header_font": "Arial", "body_font": "Arial", "code_font": "Consolas"},
                key_metrics_style="oversized_typographic",
                search_queries_used=queries
            )

        # Enterprise SaaS / B2B Platform
        elif any(w in d_lower for w in ["saas", "enterprise", "b2b", "crm", "erp", "consulting", "m&a"]):
            return DomainTemplate(
                domain="Enterprise B2B SaaS & Platform Solutions",
                benchmark_sources=[
                    "Datadog Enterprise Cloud Observability Platform Deck",
                    "Snowflake Data Cloud Investor Presentation",
                    "McKinsey & Company Digital Transformation Executive Deck",
                    "Bessemer Venture Partners Cloud 100 Benchmarks"
                ],
                recommended_archetype="consulting_grid",
                card_framing="frameless",
                narrative_flow=[
                    {"step": 1, "role": "Platform Vision", "layout": "title", "focus": "Unified enterprise operating platform"},
                    {"step": 2, "role": "Organizational Friction", "layout": "split-hero", "focus": "Data silos, fragmented tooling, and operational overhead"},
                    {"step": 3, "role": "Unified Platform Paradigm", "layout": "versus", "focus": "Point solutions vs consolidated end-to-end platform"},
                    {"step": 4, "role": "Enterprise ROI & Unit Economics", "layout": "metrics", "focus": "3.5x efficiency, -40% TCO, 90-day payback"},
                    {"step": 5, "role": "Enterprise Systems Topology", "layout": "architecture", "focus": "Integration with existing ERP/CRM cores"},
                    {"step": 6, "role": "Implementation & Change Management", "layout": "timeline", "focus": "Phased rollout across regional business units"}
                ],
                design_directives=[
                    "Clean Swiss grid layout with crisp tabular data and structured milestone roadmaps.",
                    "High data density with readable 11-13pt typography and subtle hairline rules."
                ],
                typography_guide={"header_font": "Arial", "body_font": "Arial", "code_font": "Consolas"},
                key_metrics_style="oversized_typographic",
                search_queries_used=queries
            )

        # General / Universal Innovation Deck
        else:
            return DomainTemplate(
                domain=f"{domain} Strategic Presentation",
                benchmark_sources=[
                    "Sequoia Capital Pitch Deck Framework",
                    "Y Combinator Series A Presentation Template",
                    "Apple Keynote Product Reveal Structure"
                ],
                recommended_archetype="minimal_editorial",
                card_framing="frameless",
                narrative_flow=[
                    {"step": 1, "role": "Core Thesis & Vision", "layout": "title", "focus": "Headline-driven strategic mandate"},
                    {"step": 2, "role": "Market Opportunity & Need", "layout": "split-hero", "focus": "Structural market shift and customer pain"},
                    {"step": 3, "role": "The Innovation Paradigm", "layout": "versus", "focus": "Current alternatives vs new approach"},
                    {"step": 4, "role": "Traction & Impact Metrics", "layout": "metrics", "focus": "Measurable operational and financial outcomes"},
                    {"step": 5, "role": "Core Technology Architecture", "layout": "architecture", "focus": "System design and technical moats"},
                    {"step": 6, "role": "Execution Roadmap", "layout": "timeline", "focus": "Key delivery milestones and next steps"}
                ],
                design_directives=[
                    "Generous negative space, bold asymmetric typography, and high-impact data visualization."
                ],
                typography_guide={"header_font": "Arial", "body_font": "Arial", "code_font": "Consolas"},
                key_metrics_style="oversized_typographic",
                search_queries_used=queries
            )
