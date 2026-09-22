# Rigorous Research Protocol & Fact-Verification Standards (≥90% Accuracy Gate)

This document establishes the binding methodological requirements for conducting high-rigor, autonomous research using the `professional-researcher` skill.

---

## 1. The 3-Tier Source Reliability Hierarchy

Every piece of data, technical metric, pricing schedule, or architectural requirement gathered from the internet must be categorized into one of three source tiers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 1: Primary Authoritative Standards (Reliability 95% - 100%)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Formal International Standards Bodies: ISO, PCI-SSC, IEEE, IETF RFCs,    │
│    NIST, ITU, 3GPP.                                                         │
│  • Regulatory & Central Bank Mandates: SEC 10-K/10-Q, Federal Reserve, EBA, │
│    Saudi Central Bank (SAMA), Central Bank of Egypt, UAE Central Bank.       │
│  • Primary Developer & Architecture Documentation: Official vendor docs     │
│    (e.g., Apple Developer, Android Source / AOSP, Stripe Docs, AWS Well-    │
│    Architected Framework).                                                  │
│  • Official Hardware Component Datasheets: Direct OEM chip manuals (NXP,    │
│    Broadcom, Qualcomm, STMicroelectronics).                                 │
│  • Primary Code Repositories: Official signed GitHub/GitLab releases,      │
│    kernel commit histories, formal security audit reports.                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  TIER 2: Reputable Secondary Analysis (Reliability 85% - 94%)               │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Established Industry Benchmark & Research Firms: Gartner, Forrester,    │
│    IDC, McKinsey, Boston Consulting Group.                                  │
│  • Peer-Reviewed Scientific & Engineering Literature: ACM, IEEE Xplore,     │
│    Springer, arXiv (verified submissions).                                  │
│  • Established Technical & Business Journalism: Ars Technica, Reuters,      │
│    Bloomberg, Financial Times, The Register.                                │
│  • Verified Production Telemetry: Direct test-bench logs, open-source        │
│    benchmark harnesses.                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  TIER 3: Promotional & Uncorroborated Content (Reliability < 75%)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Vendor Marketing & Sales Landing Pages (often quote theoretical bests).  │
│  • Sponsored Content & Affiliate Review Blogs.                              │
│  • Anonymous Forums, Reddit, Social Media anecdotes.                        │
│  • AI-Generated SEO Summaries & Content Farm Listicles.                      │
│  ==> MANDATE: Tier 3 sources MUST NEVER be cited as proof without           │
│      independent corroboration from a Tier 1 or Tier 2 source.              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mandatory 2-Source Triangulation Rule

No empirical claim, technical metric, or cost estimate may be asserted as fact unless verified by **at least two independent sources**:

1. **Numerical Metrics (Latency, Throughput, Memory, Power, Cost)**:
   - Must cross-corroborate vendor datasheets against independent third-party benchmarks or developer telemetry.
2. **Security & Regulatory Compliance**:
   - Must verify certification status directly on the regulatory body's active registry (e.g. PCI-SSC PTS Approved Devices list, EMVCo Approved Contactless Terminal list) rather than taking the vendor's marketing claim.
3. **Discrepancy Resolution Protocol**:
   - If sources disagree, do NOT pick one arbitrarily or take a naive mathematical average.
   - Explicitly document the variance:
     > *"Vendor marketing documents claim a maximum throughput of 1,200 TPS; however, independent laboratory stress tests under mutual TLS and AES-GCM record sustainable production throughput at 480 to 620 TPS."*

---

## 3. Data Confidence Rating Tags

All substantive sections, comparison tables, and key findings must include an explicit confidence indicator:

| Tag | Meaning | Threshold Criteria |
|---|---|---|
| `🟢 [VERIFIED: HIGH CONFIDENCE]` | Verified factual data (≥ 90%) | Backed by Tier 1 primary sources or 2+ independent benchmarks. |
| `🟡 [PROVISIONAL: MEDIUM CONFIDENCE]` | Probable estimate (75% - 89%) | Derived from reputable Tier 2 secondary sources, awaiting direct physical audit. |
| `🔴 [UNVERIFIED / CONTESTED]` | Low certainty (< 75%) | Conflicting claims, single vendor marketing statement, or pending regulatory review. |

---

## 4. Universal Multi-Domain Search Operators

When investigating any topic across diverse fields:

1. **Hardware / Component Level**:
   ```
   "[Chipset Model]" ("datasheet" OR "pinout" OR "block diagram" OR "errata") filetype:pdf
   ```
2. **Security & Cryptography**:
   ```
   "[Protocol Name]" ("CVE" OR "vulnerability" OR "side-channel" OR "attestation" OR "audit report")
   ```
3. **Regulatory & Standards**:
   ```
   "[Standard Name]" ("PCI" OR "ISO" OR "EMVCo" OR "NIST" OR "RFC") "specification"
   ```
4. **Economics & SaaS/FinTech Pricing**:
   ```
   "[Vendor/Product]" ("interchange" OR "basis points" OR "fee schedule" OR "pricing model")
   ```

---

## 5. Zero Hallucination Safeguard

If a parameter or specification cannot be verified to at least a 75% confidence level, the agent must **never guess or fabricate values**. It must explicitly state:
- *"Unpublished by OEM / Proprietary"*
- *"Pending independent hardware teardown"*
- *"Estimated range based on analogous implementations: [Range] (Confidence: Medium)"*
