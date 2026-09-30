# Visual Styling & Document Aesthetics Guide

This guide details the aesthetic standards enforced by the PDF, Word, and PowerPoint exporters in the `professional-researcher` skill.

---

## 🎨 Dynamic Styling & Color Palette Tokens

Visual styling is fully customizable and **not hardcoded**. The system supports dynamic overrides via CLI (`--primary-color`, `--accent-color`), style configurations (`--style`), or frontmatter `branding:`.

### Curated Palette Presets

| Preset Name | Primary Hex | Accent Hex | Best Suited For |
|---|---|---|---|
| `corporate-navy` (Default) | `#0F172A` | `#2563EB` | Executive whitepapers, banking, institutional reports |
| `fintech-emerald` | `#064E3B` | `#059669` | Payments, blockchain, sustainability, modern fintech |
| `minimal-slate` | `#0F172A` | `#475569` | Developer blueprints, systems engineering, specifications |
| `executive-crimson` | `#881337` | `#E11D48` | Defense, critical audits, aerospace, luxury leadership |
| `luxury-violet` | `#4C1D95` | `#7C3AED` | Advanced AI research, creative computing, venture capital |

---

## 🖼️ Custom Brand Logo Specifications

Brand logos are automatically scaled and embedded across all deliverable formats:

1. **PDF Cover Page**:
   - Position: Placed prominently above the accent color rule.
   - Max bounds: 180pt width × 60pt height (aspect ratio strictly preserved).
   - Spacing: Dynamically shrinks following vertical spacer to prevent cover overflow.
2. **Word (`.docx`) Cover Page**:
   - Position: Centered above document title block.
   - Max bounds: 2.2 inches width.
3. **PowerPoint (`.pptx`) Slides**:
   - **Title Slide**: Displayed in upper branding zone (width: 2.2 inches). Coordinates mirror automatically in Arabic RTL mode.
   - **Content Slides**: Crisp header badge logo (width: 1.0 inch) positioned in the upper right (or upper left in RTL) for consistent organizational identity.

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
   - Background fill dynamically matches `primary_color` (or preset).
   - High-contrast bold white text.
   - Configured to repeat across pages on page overflow (`repeatRows=1` in PDF, `w:tblHeader` in Word).
2. **Body Cells**:
   - Wrapped in flowable Paragraphs so text dynamically wraps without clipping.
   - Alternating zebra row backgrounds (`#F8FAFC` vs `#FFFFFF`).
   - Padding: 5pt top/bottom, 6pt left/right minimum.
   - Subtle 0.5pt border `#E2E8F0`.

