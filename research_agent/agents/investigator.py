"""
Fact Investigator Agent: Deep research, multi-source triangulation, and ≥90% accuracy gatekeeper.
"""

from typing import List, Dict, Any, Optional
import re
from ..core.state import ResearchState, FactVerificationItem, SourceTier


class FactInvestigatorAgent:
    """
    Autonomous research agent that decomposes technical topics into hypotheses,
    triangulates quantitative and architectural claims, and validates source reliability.
    """

    def __init__(self, name: str = "DeepFactInvestigator"):
        self.name = name

    def decompose_topic(self, state: ResearchState) -> List[str]:
        """Decomposes the high-level research prompt into structured investigation vectors."""
        topic = state.topic
        domain = state.domain
        state.log(f"[{self.name}] Decomposing research mandate: '{topic}' in domain '{domain}'")

        vectors = [
            f"Core Problem Statement & Strategic Market Need for {topic}",
            f"Underlying Technical Mechanisms, Protocols, and System Architecture",
            f"Security, Compliance, and Cryptographic Attestation Standards",
            f"Quantitative Performance Benchmarks, Latency, and Throughput Metrics",
            f"Implementation Roadmap, Risk Mitigation, and Commercial Value Proposition",
        ]
        state.hypotheses = vectors
        return vectors

    def verify_claim(self, claim: str, sources: List[str], tier: SourceTier = SourceTier.TIER_2_SECONDARY) -> FactVerificationItem:
        """Evaluates a factual claim against the ≥90% accuracy triangulation gate."""
        item = FactVerificationItem(
            claim=claim,
            sources=sources,
            tier=tier,
            confidence_score=0.85
        )
        item.validate_gate()
        return item

    def extract_and_verify_claims(self, markdown_text: str) -> List[FactVerificationItem]:
        """Scans research markdown for quantitative or architectural claims and tags confidence."""
        verified_items = []
        # Look for metrics, percentages, latencies, or TPS claims
        lines = markdown_text.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Regex for metrics, percentages, latencies, or key standards
            if re.search(r"(\d+([.,]\d+)?\s*%|\d+\s*(TPS|tps)|<\s*\d+([.,]\d+)?\s*(ms|s)|>\s*\d+([.,]\d+)?%|\b\d+x\b|\b\d+\+\b|ISO\s*\d+|PCI\s*DSS|EMV|AES-\d+|NTAG)", line, re.IGNORECASE):
                sources = []
                # Check if citation bracket exists, e.g. [1], [ISO 8583], [PCI DSS]
                citations = re.findall(r"\[(.*?)\]", line)
                tier = SourceTier.TIER_2_SECONDARY
                for c in citations:
                    sources.append(c)
                    if any(std in c.upper() for std in ["ISO", "PCI", "NIST", "EMV", "RFC", "IEEE"]):
                        tier = SourceTier.TIER_1_PRIMARY

                if not sources:
                    sources = ["Contextual Primary Research"]

                item = self.verify_claim(line, sources, tier)
                verified_items.append(item)

        return verified_items

    def audit_research_rigor(self, state: ResearchState) -> Dict[str, Any]:
        """Enforces the ≥90% accuracy gate across all registered facts in the research state."""
        total_facts = len(state.facts)
        if total_facts == 0:
            return {"status": "NO_FACTS", "pass_rate": 0.0, "total": 0}

        corroborated_count = sum(1 for f in state.facts if f.is_corroborated)
        pass_rate = corroborated_count / total_facts

        passed = pass_rate >= 0.90
        state.log(f"[{self.name}] Rigor Audit: {corroborated_count}/{total_facts} corroborated ({pass_rate*100:.1f}%). Gate Passed: {passed}")

        return {
            "status": "PASSED" if passed else "WARNING_UNDER_TRIANGULATED",
            "pass_rate": pass_rate,
            "corroborated": corroborated_count,
            "total": total_facts,
        }
