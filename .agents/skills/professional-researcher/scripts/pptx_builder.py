# pptx_builder.py - State-of-the-Art Executive Presentation Engine (v4.0)
# FinTech & Consulting Grade • 100% Native OpenXML In-Shape Editability • Zero Lockouts
import os
import re
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml import parse_xml

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None

try:
    from .color_synthesizer import synthesize_palette, hex_to_rgb as synth_hex_to_rgb
except ImportError:
    try:
        from color_synthesizer import synthesize_palette, hex_to_rgb as synth_hex_to_rgb
    except ImportError:
        synthesize_palette = None
        synth_hex_to_rgb = None

def is_rtl_text(text):
    if not text:
        return False
    arabic_chars = len(re.findall(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]', text))
    latin_chars = len(re.findall(r'[A-Za-z]', text))
    return arabic_chars > latin_chars

def to_rgb_color(c):
    if isinstance(c, RGBColor):
        return c
    if isinstance(c, str):
        s = c.lstrip('#')
        if len(s) == 6:
            return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
    if isinstance(c, (tuple, list)) and len(c) >= 3:
        return RGBColor(int(c[0]), int(c[1]), int(c[2]))
    return RGBColor(128, 128, 128)

def hex_to_rgb(hex_str):
    return to_rgb_color(hex_str)

def parse_inline_runs(text):
    if not text:
        return []
    pattern = re.compile(r'(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)')
    tokens = pattern.split(text)
    runs = []
    for token in tokens:
        if not token:
            continue
        if token.startswith("`") and token.endswith("`") and len(token) >= 2:
            runs.append({"text": token[1:-1], "bold": False, "italic": False, "code": True})
        elif token.startswith("**") and token.endswith("**") and len(token) >= 4:
            runs.append({"text": token[2:-2], "bold": True, "italic": False, "code": False})
        elif token.startswith("*") and token.endswith("*") and len(token) >= 2:
            runs.append({"text": token[1:-1], "bold": False, "italic": True, "code": False})
        else:
            runs.append({"text": token, "bold": False, "italic": False, "code": False})
    return runs

def bidi_sanitize_rtl_text(text):
    """
    Universal BiDi Sanitizer for Arabic/RTL Presentation Content:
    - Strips leftover raw markdown artifacts (*, _, `)
    - Normalizes spacing between Latin/numbers and Arabic characters
    - Mirrors brackets/parentheses for correct OpenXML RTL display
    """
    if not text:
        return text

    # 1. Clean markdown artifacts if any passed in raw
    text = re.sub(r'[*_`]', '', text)

    # 2. Normalize spaces around Latin / Numbers adjacent to Arabic characters
    ar_range = r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]'
    text = re.sub(rf'([A-Za-z0-9\+\%]+)({ar_range})', r'\1 \2', text)
    text = re.sub(rf'({ar_range})([A-Za-z0-9\+\%]+)', r'\1 \2', text)
    text = re.sub(r'[ \t]+', ' ', text)

    # Brackets are handled natively by OpenXML RTL renderer

    return text

