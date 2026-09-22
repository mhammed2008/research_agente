"""
PDF Report Generator using ReportLab Platypus (v2.0).
Generates executive-grade research reports with:
- Multilingual & Universal Character Support (English, Arabic, Cyrillic, Turkish, CJK, etc.)
- Automatic RTL (Right-to-Left) detection, character reshaping, and BiDi reordering
- Cross-platform font registration (Windows, macOS, Linux)
- Dedicated modern cover page with metadata block
- Auto-generated Table of Contents
- Two-pass canvas for dynamic 'Page X of Y' running headers & footers
- Styled typography hierarchy (Title, Subtitle, H1-H3, Body, Code)
- Professional callout boxes (Note, Important, Tip, Warning)
- Blockquote rendering with gray accent bar
- Auto-wrapped, zebra-striped data comparison tables
- Nested bullet support with indent levels
- Embedded images with captions
- Orphan heading prevention (keepWithNext)
"""

import os
import re
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
    Preformatted,
    Image as RLImage,
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Multilingual / Arabic & BiDi support
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_BIDI = True
except ImportError:
    HAS_BIDI = False

# Image support
try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# Register Universal Unicode TrueType Fonts from Windows, macOS, or Linux
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

def init_unicode_fonts():
    global FONT_REGULAR, FONT_BOLD
    font_candidates = [
        # Windows
        ("C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\arialbd.ttf", "ArialUnicode", "ArialUnicode-Bold"),
        ("C:\\Windows\\Fonts\\segoeui.ttf", "C:\\Windows\\Fonts\\segoeuib.ttf", "SegoeUIUnicode", "SegoeUIUnicode-Bold"),
        ("C:\\Windows\\Fonts\\tahoma.ttf", "C:\\Windows\\Fonts\\tahomabd.ttf", "TahomaUnicode", "TahomaUnicode-Bold"),
        # macOS
        ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "ArialUnicode", "ArialUnicode-Bold"),
        ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf", "ArialUnicode", "ArialUnicode-Bold"),
        ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Helvetica.ttc", "HelveticaSys", "HelveticaSys-Bold"),
        # Linux (Liberation Sans is metrically compatible with Arial)
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "LiberationSans", "LiberationSans-Bold"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans", "DejaVuSans-Bold"),
        ("/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", "DejaVuSans", "DejaVuSans-Bold"),
    ]
    for reg_path, bold_path, reg_name, bold_name in font_candidates:
        if os.path.exists(reg_path) and os.path.exists(bold_path):
            try:
                pdfmetrics.registerFont(TTFont(reg_name, reg_path))
                pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                FONT_REGULAR = reg_name
                FONT_BOLD = bold_name
                return
            except Exception:
                continue

    # Fallback warning
    print("[WARN] No Unicode TrueType fonts found — falling back to Helvetica. "
          "Arabic/CJK text may not render correctly.", file=sys.stderr)

init_unicode_fonts()


RTL_REGEX = re.compile(r'[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')

def is_rtl_text(text):
    """Detects if text contains Arabic, Hebrew, or other RTL characters."""
    if not isinstance(text, str):
        return False
    return bool(RTL_REGEX.search(text))

