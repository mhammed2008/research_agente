# Visual Styling & Document Aesthetics Guide

This guide details the aesthetic standards enforced by the PDF and Word exporters in the `professional-researcher` skill.

---

## 🎨 Color Palette Tokens

| Token Name | Hex Code | Purpose | Platypus Usage | Word (.docx) Usage |
|---|---|---|---|---|
| **Primary Navy** | `#0F172A` | Covers, H1 titles, Table Headers | `colors.HexColor("#0F172A")` | `RGBColor(15, 23, 42)` |
| **Accent Royal Blue** | `#2563EB` | Accent bars, H2 subtitles, Badges | `colors.HexColor("#2563EB")` | `RGBColor(37, 99, 235)` |
| **Secondary Slate** | `#334155` | H3 headings, Subtitles | `colors.HexColor("#334155")` | `RGBColor(51, 65, 85)` |
| **Body Charcoal** | `#1E293B` | Body paragraphs, bullet text | `colors.HexColor("#1E293B")` | `RGBColor(30, 41, 59)` |
| **Muted Slate** | `#64748B` | Running headers/footers, metadata labels | `colors.HexColor("#64748B")` | `RGBColor(100, 116, 139)` |
| **Light Slate Fill** | `#F8FAFC` | Zebra table rows, Callout backgrounds | `colors.HexColor("#F8FAFC")` | `w:shd w:fill="F8FAFC"` |
| **Border Gray** | `#E2E8F0` | Table grid borders, dividers | `colors.HexColor("#E2E8F0")` | `w:tcBorders w:color="E2E8F0"` |

---

## 📑 Callout Box Taxonomy

| Callout Tag | Border Accent | Background Tint | Meaning & Intended Use |
|---|---|---|---|
| `> [!NOTE]` | Blue `#2563EB` | Tint `#EFF6FF` | Essential background context or non-obvious operational realities. |
| `> [!TIP]` | Emerald `#059669` | Tint `#ECFDF5` | Strategic efficiency recommendations, cost savings, best practices. |
| `> [!IMPORTANT]` | Rose `#DC2626` | Tint `#FEF2F2` | Regulatory mandates, security prerequisites, critical decisions. |
| `> [!WARNING]` | Amber `#D97706` | Tint `#FFFBEB` | Strategic hazards, breaking changes, vendor traps, security risks. |

---

## 📊 Table Design Rules

1. **Header Row**:
   - Background fill `#0F172A`
   - High-contrast bold white text
   - Configured to repeat across pages on page overflow (`repeatRows=1` in PDF, `w:tblHeader` in Word).
2. **Body Cells**:
   - Wrapped in flowable Paragraphs so text dynamically wraps without clipping.
   - Alternating zebra row backgrounds (`#F8FAFC` vs `#FFFFFF`).
   - Padding: 5pt top/bottom, 6pt left/right minimum.
   - Subtle 0.5pt border `#E2E8F0`.