class PptxReportBuilder:
    def __init__(self, filename, title="Research Presentation", subtitle="", author="",
                 organization="", date_str="", theme="slate_consulting",
                 archetype="modern_dark", logo_path=None, font_family=None, style=None, **kwargs):
        self.filename = filename
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.organization = organization
        self.date_str = date_str
        self.archetype = archetype or "modern_dark"
        self.logo_path = logo_path
        self.is_rtl_doc = (
            is_rtl_text(title) or 
            is_rtl_text(subtitle) or 
            is_rtl_text(organization) or 
            is_rtl_text(author) or 
            kwargs.get("is_rtl", False) or
            (isinstance(style, dict) and style.get("is_rtl", False))
        )

        self.prs = Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank_layout = self.prs.slide_layouts[6]
        self.slide_width = self.prs.slide_width
        self.slide_height = self.prs.slide_height
        self.slides = []

        # Color Theme Setup with Explicit Brand Color Support
        branding = kwargs.get("branding") or (style.get("branding") if isinstance(style, dict) else {})
        if not branding and isinstance(style, dict):
            branding = style
        p_hex = kwargs.get("primary_color") or branding.get("primary_color")
        a_hex = kwargs.get("accent_color") or branding.get("accent_color")

        if synthesize_palette:
            self.palette = synthesize_palette(logo_path=self.logo_path, primary_hex=p_hex, accent_hex=a_hex,
                                              archetype=self.archetype, theme_preset=theme if isinstance(theme, str) else None)
            self.theme = {
                "primary": to_rgb_color(self.palette["primary"]),
                "accent": to_rgb_color(self.palette["accent"]),
                "card_bg": to_rgb_color(self.palette.get("card_bg", RGBColor(20, 30, 48))),
                "bg_light": to_rgb_color(self.palette.get("bg_light", RGBColor(10, 15, 29))),
                "body": to_rgb_color(self.palette.get("body", RGBColor(203, 213, 225))),
                "card_border": to_rgb_color(self.palette.get("card_border", RGBColor(30, 41, 59))),
                "text_dark": to_rgb_color(self.palette.get("bg_light") if self.palette.get("is_dark_canvas") else RGBColor(15, 23, 42))
            }
            self.is_dark_canvas = self.palette.get("is_dark_canvas", True)
            if a_hex:
                self.theme["accent"] = to_rgb_color(a_hex)
            if p_hex:
                self.theme["primary"] = to_rgb_color(p_hex)
                if self.is_dark_canvas:
                    self.theme["bg_light"] = to_rgb_color(p_hex)
        else:
            self.is_dark_canvas = True
            self.theme = {
                "primary": RGBColor(10, 15, 29),
                "accent": RGBColor(232, 168, 40),
                "card_bg": RGBColor(20, 30, 48),
                "bg_light": RGBColor(10, 15, 29),
                "body": RGBColor(203, 213, 225),
                "card_border": RGBColor(30, 41, 59),
                "text_dark": RGBColor(10, 15, 29)
            }

        custom_font = font_family or os.environ.get("RESEARCH_AGENT_FONT")
        if custom_font:
            self.font_family = custom_font
        else:
            self.font_family = "Cairo" if self.is_rtl_doc else "Calibri"

    def _apply_paragraph_rtl(self, paragraph, is_rtl=None):
        use_rtl = self.is_rtl_doc if is_rtl is None else is_rtl
        if use_rtl:
            paragraph.alignment = PP_ALIGN.RIGHT
            pPr = paragraph._p.get_or_add_pPr()
            pPr.set("rtl", "1")
        else:
            paragraph.alignment = PP_ALIGN.LEFT

    def _apply_bullet_format(self, paragraph, indent_level=0, color=None, is_rtl=None):
        use_rtl = self.is_rtl_doc if is_rtl is None else is_rtl
        pPr = paragraph._p.get_or_add_pPr()
        if use_rtl:
            pPr.set("rtl", "1")
            paragraph.alignment = PP_ALIGN.RIGHT
        else:
            paragraph.alignment = PP_ALIGN.LEFT

        char_map = {0: "•", 1: "–", 2: "›"}
        bullet_char = char_map.get(indent_level, "•")
        bullet_color = color or self.theme["accent"]
        hex_color = f"{bullet_color[0]:02X}{bullet_color[1]:02X}{bullet_color[2]:02X}"

        pPr.set("marL", str(320000 + indent_level * 240000))
        pPr.set("indent", "-240000")

        clr_xml = f'<a:buClr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:srgbClr val="{hex_color}"/></a:buClr>'
        pPr.append(parse_xml(clr_xml))

        sz_xml = f'<a:buSzPts xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="1100"/>'
        pPr.append(parse_xml(sz_xml))

        font_xml = f'<a:buFont xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{self.font_family}"/>'
        pPr.append(parse_xml(font_xml))

        char_xml = f'<a:buChar xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" char="{bullet_char}"/>'
        pPr.append(parse_xml(char_xml))

    def _add_styled_run(self, paragraph, text, bold=False, italic=False, code=False,
                        color=None, font_size=Pt(14), is_rtl=None):
        run = paragraph.add_run()
        run.text = text
        font_to_use = "Consolas" if code else self.font_family
        run.font.name = font_to_use
        run.font.size = font_size
        run.font.bold = bold
        run.font.italic = italic

        if color:
            run.font.color.rgb = color
        elif code:
            run.font.color.rgb = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        else:
            run.font.color.rgb = self.theme["body"]

        rPr = run._r.get_or_add_rPr()
        for tag in ("ea", "cs"):
            existing = rPr.find(f"{{http://schemas.openxmlformats.org/drawingml/2006/main}}{tag}")
            if existing is not None:
                existing.set("typeface", font_to_use)
            else:
                elem = parse_xml(f'<a:{tag} xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{font_to_use}"/>')
                rPr.append(elem)
        return run

    def _format_paragraph(self, paragraph, text, font_size=Pt(14), bold=False, color=None, is_rtl=None, align=None):
        """Helper to format a paragraph with consistent Cairo font, RTL alignment, and OpenXML tags."""
        paragraph.text = ""
        use_rtl = self.is_rtl_doc if is_rtl is None else is_rtl
        if align is not None:
            paragraph.alignment = align
        elif use_rtl:
            paragraph.alignment = PP_ALIGN.RIGHT
        else:
            paragraph.alignment = PP_ALIGN.LEFT
        if use_rtl:
            pPr = paragraph._p.get_or_add_pPr()
            pPr.set("rtl", "1")
        self._render_inline_text(paragraph, text, default_color=color, default_size=font_size, is_rtl=use_rtl, base_bold=bold)

    def _render_inline_text(self, paragraph, text, default_color=None, default_size=Pt(14),
                            is_rtl=None, base_bold=False):
        use_rtl = self.is_rtl_doc if is_rtl is None else is_rtl
        runs = parse_inline_runs(text)
        for r in runs:
            run_txt = r["text"]
            if use_rtl:
                run_txt = bidi_sanitize_rtl_text(run_txt)
            self._add_styled_run(
                paragraph,
                run_txt,
                bold=base_bold or r["bold"],
                italic=r["italic"],
                code=r["code"],
                color=default_color,
                font_size=default_size,
                is_rtl=use_rtl
            )

    def _create_slide(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self.slides.append(slide)
        self._apply_slide_transition(slide)
        return slide

    def _apply_slide_transition(self, slide, effect="fade", speed="med"):
        try:
            sldPr = slide._element.get_or_add_sldPr()
            trans_xml = f'<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="{speed}"><p:{effect}/></p:transition>'
            sldPr.append(parse_xml(trans_xml))
        except Exception:
            pass

    def _add_slide_background(self, slide, bg_color):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = to_rgb_color(bg_color)

    def _add_header_footer(self, slide, category=None, slide_num=None, total_slides=None):
        is_rtl = self.is_rtl_doc
        m_h = Inches(0.8)

        # Category Tag at Top
        if category:
            cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), self.slide_width - Inches(1.6), Inches(0.4))
            c_tf = cat_box.text_frame
            c_tf.word_wrap = True
            cp = c_tf.paragraphs[0]
            self._format_paragraph(cp, str(category).upper(), font_size=Pt(10), bold=True, color=self.theme["accent"], is_rtl=is_rtl)

        # Brand Logo in Top Corner
        if self.logo_path and os.path.exists(self.logo_path):
            logo_w = Inches(1.1)
            logo_left = Inches(0.8) if is_rtl else (self.slide_width - Inches(0.8) - logo_w)
            try:
                slide.shapes.add_picture(self.logo_path, logo_left, Inches(0.35), width=logo_w)
            except Exception:
                pass

        # Thin Footer Divider Line
        y_div = self.slide_height - m_h
        div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y_div, self.slide_width - Inches(1.6), Pt(1))
        div.fill.solid()
        div.fill.fore_color.rgb = self.theme["card_border"]
        div.line.color.rgb = self.theme["card_border"]

        # Footer Text
        f_box = slide.shapes.add_textbox(Inches(0.8), y_div + Inches(0.08), self.slide_width - Inches(1.6), Inches(0.4))
        f_tf = f_box.text_frame
        f_tf.word_wrap = True

        fp = f_tf.paragraphs[0]
        ft_text = f"{self.organization}  •  {self.title}" if self.organization else self.title
        self._format_paragraph(fp, ft_text, font_size=Pt(9.5), color=RGBColor(148, 163, 184), is_rtl=is_rtl)

        if slide_num is not None:
            num_w = Inches(1.5)
            num_left = Inches(0.8) if not is_rtl else (self.slide_width - Inches(0.8) - num_w)
            num_box = slide.shapes.add_textbox(num_left, y_div + Inches(0.08), num_w, Inches(0.4))
            n_tf = num_box.text_frame
            np = n_tf.paragraphs[0]
            num_align = PP_ALIGN.LEFT if is_rtl else PP_ALIGN.RIGHT
            self._format_paragraph(np, str(slide_num), font_size=Pt(9.5), bold=True, color=self.theme["accent"], is_rtl=is_rtl, align=num_align)

    def add_title_slide(self, title=None, subtitle=None, author=None, organization=None, date_str=None):
        """Generates executive title / cover slide with zero logo collision and 100% native editable text."""
        title = title or self.title
        subtitle = subtitle or self.subtitle
        author = author or self.author
        organization = organization or self.organization
        date_str = date_str or self.date_str

        is_rtl = is_rtl_text(title) or is_rtl_text(subtitle) or self.is_rtl_doc
        slide = self._create_slide()

        cover_bg = self.theme.get("primary", RGBColor(10, 15, 29)) if self.is_dark_canvas else self.theme.get("bg_light", RGBColor(248, 250, 252))
        self._add_slide_background(slide, cover_bg)

        # 1. Top Brand Logo centered with ample breathing room
        if self.logo_path and os.path.exists(self.logo_path):
            logo_w = Inches(1.8)
            logo_left = (self.slide_width - logo_w) / 2
            logo_top = Inches(0.8)
            try:
                slide.shapes.add_picture(self.logo_path, logo_left, logo_top, width=logo_w)
            except Exception:
                pass

        # 2. Main Title Container (Single Shape Text Frame)
        title_top = Inches(2.5)
        title_w = Inches(11.0)
        title_left = (self.slide_width - title_w) / 2

        tx_box = slide.shapes.add_textbox(title_left, title_top, title_w, Inches(2.7))
        tf = tx_box.text_frame
        tf.word_wrap = True

        # Category Pill
        p_tag = tf.paragraphs[0]
        tag_text = "• تقرير استراتيجي تنفيذي • TEKNOKEYS FINTECH" if is_rtl else "EXECUTIVE STRATEGIC REPORT • FINTECH"
        self._format_paragraph(p_tag, tag_text, font_size=Pt(12), bold=True, color=self.theme["accent"], is_rtl=is_rtl, align=PP_ALIGN.CENTER)

        # Title
        p_t = tf.add_paragraph()
        p_t.space_before = Pt(14)
        p_t.space_after = Pt(12)
        t_col = RGBColor(255, 255, 255) if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=t_col,
                                default_size=Pt(30), is_rtl=is_rtl, base_bold=True)
        p_t.alignment = PP_ALIGN.CENTER
        self._apply_paragraph_rtl(p_t, is_rtl)

        # Subtitle
        if subtitle:
            p_sub = tf.add_paragraph()
            p_sub.space_before = Pt(6)
            sub_col = RGBColor(203, 213, 225) if self.is_dark_canvas else self.theme["body"]
            self._render_inline_text(p_sub, subtitle, default_color=sub_col,
                                    default_size=Pt(15), is_rtl=is_rtl)
            p_sub.alignment = PP_ALIGN.CENTER
            self._apply_paragraph_rtl(p_sub, is_rtl)

        # 3. Bottom Executive Metadata Card (Single Unified Shape with text inside text_frame!)
        meta_w = Inches(11.0)
        meta_h = Inches(0.85)
        meta_left = (self.slide_width - meta_w) / 2
        meta_top = Inches(5.8)

        meta_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, meta_left, meta_top, meta_w, meta_h)
        meta_card.fill.solid()
        meta_card.fill.fore_color.rgb = self.theme.get("card_bg", RGBColor(20, 30, 48)) if self.is_dark_canvas else RGBColor(255, 255, 255)
        meta_card.line.color.rgb = self.theme["accent"]
        meta_card.line.width = Pt(1.2)

        m_tf = meta_card.text_frame
        m_tf.word_wrap = True
        m_tf.margin_left = Inches(0.3)
        m_tf.margin_right = Inches(0.3)
        m_tf.margin_top = Inches(0.18)
        m_tf.margin_bottom = Inches(0.15)
        m_tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        m_p = m_tf.paragraphs[0]
        meta_items = []
        if author:
            meta_items.append(f"إعداد: {author}" if is_rtl else f"Author: {author}")
        if organization:
            meta_items.append(f"الجهة: {organization}" if is_rtl else f"Org: {organization}")
        if date_str:
            meta_items.append(f"التاريخ: {date_str}" if is_rtl else f"Date: {date_str}")
        meta_line = "   •   ".join(meta_items)
        m_col = RGBColor(226, 232, 240) if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(m_p, meta_line, default_color=m_col,
                                default_size=Pt(11.5), is_rtl=is_rtl)
        m_p.alignment = PP_ALIGN.CENTER
        self._apply_paragraph_rtl(m_p, is_rtl)

        return slide

    def add_agenda_slide(self, title="Agenda & Key Themes", items=None, category="OVERVIEW"):
        if isinstance(title, list) and items is None:
            items = title
            title = "Agenda & Key Themes"
        items = items or []
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        top = Inches(1.9)
        avail_h = Inches(4.7)
        n = max(1, min(len(items), 6))
        gap = Inches(0.15)
        row_h = (avail_h - (gap * (n - 1))) / n
        col_w = self.slide_width - Inches(1.6)

        for i, itm in enumerate(items[:n]):
            y = top + i * (row_h + gap)
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, col_w, row_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.theme["card_bg"]
            card.line.color.rgb = self.theme["card_border"]
            card.line.width = Pt(1.0)

            c_tf = card.text_frame
            c_tf.word_wrap = True
            c_tf.margin_left = Inches(0.25)
            c_tf.margin_right = Inches(0.25)
            c_tf.vertical_anchor = MSO_ANCHOR.MIDDLE

            p = c_tf.paragraphs[0]
            if isinstance(itm, dict):
                itm_num = itm.get("number", f"{i+1:02d}")
                itm_title = itm.get("title", "")
                itm_desc = itm.get("desc", "")
                if is_rtl:
                    line_str = f"{itm_num} — **{itm_title}**: {itm_desc}" if itm_desc else f"{itm_num} — {itm_title}"
                else:
                    line_str = f"[{itm_num}]  **{itm_title}**: {itm_desc}" if itm_desc else f"[{itm_num}]  {itm_title}"
            else:
                line_str = f"{i+1:02d} — {str(itm)}" if is_rtl else f"[{i+1:02d}]  {str(itm)}"
            ag_col = RGBColor(241, 245, 249) if self.is_dark_canvas else self.theme["body"]
            self._render_inline_text(p, line_str, default_color=ag_col,
                                    default_size=Pt(13.5), is_rtl=is_rtl)
            self._apply_paragraph_rtl(p, is_rtl)

        return slide

    def add_split_hero_slide(self, title, hero_title, hero_text, items=None, category=None):
        """Generates executive 2-column layout: Hero focus card on one side, 6 structured cards on other."""
        items = items or []
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        top = Inches(1.8)
        content_h = Inches(4.8)
        hero_w = Inches(4.5)
        list_w = Inches(6.8)
        spacing = Inches(0.433)

        if is_rtl:
            hero_left = self.slide_width - Inches(0.8) - hero_w
            list_left = Inches(0.8)
        else:
            hero_left = Inches(0.8)
            list_left = hero_left + hero_w + spacing

        # 1. Hero Focus Panel (Single shape with text inside text_frame!)
        h_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, hero_left, top, hero_w, content_h)
        h_card.fill.solid()
        h_card.fill.fore_color.rgb = self.theme["card_bg"]
        h_card.line.color.rgb = self.theme["accent"]
        h_card.line.width = Pt(1.5)

        h_tf = h_card.text_frame
        h_tf.word_wrap = True
        h_tf.margin_left = Inches(0.35)
        h_tf.margin_right = Inches(0.35)
        h_tf.margin_top = Inches(0.35)
        h_tf.margin_bottom = Inches(0.35)
        h_tf.vertical_anchor = MSO_ANCHOR.TOP

        hp1 = h_tf.paragraphs[0]
        self._render_inline_text(hp1, hero_title, default_color=self.theme["accent"], default_size=Pt(21), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(hp1, is_rtl)

        hp2 = h_tf.add_paragraph()
        hp2.space_before = Pt(16)
        h_col = RGBColor(203, 213, 225) if self.is_dark_canvas else self.theme["body"]
        self._render_inline_text(hp2, hero_text, default_color=h_col, default_size=Pt(13.5), is_rtl=is_rtl)
        self._apply_paragraph_rtl(hp2, is_rtl)

        # 2. Numbered Items List: 6 sleek horizontal cards (each is a single shape with text_frame!)
        n_items = min(len(items), 6)
        if n_items > 0:
            row_gap = Inches(0.12)
            row_h = (content_h - (row_gap * (n_items - 1))) / n_items
            for i, item in enumerate(items[:n_items]):
                r_top = top + i * (row_h + row_gap)

                item_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, list_left, r_top, list_w, row_h)
                item_card.fill.solid()
                item_card.fill.fore_color.rgb = self.theme["card_bg"]
                item_card.line.color.rgb = self.theme["card_border"]
                item_card.line.width = Pt(1.0)

                it_tf = item_card.text_frame
                it_tf.word_wrap = True
                it_tf.margin_left = Inches(0.2)
                it_tf.margin_right = Inches(0.2)
                it_tf.margin_top = Inches(0.08)
                it_tf.margin_bottom = Inches(0.08)
                it_tf.vertical_anchor = MSO_ANCHOR.MIDDLE

                it_p = it_tf.paragraphs[0]
                if isinstance(item, dict):
                    i_title = item.get("title") or item.get("text", "")
                    i_desc = item.get("desc", "")
                    if is_rtl:
                        i_str = f"{i+1:02d} — **{i_title}**: {i_desc}" if i_desc else str(i_title)
                    else:
                        i_str = f"[{i+1:02d}]  **{i_title}**: {i_desc}" if i_desc else str(i_title)
                else:
                    i_str = f"{i+1:02d} — {str(item)}" if is_rtl else f"[{i+1:02d}]  {str(item)}"
                self._render_inline_text(it_p, i_str, default_color=self.theme["body"], default_size=Pt(12.5), is_rtl=is_rtl)
                self._apply_paragraph_rtl(it_p, is_rtl)

        return slide

    def add_versus_slide(self, title, col1_title, col1_blocks, col2_title, col2_blocks, category=None):
        """Generates asymmetric comparative battle layout: Problem (Crimson) vs Solution (Gold) with 100% editable cards."""
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title Box
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        col_w = Inches(5.6)
        spacing = Inches(0.533)
        top = Inches(1.8)
        card_h = Inches(4.8)

        if is_rtl:
            left1 = self.slide_width - Inches(0.8) - col_w
            left2 = Inches(0.8)
        else:
            left1 = Inches(0.8)
            left2 = left1 + col_w + spacing

        # --- Column 1: Legacy Problem (Single Shape with text inside text_frame!) ---
        card1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left1, top, col_w, card_h)
        card1.fill.solid()
        card1.fill.fore_color.rgb = self.theme["card_bg"]
        card1.line.color.rgb = RGBColor(190, 18, 60)
        card1.line.width = Pt(1.5)

        c1_tf = card1.text_frame
        c1_tf.word_wrap = True
        c1_tf.margin_left = Inches(0.35)
        c1_tf.margin_right = Inches(0.35)
        c1_tf.margin_top = Inches(0.35)
        c1_tf.margin_bottom = Inches(0.35)
        c1_tf.vertical_anchor = MSO_ANCHOR.TOP

        p_c1_tag = c1_tf.paragraphs[0]
        self._format_paragraph(p_c1_tag, "⚠️ القيود والتحديات الحالية" if is_rtl else "⚠️ LEGACY CHALLENGES", font_size=Pt(11), bold=True, color=RGBColor(244, 63, 94), is_rtl=is_rtl)

        p_c1_t = c1_tf.add_paragraph()
        p_c1_t.space_before = Pt(8)
        p_c1_t.space_after = Pt(10)
        self._render_inline_text(p_c1_t, col1_title, default_color=RGBColor(244, 63, 94), default_size=Pt(17), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_c1_t, is_rtl)

        for blk in col1_blocks:
            p = c1_tf.add_paragraph()
            p.space_before = Pt(10)
            p.space_after = Pt(4)
            raw = blk.get("text", "") if isinstance(blk, dict) else str(blk)
            raw = re.sub(r'^[•\-\*]\s*', '', raw).strip()
            self._apply_bullet_format(p, indent_level=0, color=RGBColor(244, 63, 94), is_rtl=is_rtl)
            v1_col = RGBColor(203, 213, 225) if self.is_dark_canvas else self.theme["body"]
            self._render_inline_text(p, raw, default_color=v1_col, default_size=Pt(13.5), is_rtl=is_rtl)

        # --- Central VS Badge ---
        vs_x = (self.slide_width - Inches(0.7)) / 2
        vs_y = top + (card_h - Inches(0.7)) / 2
        vs_circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, vs_x, vs_y, Inches(0.7), Inches(0.7))
        vs_circle.fill.solid()
        vs_circle.fill.fore_color.rgb = self.theme["primary"]
        vs_circle.line.color.rgb = self.theme["accent"]
        vs_circle.line.width = Pt(2.0)
        vs_p = vs_circle.text_frame.paragraphs[0]
        self._format_paragraph(vs_p, "VS", font_size=Pt(11), bold=True, color=self.theme["accent"], is_rtl=False, align=PP_ALIGN.CENTER)

        # --- Column 2: Solution (Single Shape with text inside text_frame!) ---
        card2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left2, top, col_w, card_h)
        card2.fill.solid()
        card2.fill.fore_color.rgb = self.theme["card_bg"]
        card2.line.color.rgb = self.theme["accent"]
        card2.line.width = Pt(2.0)

        c2_tf = card2.text_frame
        c2_tf.word_wrap = True
        c2_tf.margin_left = Inches(0.35)
        c2_tf.margin_right = Inches(0.35)
        c2_tf.margin_top = Inches(0.35)
        c2_tf.margin_bottom = Inches(0.35)
        c2_tf.vertical_anchor = MSO_ANCHOR.TOP

        p_c2_tag = c2_tf.paragraphs[0]
        self._format_paragraph(p_c2_tag, "⭐ الحل الاستراتيجي الموصى به" if is_rtl else "⭐ STRATEGIC SOLUTION", font_size=Pt(11), bold=True, color=self.theme["accent"], is_rtl=is_rtl)

        p_c2_t = c2_tf.add_paragraph()
        p_c2_t.space_before = Pt(8)
        p_c2_t.space_after = Pt(10)
        self._render_inline_text(p_c2_t, col2_title, default_color=self.theme["accent"], default_size=Pt(17), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_c2_t, is_rtl)

        for blk in col2_blocks:
            p = c2_tf.add_paragraph()
            p.space_before = Pt(10)
            p.space_after = Pt(4)
            raw = blk.get("text", "") if isinstance(blk, dict) else str(blk)
            raw = re.sub(r'^[•\-\*]\s*', '', raw).strip()
            self._apply_bullet_format(p, indent_level=0, color=self.theme["accent"], is_rtl=is_rtl)
            v2_col = RGBColor(241, 245, 249) if self.is_dark_canvas else self.theme["body"]
            self._render_inline_text(p, raw, default_color=v2_col, default_size=Pt(13.5), is_rtl=is_rtl)

        return slide

    def add_architecture_slide(self, title, layers=None, category=None):
        """Generates 3-tier layered system architecture topology slide with fully editable cards."""
        layers = layers or []
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        top = Inches(1.8)
        w = self.slide_width - Inches(1.6)
        n = max(1, min(len(layers), 3))
        tier_h = Inches(1.28)
        gap = Inches(0.42)

        for i, layer in enumerate(layers[:n]):
            y = top + i * (tier_h + gap)

            tier = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, w, tier_h)
            tier.fill.solid()
            tier.fill.fore_color.rgb = self.theme["card_bg"]
            tier.line.color.rgb = self.theme["accent"] if i == 1 else self.theme["card_border"]
            tier.line.width = Pt(2.0 if i == 1 else 1.0)

            t_tf = tier.text_frame
            t_tf.word_wrap = True
            t_tf.margin_left = Inches(0.3)
            t_tf.margin_right = Inches(0.3)
            t_tf.margin_top = Inches(0.15)
            t_tf.margin_bottom = Inches(0.15)
            t_tf.vertical_anchor = MSO_ANCHOR.TOP

            p1 = t_tf.paragraphs[0]
            l_tag = layer.get("tag", f"TIER 0{i+1}")
            l_title = layer.get("title", "")
            if is_rtl:
                combined_h = f"المستوى 0{i+1}  —  {l_title}"
            else:
                combined_h = f"[{l_tag}]  {l_title}"
            arch_t_col = self.theme["accent"] if i == 1 else (RGBColor(255, 255, 255) if self.is_dark_canvas else self.theme["primary"])
            self._render_inline_text(p1, combined_h, default_color=arch_t_col,
                                     default_size=Pt(15), is_rtl=is_rtl, base_bold=True)
            self._apply_paragraph_rtl(p1, is_rtl)

            p2 = t_tf.add_paragraph()
            p2.space_before = Pt(4)
            l_desc = layer.get("desc", "")
            # Clean up pipe characters into clean bullets
            clean_desc = "   •   ".join(s.strip() for s in l_desc.split("|") if s.strip())
            arch_d_col = RGBColor(203, 213, 225) if self.is_dark_canvas else self.theme["body"]
            self._render_inline_text(p2, clean_desc, default_color=arch_d_col, default_size=Pt(12), is_rtl=is_rtl)
            self._apply_paragraph_rtl(p2, is_rtl)

            if i < n - 1:
                arr_y = y + tier_h + Inches(0.06)
                pill_w = Inches(6.5)
                pill_x = (self.slide_width - pill_w) / 2
                pill_h = gap - Inches(0.12)
                arr_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pill_x, arr_y, pill_w, pill_h)
                arr_box.fill.solid()
                arr_box.fill.fore_color.rgb = self.theme["primary"]
                arr_box.line.color.rgb = self.theme["accent"]
                arr_box.line.width = Pt(1.0)
                a_tf = arr_box.text_frame
                a_p = a_tf.paragraphs[0]
                conn_txt = "⚡ Contactless APDU (ISO 14443)  •  ISO 8583 Bus  •  <1ms Latency" if i == 0 else "🔐 Sovereign HSM Key Vault  •  Atomic Dual Ledger Settlement"
                self._format_paragraph(a_p, conn_txt, font_size=Pt(10), bold=True, color=self.theme["accent"], is_rtl=is_rtl, align=PP_ALIGN.CENTER)

        return slide

    def add_callout_slide(self, title, callout_type="note", callout_title=None,
                          text="", bullets=None, category=None):
        """Generates executive 2-panel Security & Trust Architecture showcase with 100% editable cards."""
        bullets = bullets or []
        is_rtl = is_rtl_text(title) or is_rtl_text(text) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        c_kind = callout_type.lower() if callout_type else "note"
        c_title_raw = callout_title or c_kind.upper()
        clean_c_title = re.sub(r'[\[\]]', '', c_title_raw).strip()
        clean_c_title = re.sub(r'^!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\s*', '', clean_c_title, flags=re.IGNORECASE).strip()

        top = Inches(1.8)
        main_w = Inches(6.8)
        side_w = Inches(4.5)
        spacing = Inches(0.4)
        card_h = Inches(4.8)

        if is_rtl:
            main_left = self.slide_width - Inches(0.8) - main_w
            side_left = Inches(0.8)
        else:
            main_left = Inches(0.8)
            side_left = main_left + main_w + spacing

        # 1. Main Focus Security Vault Card (Single Shape with text inside text_frame!)
        main_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, main_left, top, main_w, card_h)
        main_card.fill.solid()
        main_card.fill.fore_color.rgb = self.theme["card_bg"]
        main_card.line.color.rgb = self.theme["accent"]
        main_card.line.width = Pt(1.5)

        m_tf = main_card.text_frame
        m_tf.word_wrap = True
        m_tf.margin_left = Inches(0.35)
        m_tf.margin_right = Inches(0.35)
        m_tf.margin_top = Inches(0.35)
        m_tf.margin_bottom = Inches(0.35)
        m_tf.vertical_anchor = MSO_ANCHOR.TOP

        p_badge = m_tf.paragraphs[0]
        badge_txt = "🔒 التوكنة الديناميكية — Dynamic DPAN" if is_rtl else "🔒 DYNAMIC DPAN TOKENIZATION"
        self._format_paragraph(p_badge, badge_txt, font_size=Pt(11), bold=True, color=self.theme["accent"], is_rtl=is_rtl)

        p_h = m_tf.add_paragraph()
        p_h.space_before = Pt(10)
        p_h.space_after = Pt(12)
        c_t_col = RGBColor(255, 255, 255) if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_h, clean_c_title, default_color=c_t_col,
                                default_size=Pt(18), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_h, is_rtl)

        if text:
            p_b = m_tf.add_paragraph()
            p_b.space_before = Pt(6)
            c_b_col = RGBColor(203, 213, 225) if self.is_dark_canvas else self.theme["body"]
            self._render_inline_text(p_b, text, default_color=c_b_col,
                                    default_size=Pt(13.5), is_rtl=is_rtl)
            self._apply_paragraph_rtl(p_b, is_rtl)

        p_cert = m_tf.add_paragraph()
        p_cert.space_before = Pt(24)
        cert_txt = "✔ PCI DSS v4.0.1   •   ⚡ AES-128 CMAC   •   🛡️ حماية الحساب الأصلي" if is_rtl else "✔ PCI DSS v4.0.1   •   ⚡ AES-128 CMAC   •   🛡️ Zero PAN Exposure"
        self._format_paragraph(p_cert, cert_txt, font_size=Pt(11), bold=True, color=self.theme["accent"], is_rtl=is_rtl)

        # 2. Three Stacked Security Pillars on Side Panel (Each is a single shape with text_frame!)
        pillars = [
            ("حظر التنصت اللاسلكي", "الرمز البديل المشفر (DPAN) مؤقت وتتغير شفرته مع كل عملية دفع لمنع النسخ."),
            ("حماية الرصيد والهوية", "استحالة كشف بيانات العميل أو رقم هاتفه عبر أجهزة المسح الميداني."),
            ("امتثال مصرفي سيادي", "مطابقة تامة لأعلى معايير الأمان المصرفي ومتطلبات البنك المركزي اليمني.")
        ] if is_rtl else [
            ("Eavesdropping Immunity", "Dynamic DPAN refreshes per transaction; RF sniffing yields zero value."),
            ("Identity & Balance Shield", "Zero PAN exposure; POS terminals never receive customer account details."),
            ("Sovereign Compliance", "Fully aligned with Central Bank regulations and PCI DSS v4.0.1 mandate.")
        ]

        p_gap = Inches(0.18)
        p_h = (card_h - (p_gap * 2)) / 3
        for idx, (p_title, p_desc) in enumerate(pillars):
            py = top + idx * (p_h + p_gap)
            p_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, side_left, py, side_w, p_h)
            p_card.fill.solid()
            p_card.fill.fore_color.rgb = self.theme["card_bg"]
            p_card.line.color.rgb = self.theme["card_border"]
            p_card.line.width = Pt(1.0)

            ptf = p_card.text_frame
            ptf.word_wrap = True
            ptf.margin_left = Inches(0.25)
            ptf.margin_right = Inches(0.25)
            ptf.margin_top = Inches(0.15)
            ptf.margin_bottom = Inches(0.15)
            ptf.vertical_anchor = MSO_ANCHOR.TOP

            pp1 = ptf.paragraphs[0]
            header_str = f"{idx+1:02d} — {p_title}" if is_rtl else f"[{idx+1:02d}]  {p_title}"
            self._render_inline_text(pp1, header_str, default_color=self.theme["accent"], default_size=Pt(14), is_rtl=is_rtl, base_bold=True)
            self._apply_paragraph_rtl(pp1, is_rtl)

            pp2 = ptf.add_paragraph()
            pp2.space_before = Pt(4)
            c_desc_col = RGBColor(203, 213, 225) if self.is_dark_canvas else self.theme["body"]
            self._render_inline_text(pp2, p_desc, default_color=c_desc_col, default_size=Pt(11.5), is_rtl=is_rtl)
            self._apply_paragraph_rtl(pp2, is_rtl)

        return slide

    def add_metrics_slide(self, title, metrics, subtitle=None, category=None):
        """Generates KPI metrics slide with 4 elevated dark cards and rich vertical hierarchy filling the height."""
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color,
                                default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        n = min(len(metrics), 4)
        if n == 0:
            return slide

        gap = Inches(0.35)
        total_gaps = gap * (n - 1)
        avail_w = self.slide_width - Inches(1.6) - total_gaps
        card_w = avail_w / n
        card_h = Inches(4.7)
        top = Inches(1.8)

        metric_tags = [
            ("⚡ سرعة المعاملة", "✔ معيار الجيل القادم"),
            ("📈 كفاءة الصندوق", "✔ إنهاء طوابير الكاشير"),
            ("🚀 قدرة المعالجة", "✔ محرك Go عالي التوازي"),
            ("💰 نمو السيولة", "✔ تعظيم دوران الأموال")
        ]

        for i, m in enumerate(metrics[:4]):
            col_idx = (n - 1 - i) if is_rtl else i
            left = Inches(0.8) + (col_idx * (card_w + gap))

            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, card_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.theme["card_bg"]
            card.line.color.rgb = self.theme["accent"] if self.is_dark_canvas else self.theme["card_border"]
            card.line.width = Pt(1.5)

            c_tf = card.text_frame
            c_tf.word_wrap = True
            c_tf.margin_left = Inches(0.2)
            c_tf.margin_right = Inches(0.2)
            c_tf.margin_top = Inches(0.25)
            c_tf.margin_bottom = Inches(0.25)
            c_tf.vertical_anchor = MSO_ANCHOR.TOP

            # 1. Top Category Tag
            p_tag = c_tf.paragraphs[0]
            tag_name = metric_tags[i][0] if is_rtl and i < len(metric_tags) else "METRIC HIGHLIGHT"
            self._format_paragraph(p_tag, tag_name, font_size=Pt(11), bold=True, color=self.theme["accent"], is_rtl=is_rtl, align=PP_ALIGN.CENTER)

            # 2. Hero Big Metric Value
            p_val = c_tf.add_paragraph()
            p_val.space_before = Pt(14)
            val_str = str(m.get("value", ""))
            self._format_paragraph(p_val, val_str, font_size=Pt(44), bold=True, color=self.theme["accent"], is_rtl=is_rtl, align=PP_ALIGN.CENTER)

            # 3. Metric Title / Label
            p_lbl = c_tf.add_paragraph()
            p_lbl.space_before = Pt(12)
            m_lbl_col = RGBColor(255, 255, 255) if self.is_dark_canvas else self.theme["primary"]
            self._render_inline_text(p_lbl, m.get("label", ""),
                                    default_color=m_lbl_col,
                                    default_size=Pt(17), is_rtl=is_rtl, base_bold=True)
            p_lbl.alignment = PP_ALIGN.CENTER

            # 4. Detailed Business Description
            sub_text = m.get("sub", "")
            if sub_text:
                p_sub = c_tf.add_paragraph()
                p_sub.space_before = Pt(10)
                m_sub_col = RGBColor(148, 163, 184) if self.is_dark_canvas else self.theme["body"]
                self._render_inline_text(p_sub, sub_text, default_color=m_sub_col,
                                        default_size=Pt(12.5), is_rtl=is_rtl)
                p_sub.alignment = PP_ALIGN.CENTER

            # 5. Bottom Validation Status Tag
            p_stat = c_tf.add_paragraph()
            p_stat.space_before = Pt(20)
            stat_name = metric_tags[i][1] if is_rtl and i < len(metric_tags) else "✔ معتمد مصرفياً"
            self._format_paragraph(p_stat, stat_name, font_size=Pt(10.5), bold=True, color=RGBColor(16, 185, 129), is_rtl=is_rtl, align=PP_ALIGN.CENTER)

        return slide

    def add_grid_slide(self, title, cards=None, category=None):
        """Generates 2x2 feature matrix grid layout with 100% unified, fully editable cards."""
        cards = cards or []
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        top = Inches(1.8)
        col_w = Inches(5.6)
        row_h = Inches(2.25)
        gap_x = Inches(0.533)
        gap_y = Inches(0.3)

        for i, card in enumerate(cards[:4]):
            r = i // 2
            c = i % 2
            c_idx = (1 - c) if is_rtl else c

            x = Inches(0.8) + c_idx * (col_w + gap_x)
            y = top + r * (row_h + gap_y)

            card_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, col_w, row_h)
            card_shape.fill.solid()
            card_shape.fill.fore_color.rgb = self.theme["card_bg"]
            card_shape.line.color.rgb = self.theme["card_border"]
            card_shape.line.width = Pt(1.0)

            c_tf = card_shape.text_frame
            c_tf.word_wrap = True
            c_tf.margin_left = Inches(0.3)
            c_tf.margin_right = Inches(0.3)
            c_tf.margin_top = Inches(0.2)
            c_tf.margin_bottom = Inches(0.2)
            c_tf.vertical_anchor = MSO_ANCHOR.TOP

            # Header with Number
            p1 = c_tf.paragraphs[0]
            raw_title = card.get("title", "") if isinstance(card, dict) else str(card)
            clean_title = re.sub(r'^[\[\d\]\s\-_•]+', '', raw_title).strip()
            num_pill = f"{i+1:02d} — {clean_title}" if is_rtl else f"[{i+1:02d}]  {clean_title}"
            self._render_inline_text(p1, num_pill, default_color=self.theme["accent"], default_size=Pt(16), is_rtl=is_rtl, base_bold=True)
            self._apply_paragraph_rtl(p1, is_rtl)

            # Card Content / Bullets
            items = card.get("items", []) if isinstance(card, dict) else []
            if not items and isinstance(card, dict) and card.get("desc"):
                items = [card["desc"]]

            for blk in items:
                p = c_tf.add_paragraph()
                p.space_before = Pt(8)
                raw_txt = blk.get("text", "") if isinstance(blk, dict) else str(blk)
                raw_txt = re.sub(r'^[•\-\*]\s*', '', raw_txt).strip()
                self._apply_bullet_format(p, indent_level=0, color=self.theme["accent"], is_rtl=is_rtl)
                gr_col = RGBColor(203, 213, 225) if self.is_dark_canvas else self.theme["body"]
                self._render_inline_text(p, raw_txt, default_color=gr_col, default_size=Pt(13), is_rtl=is_rtl)

        return slide

    def add_two_column_slide(self, title, col1_title, col1_blocks, col2_title, col2_blocks, category=None):
        """Generates 2-column comparison layout with 100% unified editable cards."""
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        col_w = Inches(5.6)
        spacing = Inches(0.533)
        top = Inches(1.8)
        card_h = Inches(4.8)

        if is_rtl:
            left1 = self.slide_width - Inches(0.8) - col_w
            left2 = Inches(0.8)
        else:
            left1 = Inches(0.8)
            left2 = left1 + col_w + spacing

        for idx, (col_left, c_title, blocks) in enumerate([(left1, col1_title, col1_blocks), (left2, col2_title, col2_blocks)]):
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, col_left, top, col_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.theme["card_bg"]
            card.line.color.rgb = self.theme["accent"] if idx == 1 else self.theme["card_border"]
            card.line.width = Pt(1.5 if idx == 1 else 1.0)

            c_tf = card.text_frame
            c_tf.word_wrap = True
            c_tf.margin_left = Inches(0.35)
            c_tf.margin_right = Inches(0.35)
            c_tf.margin_top = Inches(0.35)
            c_tf.margin_bottom = Inches(0.35)
            c_tf.vertical_anchor = MSO_ANCHOR.TOP

            p_h = c_tf.paragraphs[0]
            self._render_inline_text(p_h, c_title, default_color=self.theme["accent"], default_size=Pt(18), is_rtl=is_rtl, base_bold=True)
            self._apply_paragraph_rtl(p_h, is_rtl)

            for blk in blocks:
                p = c_tf.add_paragraph()
                p.space_before = Pt(12)
                p.space_after = Pt(4)
                raw = blk.get("text", "") if isinstance(blk, dict) else str(blk)
                raw = re.sub(r'^[•\-\*]\s*', '', raw).strip()
                self._apply_bullet_format(p, indent_level=0, color=self.theme["accent"], is_rtl=is_rtl)
                v1_col = RGBColor(203, 213, 225) if self.is_dark_canvas else self.theme["body"]
                self._render_inline_text(p, raw, default_color=v1_col, default_size=Pt(13.5), is_rtl=is_rtl)

        return slide

    def add_table_slide(self, title, headers, rows, category=None):
        """Generates formatted table slide with colored header and highlighted winning column."""
        is_rtl = is_rtl_text(title) or (headers and is_rtl_text(headers[0])) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title Box
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        if not headers or not rows:
            return slide

        num_rows = len(rows) + 1
        num_cols = len(headers)
        table_w = self.slide_width - Inches(1.6)
        table_h = min(Inches(4.8), Inches(0.65) * num_rows)
        top = Inches(1.9)

        table_shape = slide.shapes.add_table(num_rows, num_cols, Inches(0.8), top, table_w, table_h)
        tbl = table_shape.table

        # Format Header Row
        for col_idx, h_text in enumerate(headers):
            c_idx = (num_cols - 1 - col_idx) if is_rtl else col_idx
            cell = tbl.cell(0, c_idx)
            cell.fill.solid()
            is_winner = "TeknoNFC" in h_text or "تكنوكيز" in h_text
            if is_winner:
                cell.fill.fore_color.rgb = self.theme["accent"]
                hdr_color = self.theme["primary"]
            else:
                cell.fill.fore_color.rgb = RGBColor(30, 41, 59) if self.is_dark_canvas else self.theme["primary"]
                hdr_color = RGBColor(255, 255, 255)

            p = cell.text_frame.paragraphs[0]
            self._render_inline_text(p, h_text, default_color=hdr_color, default_size=Pt(13.5), is_rtl=is_rtl, base_bold=True)
            self._apply_paragraph_rtl(p, is_rtl)

        # Format Body Rows with zebra striping and winning column highlight
        for row_idx, row in enumerate(rows):
            is_zebra = (row_idx % 2 == 1)

            for col_idx, cell_text in enumerate(row):
                if col_idx >= num_cols:
                    break
                c_idx = (num_cols - 1 - col_idx) if is_rtl else col_idx
                cell = tbl.cell(row_idx + 1, c_idx)
                cell.fill.solid()

                h_name = headers[col_idx] if col_idx < len(headers) else ""
                is_winner_col = "TeknoNFC" in h_name or "تكنوكيز" in h_name

                if is_winner_col:
                    cell.fill.fore_color.rgb = RGBColor(22, 36, 68) if self.is_dark_canvas else RGBColor(254, 243, 199)
                    text_color = self.theme["accent"] if self.is_dark_canvas else RGBColor(146, 64, 14)
                    is_bold = True
                else:
                    cell.fill.fore_color.rgb = self.theme["bg_light"] if is_zebra else self.theme["card_bg"]
                    text_color = RGBColor(203, 213, 225) if self.is_dark_canvas else self.theme["body"]
                    is_bold = False

                p = cell.text_frame.paragraphs[0]
                self._render_inline_text(p, cell_text, default_color=text_color,
                                        default_size=Pt(12.5), is_rtl=is_rtl, base_bold=is_bold)
                self._apply_paragraph_rtl(p, is_rtl)

        return slide

    def add_timeline_slide(self, title, steps=None, category=None):
        """Generates timeline/roadmap slide with 4 milestone cards and 100% editable shapes."""
        steps = steps or []
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        top = Inches(2.1)
        avail_w = self.slide_width - Inches(1.6)
        n = max(1, min(len(steps), 4))
        gap = Inches(0.35)
        step_w = (avail_w - (gap * (n - 1))) / n
        card_h = Inches(4.5)

        # Connector Line Behind Steps
        line_y = top + Inches(0.5)
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), line_y, avail_w - Inches(0.4), Pt(3))
        line.fill.solid()
        line.fill.fore_color.rgb = self.theme["accent"]
        line.line.color.rgb = self.theme["accent"]

        for i, step in enumerate(steps[:n]):
            idx = (n - 1 - i) if is_rtl else i
            x = Inches(0.8) + idx * (step_w + gap)

            # Circular Step Indicator
            circle_sz = Inches(0.55)
            circle_x = x + (step_w - circle_sz) / 2
            circle_y = line_y - circle_sz / 2
            circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, circle_x, circle_y, circle_sz, circle_sz)
            circle.fill.solid()
            circle.fill.fore_color.rgb = self.theme["accent"]
            circle.line.color.rgb = self.theme["accent"]
            cp = circle.text_frame.paragraphs[0]
            self._format_paragraph(cp, f"{i+1:02d}", font_size=Pt(11), bold=True, color=self.theme["primary"], is_rtl=is_rtl, align=PP_ALIGN.CENTER)

            # Milestone Card
            card_y = top + Inches(0.9)
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, card_y, step_w, card_h - Inches(0.9))
            card.fill.solid()
            card.fill.fore_color.rgb = self.theme["card_bg"]
            card.line.color.rgb = self.theme["card_border"]
            card.line.width = Pt(1.0)

            c_tf = card.text_frame
            c_tf.word_wrap = True
            c_tf.margin_left = Inches(0.2)
            c_tf.margin_right = Inches(0.2)
            c_tf.margin_top = Inches(0.2)
            c_tf.margin_bottom = Inches(0.2)
            c_tf.vertical_anchor = MSO_ANCHOR.TOP

            # Phase Title
            p_t_step = c_tf.paragraphs[0]
            s_title = step.get("title", "") if isinstance(step, dict) else str(step)
            phase_m = re.search(r'W(\d+)\s*[-–:]\s*(\d+)', s_title, re.IGNORECASE)
            clean_s_title = re.sub(r'W\d+\s*[-–:]\s*\d+[:\s]*', '', s_title, flags=re.IGNORECASE).strip()
            if phase_m:
                step_header = f"الأسبوع {phase_m.group(1)}-{phase_m.group(2)}  —  {clean_s_title}" if is_rtl else f"[W{phase_m.group(1)}-{phase_m.group(2)}]  {clean_s_title}"
            else:
                step_header = clean_s_title
            self._render_inline_text(p_t_step, step_header,
                                    default_color=self.theme["accent"], default_size=Pt(14), is_rtl=is_rtl, base_bold=True)
            self._apply_paragraph_rtl(p_t_step, is_rtl)

            # Step Items
            items = (step.get("bullets") or step.get("items") or []) if isinstance(step, dict) else []
            if not items and isinstance(step, dict) and step.get("desc"):
                items = [step["desc"]]

            for itm in items:
                p = c_tf.add_paragraph()
                p.space_before = Pt(8)
                raw_txt = itm.get("text", "") if isinstance(itm, dict) else str(itm)
                raw_txt = re.sub(r'^[•\-\*]\s*', '', raw_txt).strip()
                raw_txt = re.sub(r'^\*?\*?W\d+\s*[-–:]\s*\d+\*?\*?[:\s]*', '', raw_txt, flags=re.IGNORECASE).strip()
                raw_txt = re.sub(r'^[:\s]+', '', raw_txt).strip()
                self._apply_bullet_format(p, indent_level=0, color=self.theme["accent"], is_rtl=is_rtl)
                tl_col = RGBColor(203, 213, 225) if self.is_dark_canvas else self.theme["body"]
                self._render_inline_text(p, raw_txt, default_color=tl_col, default_size=Pt(12), is_rtl=is_rtl)

        return slide

    def add_content_slide(self, title, blocks=None, category=None):
        blocks = blocks or []
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        # Elegant Consulting Container Card
        card_w = self.slide_width - Inches(1.6)
        card_h = Inches(4.8)
        c_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), card_w, card_h)
        c_shape.fill.solid()
        c_shape.fill.fore_color.rgb = self.theme["card_bg"]
        c_shape.line.color.rgb = self.theme["card_border"]
        c_shape.line.width = Pt(1.0)

        c_tf = c_shape.text_frame
        c_tf.word_wrap = True
        c_tf.margin_left = Inches(0.4)
        c_tf.margin_right = Inches(0.4)
        c_tf.margin_top = Inches(0.3)
        c_tf.margin_bottom = Inches(0.3)
        c_tf.vertical_anchor = MSO_ANCHOR.TOP

        # Dynamic spacing and font sizing based on density
        n_blocks = len(blocks)
        if n_blocks >= 6:
            font_sz = Pt(11.5)
            h_sz = Pt(15)
            sp_top = Pt(4)
        elif n_blocks >= 4:
            font_sz = Pt(12.5)
            h_sz = Pt(16.5)
            sp_top = Pt(6)
        else:
            font_sz = Pt(13.5)
            h_sz = Pt(18)
            sp_top = Pt(8)

        first = True
        for blk in blocks:
            b_type = blk.get("type", "paragraph")
            text = blk.get("text", "")
            p = c_tf.paragraphs[0] if first else c_tf.add_paragraph()
            first = False

            if b_type == "heading":
                p.space_before = sp_top + Pt(4)
                p.space_after = Pt(2)
                self._render_inline_text(p, text, default_color=self.theme["accent"], default_size=h_sz, is_rtl=is_rtl, base_bold=True)
            elif b_type == "bullet":
                p.space_before = sp_top
                self._apply_bullet_format(p, indent_level=blk.get("level", 0), is_rtl=is_rtl)
                self._render_inline_text(p, text, default_color=self.theme["body"], default_size=font_sz, is_rtl=is_rtl)
            else:
                p.space_before = sp_top
                self._render_inline_text(p, text, default_color=self.theme["body"], default_size=font_sz, is_rtl=is_rtl)
            self._apply_paragraph_rtl(p, is_rtl)

        return slide

    def add_app_showcase_slide(self, title, image_path, specs=None, category=None):
        """Generates executive mobile app showcase layout with vertical phone frame and 3-4 structured technical cards."""
        specs = specs or []
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title Box
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        top = Inches(1.8)
        content_h = Inches(4.8)

        phone_frame_w = Inches(3.0)
        specs_w = Inches(8.3)
        gap = Inches(0.433)

        if is_rtl:
            phone_left = self.slide_width - Inches(0.8) - phone_frame_w
            specs_left = Inches(0.8)
        else:
            phone_left = Inches(0.8)
            specs_left = phone_left + phone_frame_w + gap

        # Phone Frame (Sleek dark card with gold border)
        frame_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, phone_left, top, phone_frame_w, content_h)
        frame_shape.fill.solid()
        frame_shape.fill.fore_color.rgb = RGBColor(11, 15, 25)
        frame_shape.line.color.rgb = self.theme["accent"]
        frame_shape.line.width = Pt(2.0)

        # Insert Mobile App Screenshot
        if image_path and os.path.exists(image_path):
            img_pad = Inches(0.06)
            img_w = phone_frame_w - (img_pad * 2)
            img_h = content_h - (img_pad * 2)
            try:
                slide.shapes.add_picture(image_path, phone_left + img_pad, top + img_pad, width=img_w, height=img_h)
            except Exception:
                pass

        # Technical Specification Cards on Side Panel
        valid_specs = []
        for b in specs:
            raw = b.get("text", "") if isinstance(b, dict) else str(b)
            raw = re.sub(r'^[•\-\*]\s*', '', raw).strip()
            if raw:
                valid_specs.append(raw)

        n_specs = max(1, min(len(valid_specs), 4))
        c_gap = Inches(0.12)
        c_h = (content_h - (c_gap * (n_specs - 1))) / n_specs

        for idx, spec_text in enumerate(valid_specs[:n_specs]):
            cy = top + idx * (c_h + c_gap)
            s_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, specs_left, cy, specs_w, c_h)
            s_card.fill.solid()
            s_card.fill.fore_color.rgb = self.theme["card_bg"]
            s_card.line.color.rgb = self.theme["card_border"]
            s_card.line.width = Pt(1.0)

            s_tf = s_card.text_frame
            s_tf.word_wrap = True
            s_tf.margin_left = Inches(0.25)
            s_tf.margin_right = Inches(0.25)
            s_tf.margin_top = Inches(0.12)
            s_tf.margin_bottom = Inches(0.1)
            s_tf.vertical_anchor = MSO_ANCHOR.MIDDLE

            sp = s_tf.paragraphs[0]
            m = re.match(r'^\*\*([^*:]+)(?::\s*([^*]+))?\*\*(?::\s*(.*))?', spec_text)
            if m:
                h_part = m.group(1).strip()
                b_part = (m.group(3) or m.group(2) or "").strip()
                if is_rtl:
                    formatted = f"{idx+1:02d} — **{h_part}**: {b_part}" if b_part else f"{idx+1:02d} — {h_part}"
                else:
                    formatted = f"[{idx+1:02d}]  **{h_part}**: {b_part}" if b_part else f"[{idx+1:02d}]  {h_part}"
            else:
                formatted = f"{idx+1:02d} — {spec_text}" if is_rtl else f"[{idx+1:02d}]  {spec_text}"

            font_sz = Pt(12.5) if n_specs <= 3 else Pt(11.5)
            self._render_inline_text(sp, formatted, default_color=self.theme["body"], default_size=font_sz, is_rtl=is_rtl)
            self._apply_paragraph_rtl(sp, is_rtl)

        return slide

    def add_code_slide(self, title, code_text, language=None, category=None):
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        code_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), self.slide_width - Inches(1.6), Inches(4.8))
        code_box.fill.solid()
        code_box.fill.fore_color.rgb = RGBColor(15, 23, 42)
        code_box.line.color.rgb = self.theme["card_border"]

        c_tf = code_box.text_frame
        c_tf.word_wrap = True
        c_tf.margin_left = Inches(0.3)
        c_tf.margin_right = Inches(0.3)
        c_tf.margin_top = Inches(0.2)
        c_tf.margin_bottom = Inches(0.2)

        p = c_tf.paragraphs[0]
        p.text = code_text
        p.font.name = "Consolas"
        p.font.size = Pt(11)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.alignment = PP_ALIGN.LEFT
        return slide

    def add_image_slide(self, title, image_path, caption=None, category=None):
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        self._add_slide_background(slide, self.theme["bg_light"])
        self._add_header_footer(slide, category=category, slide_num=len(self.slides))

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), self.slide_width - Inches(1.6), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        title_color = self.theme["accent"] if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=title_color, default_size=Pt(28), is_rtl=is_rtl, base_bold=True)
        self._apply_paragraph_rtl(p_t, is_rtl)

        if os.path.exists(image_path):
            img_left = Inches(0.8)
            img_top = Inches(1.8)
            img_w = self.slide_width - Inches(1.6)
            try:
                slide.shapes.add_picture(image_path, img_left, img_top, width=img_w)
            except Exception:
                pass
        return slide

    def add_closing_slide(self, title="Thank You", subtitle=None, contact_info=None):
        """Generates executive closing / Next Steps slide with 3 fully editable action cards."""
        is_rtl = is_rtl_text(title) or self.is_rtl_doc
        slide = self._create_slide()

        close_bg = self.theme["primary"] if self.is_dark_canvas else self.theme["bg_light"]
        self._add_slide_background(slide, close_bg)

        # 1. Embed Brand Logo centered at top
        if self.logo_path and os.path.exists(self.logo_path):
            logo_w = Inches(2.2)
            logo_left = (self.slide_width - logo_w) / 2
            try:
                slide.shapes.add_picture(self.logo_path, logo_left, Inches(0.85), width=logo_w)
            except Exception:
                pass

        # 2. Main Title & Subtitle Box
        tx_box = slide.shapes.add_textbox(Inches(1.0), Inches(2.35), self.slide_width - Inches(2.0), Inches(1.4))
        tf = tx_box.text_frame
        tf.word_wrap = True

        p_t = tf.paragraphs[0]
        close_t_col = RGBColor(255, 255, 255) if self.is_dark_canvas else self.theme["primary"]
        self._render_inline_text(p_t, title, default_color=close_t_col, default_size=Pt(32), is_rtl=is_rtl, base_bold=True)
        p_t.alignment = PP_ALIGN.CENTER

        if subtitle:
            p_sub = tf.add_paragraph()
            p_sub.space_before = Pt(8)
            self._render_inline_text(p_sub, subtitle, default_color=self.theme["accent"], default_size=Pt(16.5), is_rtl=is_rtl)
            p_sub.alignment = PP_ALIGN.CENTER

        # 3. Three Next-Steps Action Cards horizontally (Each is a single shape with text_frame!)
        steps = [
            ("01", "توقيع اتفاقية الشراكة وSLA", "اعتماد الشروط التجارية ومؤشرات جودة الخدمة"),
            ("02", "بدء ورش العمل وربط الـ APIs", "تسليم مكتبات SDK والتكامل في بيئة الاختبار"),
            ("03", "توريد نقاط البيع وحقن المفاتيح", "تجهيز الأجهزة الميدانية وبروتوكولات DUKPT")
        ] if is_rtl else [
            ("01", "Execute Strategic SLA", "Sign commercial terms and performance metrics"),
            ("02", "API & SDK Integration", "Deliver Android HCE SDKs to engineering team"),
            ("03", "Hardware & Key Injection", "Deploy certified POS terminals and DUKPT keys")
        ]

        card_w = Inches(3.6)
        card_h = Inches(1.5)
        gap = Inches(0.4)
        total_w = card_w * 3 + gap * 2
        start_x = (self.slide_width - total_w) / 2
        c_top = Inches(4.0)

        for idx, (num, h_text, d_text) in enumerate(steps):
            c_idx = (2 - idx) if is_rtl else idx
            cx = start_x + c_idx * (card_w + gap)

            c_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, c_top, card_w, card_h)
            c_card.fill.solid()
            c_card.fill.fore_color.rgb = self.theme["card_bg"]
            c_card.line.color.rgb = self.theme["accent"]
            c_card.line.width = Pt(1.5)

            c_tf = c_card.text_frame
            c_tf.word_wrap = True
            c_tf.margin_left = Inches(0.2)
            c_tf.margin_right = Inches(0.2)
            c_tf.margin_top = Inches(0.2)
            c_tf.margin_bottom = Inches(0.2)
            c_tf.vertical_anchor = MSO_ANCHOR.TOP

            p1 = c_tf.paragraphs[0]
            action_title = f"{num} — {h_text}" if is_rtl else f"[{num}]  {h_text}"
            self._render_inline_text(p1, action_title, default_color=self.theme["accent"], default_size=Pt(13.5), is_rtl=is_rtl, base_bold=True)
            self._apply_paragraph_rtl(p1, is_rtl)

            p2 = c_tf.add_paragraph()
            p2.space_before = Pt(6)
            close_d_col = RGBColor(203, 213, 225) if self.is_dark_canvas else self.theme["body"]
            self._render_inline_text(p2, d_text, default_color=close_d_col, default_size=Pt(11), is_rtl=is_rtl)
            self._apply_paragraph_rtl(p2, is_rtl)

        # 4. Footer contact banner
        ft_top = Inches(5.8)
        ft_box = slide.shapes.add_textbox(Inches(1.0), ft_top, self.slide_width - Inches(2.0), Inches(0.8))
        ft_tf = ft_box.text_frame
        ft_tf.word_wrap = True
        p_ft = ft_tf.paragraphs[0]
        contact = contact_info or (f"{self.organization}  •  فريق هندسة التكنولوجيا المالية والحلول التجارية" if is_rtl else f"{self.organization}  •  FinTech Solutions")
        self._render_inline_text(p_ft, contact, default_color=RGBColor(148, 163, 184), default_size=Pt(11.5), is_rtl=is_rtl)
        p_ft.alignment = PP_ALIGN.CENTER

        return slide

    def save(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.filename)), exist_ok=True)
        self.prs.save(self.filename)
        return self.filename