def process_text_for_pdf(text):
    """
    Applies Arabic reshaping and BiDi reordering for RTL text if available,
    while preserving inline HTML formatting tags (<b>, <i>, <font>).
    """
    if not isinstance(text, str) or not HAS_BIDI:
        return text

    if not is_rtl_text(text):
        return text

    # Extract HTML tags to preserve them through reshaping
    tag_pattern = re.compile(r'(<[^>]+>)')
    parts = tag_pattern.split(text)
    processed_parts = []

    for part in parts:
        if part.startswith('<') and part.endswith('>'):
            processed_parts.append(part)
        elif part:
            try:
                reshaped = arabic_reshaper.reshape(part)
                bidi_part = get_display(reshaped)
                processed_parts.append(bidi_part)
            except Exception:
                processed_parts.append(part)

    return "".join(processed_parts)


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that dynamically calculates total page count
    and prints running header and 'Page X of Y' footer on pages > 1.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return

        self.saveState()
        page_w, page_h = self._pagesize

        header_title = getattr(self, "doc_title", "RESEARCH REPORT")
        is_rtl = is_rtl_text(header_title)
        display_title = process_text_for_pdf(header_title)

        self.setFont(FONT_BOLD, 8)
        self.setFillColor(colors.HexColor("#64748B"))

        if is_rtl:
            self.drawRightString(page_w - 54, page_h - 36, display_title)
        else:
            self.drawString(54, page_h - 36, display_title.upper())

        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, page_h - 42, page_w - 54, page_h - 42)

        # Running Footer
        self.line(54, 45, page_w - 54, 45)
        self.setFont(FONT_REGULAR, 8)
        self.setFillColor(colors.HexColor("#94A3B8"))

        notice = "CONFIDENTIAL & PROPRIETARY — FOR AUTHORIZED USE ONLY"
        self.drawString(54, 32, notice)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(page_w - 54, 32, page_str)
        self.restoreState()


