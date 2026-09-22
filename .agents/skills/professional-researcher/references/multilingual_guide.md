# Multilingual & Universal Script Publishing Guide

This guide explains how the `professional-researcher` skill processes multilingual text, Unicode font embedding, and Bidirectional (RTL) scripts in PDF and Microsoft Word (.docx).

---

## 1. Supported Languages & Scripts

The rendering pipeline supports:
- **Latin & Extended Latin**: English, French, German, Spanish, Portuguese, Italian, Turkish, Polish, Vietnamese, etc.
- **Semitic / RTL**: Arabic (العربية), Persian/Farsi (فارسی), Hebrew (עברית), Urdu (اردو).
- **Cyrillic**: Russian, Ukrainian, Bulgarian, Serbian.
- **Greek**: Modern Greek.
- **CJK**: Chinese, Japanese, Korean (via Windows Unicode font fallback).

---

## 2. Arabic & RTL Processing Mechanics

### PDF Rendering (ReportLab Platypus)
1. **Font Registration**: Automatically detects and registers system Unicode TrueType fonts (`Arial`, `Segoe UI`, `Tahoma`).
2. **Contextual Character Reshaping**: Arabic letters change shape depending on their position (isolated, initial, medial, final). The pipeline applies `arabic_reshaper.reshape()` before layout.
3. **BiDi Reordering**: The Unicode Bidirectional Algorithm (`bidi.algorithm.get_display()`) transforms logical character order to visual display order.
4. **HTML Tag Preservation**: Inline formatting tags (`<b>`, `<i>`, `<font>`) are preserved across the reshaping and BiDi passes.
5. **Alignment**: Automatically sets paragraph alignment to `RIGHT` (2) when RTL characters are detected.

### Word Document (.docx) Rendering (`python-docx`)
1. **Paragraph BiDi**: Injects `<w:bidi/>` into paragraph properties (`pPr`).
2. **Character Run RTL**: Injects `<w:rtl/>` into run properties (`rPr`).
3. **Complex Script Font**: Configures `<w:rFonts w:cs="Arial"/>` for smooth glyph rendering in Microsoft Word.
4. **Table & Callout Mirroring**: Mirrors cell borders so the colored accent bar appears on the right edge.

---

## 3. Testing Multilingual Generation

To verify multilingual generation:
```bash
python skills/professional-researcher/scripts/export_engine.py \
  --input skills/professional-researcher/examples/sample_arabic_research.md \
  --pdf test_arabic.pdf \
  --docx test_arabic.docx
```