class PDFReportBuilder:
    def __init__(self, filename, title="Research Report", subtitle="", author="", organization="", date_str="", pagesize=A4):
        self.filename = filename
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.organization = organization
        self.date_str = date_str
        self.pagesize = pagesize

        self.is_rtl_doc = is_rtl_text(title) or is_rtl_text(subtitle) or is_rtl_text(author)

        self.margin = 54
        self.page_width, self.page_height = pagesize
        self.usable_width = self.page_width - 2 * self.margin

        # Theme Colors
        self.color_primary = colors.HexColor("#0F172A")    # Deep Navy
        self.color_accent = colors.HexColor("#2563EB")     # Royal Blue
        self.color_secondary = colors.HexColor("#334155")  # Slate
        self.color_body = colors.HexColor("#1E293B")       # Dark Charcoal
        self.color_light_bg = colors.HexColor("#F8FAFC")   # Slate-50
        self.color_border = colors.HexColor("#E2E8F0")     # Slate-200

        self.styles = self._create_styles()
        self.story = []

    def _create_styles(self):
        styles = getSampleStyleSheet()
        align_default = 2 if self.is_rtl_doc else 0  # 2 is RIGHT, 0 is LEFT

        styles.add(ParagraphStyle(
            "CoverBadge",
            parent=styles["Normal"],
            fontName=FONT_BOLD,
            fontSize=9,
            leading=12,
            textColor=self.color_accent,
            alignment=align_default,
            spaceAfter=12,
        ))

        styles.add(ParagraphStyle(
            "CoverTitle",
            parent=styles["Title"],
            fontName=FONT_BOLD,
            fontSize=26,
            leading=32,
            textColor=self.color_primary,
            alignment=align_default,
            spaceAfter=10,
        ))

        styles.add(ParagraphStyle(
            "CoverSubtitle",
            parent=styles["Normal"],
            fontName=FONT_REGULAR,
            fontSize=13,
            leading=18,
            textColor=self.color_secondary,
            alignment=align_default,
            spaceAfter=24,
        ))

        styles.add(ParagraphStyle(
            "CoverMetaLabel",
            parent=styles["Normal"],
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=12,
            alignment=align_default,
            textColor=colors.HexColor("#64748B"),
        ))

        styles.add(ParagraphStyle(
            "CoverMetaVal",
            parent=styles["Normal"],
            fontName=FONT_REGULAR,
            fontSize=9.5,
            leading=13,
            alignment=align_default,
            textColor=self.color_primary,
        ))

        styles.add(ParagraphStyle(
            "ExecHeading1",
            parent=styles["Heading1"],
            fontName=FONT_BOLD,
            fontSize=16,
            leading=20,
            textColor=self.color_primary,
            alignment=align_default,
            spaceBefore=18,
            spaceAfter=8,
            keepWithNext=True,
        ))

        styles.add(ParagraphStyle(
            "ExecHeading2",
            parent=styles["Heading2"],
            fontName=FONT_BOLD,
            fontSize=12.5,
            leading=16,
            textColor=self.color_accent,
            alignment=align_default,
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True,
        ))

        styles.add(ParagraphStyle(
            "ExecHeading3",
            parent=styles["Heading3"],
            fontName=FONT_BOLD,
            fontSize=10.5,
            leading=14,
            textColor=self.color_secondary,
            alignment=align_default,
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True,
        ))

        styles["BodyText"].fontName = FONT_REGULAR
        styles["BodyText"].fontSize = 9.5
        styles["BodyText"].leading = 14
        styles["BodyText"].textColor = self.color_body
        styles["BodyText"].alignment = align_default
        styles["BodyText"].spaceAfter = 8

        styles.add(ParagraphStyle(
            "BulletItem",
            parent=styles["BodyText"],
            leftIndent=0 if self.is_rtl_doc else 14,
            rightIndent=14 if self.is_rtl_doc else 0,
            firstLineIndent=0,
            alignment=align_default,
            spaceAfter=4,
        ))

        styles.add(ParagraphStyle(
            "CalloutText",
            parent=styles["BodyText"],
            fontSize=9,
            leading=13.5,
            textColor=colors.HexColor("#1E293B"),
            alignment=align_default,
            spaceAfter=0,
        ))

        styles.add(ParagraphStyle(
            "CalloutTitle",
            parent=styles["Normal"],
            fontName=FONT_BOLD,
            fontSize=9.5,
            leading=13,
            alignment=align_default,
            textColor=self.color_primary,
            spaceAfter=4,
        ))

        styles.add(ParagraphStyle(
            "CodeInline",
            parent=styles["Normal"],
            fontName="Courier",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#0F172A"),
        ))

        styles.add(ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8.5,
            leading=11.5,
            alignment=align_default,
            textColor=self.color_body,
        ))

        styles.add(ParagraphStyle(
            "TableCellHeader",
            parent=styles["Normal"],
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=11.5,
            alignment=align_default,
            textColor=colors.white,
        ))

        # v2.0: Blockquote style
        styles.add(ParagraphStyle(
            "BlockquoteText",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#475569"),
            fontName=FONT_REGULAR,
            alignment=align_default,
            spaceAfter=0,
        ))

        # v2.0: TOC styles
        styles.add(ParagraphStyle(
            "TOCTitle",
            parent=styles["Title"],
            fontName=FONT_BOLD,
            fontSize=18,
            leading=24,
            textColor=self.color_primary,
            alignment=align_default,
            spaceAfter=16,
        ))

        styles.add(ParagraphStyle(
            "TOCH1",
            parent=styles["Normal"],
            fontName=FONT_BOLD,
            fontSize=10,
            leading=16,
            textColor=self.color_primary,
            alignment=align_default,
            leftIndent=0 if not self.is_rtl_doc else 0,
            spaceAfter=2,
        ))

        styles.add(ParagraphStyle(
            "TOCH2",
            parent=styles["Normal"],
            fontName=FONT_REGULAR,
            fontSize=9.5,
            leading=15,
            textColor=self.color_accent,
            alignment=align_default,
            leftIndent=14 if not self.is_rtl_doc else 0,
            rightIndent=14 if self.is_rtl_doc else 0,
            spaceAfter=2,
        ))

        styles.add(ParagraphStyle(
            "TOCH3",
            parent=styles["Normal"],
            fontName=FONT_REGULAR,
            fontSize=9,
            leading=14,
            textColor=self.color_secondary,
            alignment=align_default,
            leftIndent=28 if not self.is_rtl_doc else 0,
            rightIndent=28 if self.is_rtl_doc else 0,
            spaceAfter=2,
        ))

        # v2.0: Image caption style
        styles.add(ParagraphStyle(
            "ImageCaption",
            parent=styles["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#64748B"),
            alignment=1,  # CENTER
            spaceAfter=12,
        ))

        return styles

    def build_cover_page(self):
        # Top Accent Bar
        self.story.append(HRFlowable(
            width="100%",
            thickness=5,
            color=self.color_accent,
            spaceAfter=30,
            hAlign="RIGHT" if self.is_rtl_doc else "LEFT"
        ))

        badge_text = "تقرير بحثي أمني وتقني استراتيجي" if self.is_rtl_doc else "STRATEGIC RESEARCH & TECHNICAL EVALUATION"
        self.story.append(Paragraph(process_text_for_pdf(badge_text), self.styles["CoverBadge"]))

        self.story.append(Paragraph(process_text_for_pdf(self.title), self.styles["CoverTitle"]))
        if self.subtitle:
            self.story.append(Paragraph(process_text_for_pdf(self.subtitle), self.styles["CoverSubtitle"]))

        # Divider
        self.story.append(HRFlowable(
            width="100%",
            thickness=1,
            color=self.color_border,
            spaceBefore=10,
            spaceAfter=35,
            hAlign="RIGHT" if self.is_rtl_doc else "LEFT"
        ))

        self.story.append(Spacer(1, 140))

        # Metadata Table
        meta_data = []
        lbl_prepared = "إعداد الباحث" if self.is_rtl_doc else "PREPARED BY"
        lbl_org = "الجهة أو المنظمة" if self.is_rtl_doc else "ORGANIZATION"
        lbl_date = "تاريخ التقرير" if self.is_rtl_doc else "DATE OF REPORT"
        lbl_class = "مستوى السرية" if self.is_rtl_doc else "CLASSIFICATION"
        val_class = "سري للغاية / مراجعة تنفيذية" if self.is_rtl_doc else "Confidential / Executive Review"

        if self.author:
            meta_data.append([
                Paragraph(process_text_for_pdf(lbl_prepared), self.styles["CoverMetaLabel"]),
                Paragraph(process_text_for_pdf(self.author), self.styles["CoverMetaVal"])
            ])
        if self.organization:
            meta_data.append([
                Paragraph(process_text_for_pdf(lbl_org), self.styles["CoverMetaLabel"]),
                Paragraph(process_text_for_pdf(self.organization), self.styles["CoverMetaVal"])
            ])
        if self.date_str:
            meta_data.append([
                Paragraph(process_text_for_pdf(lbl_date), self.styles["CoverMetaLabel"]),
                Paragraph(process_text_for_pdf(self.date_str), self.styles["CoverMetaVal"])
            ])
        meta_data.append([
            Paragraph(process_text_for_pdf(lbl_class), self.styles["CoverMetaLabel"]),
            Paragraph(process_text_for_pdf(val_class), self.styles["CoverMetaVal"])
        ])

        col_widths = [130, self.usable_width - 130] if not self.is_rtl_doc else [self.usable_width - 130, 130]
        t = Table(meta_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
        ]))
        self.story.append(t)
        self.story.append(PageBreak())

    def add_table_of_contents(self, blocks, doc_title=""):
        """Generates a styled Table of Contents page from heading blocks (H1, H2, H3)."""
        headings = [blk for blk in blocks if blk["type"] == "heading" and blk.get("level", 1) <= 3]

        # Filter out the document title heading
        if doc_title:
            headings = [h for h in headings if h["text"].strip().lower() != doc_title.strip().lower()]

        if not headings:
            return

        toc_title = "المحتويات" if self.is_rtl_doc else "TABLE OF CONTENTS"
        self.story.append(Paragraph(process_text_for_pdf(toc_title), self.styles["TOCTitle"]))
        self.story.append(HRFlowable(
            width="100%", thickness=1, color=self.color_accent,
            spaceAfter=14, hAlign="RIGHT" if self.is_rtl_doc else "LEFT"
        ))

        for h in headings:
            level = h.get("level", 1)
            style_key = {1: "TOCH1", 2: "TOCH2", 3: "TOCH3"}.get(level, "TOCH3")
            text = process_text_for_pdf(h["text"])
            self.story.append(Paragraph(text, self.styles[style_key]))

        self.story.append(Spacer(1, 8))
        self.story.append(PageBreak())

    def add_heading(self, text, level=1):
        style_key = {
            1: "ExecHeading1",
            2: "ExecHeading2",
            3: "ExecHeading3",
        }.get(level, "ExecHeading3")

        processed = process_text_for_pdf(text)
        p = Paragraph(processed, self.styles[style_key])
        self.story.append(p)

    def add_paragraph(self, text):
        processed = process_text_for_pdf(text)
        p = Paragraph(processed, self.styles["BodyText"])
        self.story.append(p)

    def add_bullet(self, text, indent=0):
        processed = process_text_for_pdf(text)
        bullet_symbol = "&bull; &nbsp; " if not self.is_rtl_doc else " &nbsp; &bull;"

        # Calculate indent offset
        indent_offset = indent * 18  # 18pt per indent level

        # Create inline style with dynamic indent
        style = ParagraphStyle(
            f"BulletIndent{indent}",
            parent=self.styles["BulletItem"],
            leftIndent=(0 if self.is_rtl_doc else 14) + (0 if self.is_rtl_doc else indent_offset),
            rightIndent=(14 if self.is_rtl_doc else 0) + (indent_offset if self.is_rtl_doc else 0),
        )

        bullet_text = f"{bullet_symbol}{processed}" if not self.is_rtl_doc else f"{processed}{bullet_symbol}"
        p = Paragraph(bullet_text, style)
        self.story.append(p)

    def add_callout(self, text, title="KEY INSIGHT", callout_type="note"):
        type_palette = {
            "note": {"accent": "#2563EB", "bg": "#EFF6FF", "title": "#1D4ED8"},
            "warning": {"accent": "#D97706", "bg": "#FFFBEB", "title": "#B45309"},
            "important": {"accent": "#DC2626", "bg": "#FEF2F2", "title": "#B91C1C"},
            "tip": {"accent": "#059669", "bg": "#ECFDF5", "title": "#047857"},
        }
        cfg = type_palette.get(callout_type, type_palette["note"])
        accent_color = colors.HexColor(cfg["accent"])
        bg_color = colors.HexColor(cfg["bg"])

        title_style = ParagraphStyle(
            f"CalloutHead_{callout_type}",
            parent=self.styles["CalloutTitle"],
            textColor=colors.HexColor(cfg["title"]),
        )

        flowables = [
            Paragraph(f"<b>{process_text_for_pdf(title.upper())}</b>", title_style),
            Paragraph(process_text_for_pdf(text), self.styles["CalloutText"]),
        ]

        border_side = ("LINERIGHT", (0, 0), (-1, -1), 3.5, accent_color) if self.is_rtl_doc else ("LINELEFT", (0, 0), (-1, -1), 3.5, accent_color)

        t = Table([[flowables]], colWidths=[self.usable_width])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg_color),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            border_side,
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))

        self.story.append(Spacer(1, 4))
        self.story.append(t)
        self.story.append(Spacer(1, 8))

    def add_blockquote(self, text):
        """Renders a plain blockquote with a gray left accent bar and light background."""
        accent_color = colors.HexColor("#94A3B8")  # Slate-400
        bg_color = self.color_light_bg

        flowables = [
            Paragraph(process_text_for_pdf(text), self.styles["BlockquoteText"]),
        ]

        border_side = ("LINERIGHT", (0, 0), (-1, -1), 3, accent_color) if self.is_rtl_doc else ("LINELEFT", (0, 0), (-1, -1), 3, accent_color)

        t = Table([[flowables]], colWidths=[self.usable_width])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg_color),
            border_side,
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))

        self.story.append(Spacer(1, 4))
        self.story.append(t)
        self.story.append(Spacer(1, 6))

    def add_image(self, path, alt=""):
        """Embeds an image with optional caption. Gracefully skips if file not found."""
        if not os.path.exists(path):
            # Render a placeholder paragraph instead of crashing
            self.story.append(Paragraph(
                f'<i>[Image not found: {alt or path}]</i>',
                self.styles["ImageCaption"]
            ))
            return

        try:
            # Calculate dimensions preserving aspect ratio
            max_width = self.usable_width * 0.85
            max_height = 300  # max height in points

            if HAS_PIL:
                with PILImage.open(path) as img:
                    img_w, img_h = img.size
                    aspect = img_h / img_w
                    display_width = min(max_width, img_w)
                    display_height = display_width * aspect
                    if display_height > max_height:
                        display_height = max_height
                        display_width = display_height / aspect
            else:
                display_width = max_width
                display_height = None  # let ReportLab figure it out

            img = RLImage(path, width=display_width, height=display_height)
            self.story.append(Spacer(1, 6))
            self.story.append(img)

            if alt:
                self.story.append(Paragraph(
                    process_text_for_pdf(alt),
                    self.styles["ImageCaption"]
                ))
            self.story.append(Spacer(1, 6))
        except Exception as e:
            self.story.append(Paragraph(
                f'<i>[Error loading image: {e}]</i>',
                self.styles["ImageCaption"]
            ))

    def add_table(self, headers, rows, col_widths=None):
        table_data = []

        header_row = [Paragraph(f"<b>{process_text_for_pdf(h)}</b>", self.styles["TableCellHeader"]) for h in headers]
        table_data.append(header_row)

        for r in rows:
            row_cells = [Paragraph(process_text_for_pdf(str(cell)), self.styles["TableCell"]) for cell in r]
            table_data.append(row_cells)

        num_cols = len(headers)
        if not col_widths:
            col_width = self.usable_width / num_cols
            col_widths = [col_width] * num_cols

        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        align_str = "RIGHT" if self.is_rtl_doc else "LEFT"
        t_style = [
            ("BACKGROUND", (0, 0), (-1, 0), self.color_primary),
            ("ALIGN", (0, 0), (-1, -1), align_str),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, self.color_border),
        ]

        for i in range(1, len(table_data)):
            if i % 2 == 0:
                t_style.append(("BACKGROUND", (0, i), (-1, i), self.color_light_bg))

        t.setStyle(TableStyle(t_style))
        self.story.append(Spacer(1, 4))
        self.story.append(t)
        self.story.append(Spacer(1, 8))

    def add_code_block(self, code_text):
        lines = code_text.strip().split("\n")
        CHUNK_SIZE = 30
        for chunk_start in range(0, len(lines), CHUNK_SIZE):
            chunk_lines = lines[chunk_start:chunk_start + CHUNK_SIZE]
            safe_code = "\n".join(chunk_lines)
            p = Preformatted(
                safe_code,
                self.styles["CodeInline"],
                maxLineLength=85
            )
            t = Table([[p]], colWidths=[self.usable_width])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            self.story.append(Spacer(1, 3))
            self.story.append(t)
            self.story.append(Spacer(1, 4))

    def add_horizontal_rule(self):
        self.story.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=self.color_border,
            spaceBefore=8,
            spaceAfter=8,
        ))

    def save(self):
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=self.pagesize,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
        )

        def canvas_maker(*args, **kwargs):
            c = NumberedCanvas(*args, **kwargs)
            c.doc_title = self.title
            return c

        doc.build(self.story, canvasmaker=canvas_maker)
        return self.filename
