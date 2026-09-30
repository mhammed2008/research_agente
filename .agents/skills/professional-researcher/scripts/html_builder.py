"""
HTML Report Generator for Professional Researcher (v2.1).
Generates publication-grade, self-contained HTML research reports with:
- Full Native Arabic (RTL) & English (LTR) typography
- Google Fonts 'Cairo', 'Inter', and 'JetBrains Mono'
- Interactive, client-side Mermaid.js diagram rendering
- GitHub-style callout alerts ([!NOTE], [!TIP], [!IMPORTANT], [!WARNING])
- Responsive desktop reading cards & clean A4 print styles for PDF generation
"""

import os
import re
import html

class HTMLReportBuilder:
    def __init__(self, title, subtitle="", author="", organization="", date_str="", is_rtl=False):
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.organization = organization
        self.date_str = date_str
        self.is_rtl = is_rtl
        self.blocks_html = []

    def _format_inline(self, text):
        """Converts basic markdown inline formatting to HTML."""
        if not text:
            return ""
        # Escape raw HTML
        escaped = html.escape(text)
        # Bold: **text**
        escaped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)
        # Italic: *text*
        escaped = re.sub(r'\*(.+?)\*', r'<em>\1</em>', escaped)
        # Inline code: `code`
        escaped = re.sub(r'`([^`]+)`', r'<code>\1</code>', escaped)
        return escaped

    def add_heading(self, text, level=1):
        formatted = self._format_inline(text)
        slug = re.sub(r'[^\w\- ]', '', text.lower()).replace(' ', '-')
        self.blocks_html.append(f'<h{level} id="{slug}">{formatted}</h{level}>')

    def add_paragraph(self, text):
        formatted = self._format_inline(text)
        self.blocks_html.append(f'<p>{formatted}</p>')

    def add_bullet(self, text, indent=0):
        formatted = self._format_inline(text)
        margin = indent * 20
        style = f' style="margin-right: {margin}px;"' if self.is_rtl else f' style="margin-left: {margin}px;"'
        self.blocks_html.append(f'<li{style}>{formatted}</li>')

    def add_callout(self, text, title="NOTE", callout_type="note"):
        formatted = self._format_inline(text)
        clean_title = html.escape(title)
        
        type_classes = {
            "note": "callout-note",
            "tip": "callout-tip",
            "important": "callout-important",
            "warning": "callout-warning"
        }
        cls = type_classes.get(callout_type.lower(), "callout-note")
        
        self.blocks_html.append(f'''
<div class="callout {cls}">
  <div class="callout-title">{clean_title}</div>
  <div class="callout-body">{formatted}</div>
</div>''')

    def add_blockquote(self, text):
        formatted = self._format_inline(text)
        self.blocks_html.append(f'<blockquote><p>{formatted}</p></blockquote>')

    def add_code_block(self, text, language=""):
        lang = language.strip().lower()
        if lang == "mermaid":
            badge_text = "مخطط هيكلي ومعماري (Architecture Flowchart)" if self.is_rtl else "Interactive Architecture Diagram"
            self.blocks_html.append(f'''
<div class="mermaid-card">
  <div class="mermaid-card-header">
    <span class="mermaid-badge"><span class="badge-icon">📊</span> {badge_text}</span>
  </div>
  <div class="mermaid-container">
    <pre class="mermaid">
{text}
    </pre>
  </div>
</div>''')
        else:
            escaped_code = html.escape(text)
            self.blocks_html.append(f'<div class="code-container"><pre><code class="language-{lang}">{escaped_code}</code></pre></div>')

    def add_table(self, headers, rows):
        th_cells = "".join([f'<th>{self._format_inline(h)}</th>' for h in headers])
        tr_rows = []
        for row in rows:
            td_cells = "".join([f'<td>{self._format_inline(str(cell))}</td>' for cell in row])
            tr_rows.append(f'<tr>{td_cells}</tr>')
        
        table_html = f'''
<div class="table-container">
  <table>
    <thead><tr>{th_cells}</tr></thead>
    <tbody>{"".join(tr_rows)}</tbody>
  </table>
</div>'''
        self.blocks_html.append(table_html)

    def add_image(self, path, alt=""):
        escaped_alt = html.escape(alt)
        self.blocks_html.append(f'''
<div class="figure-container">
  <img src="{path}" alt="{escaped_alt}" />
  {f'<div class="figure-caption">{escaped_alt}</div>' if escaped_alt else ''}
</div>''')

    def add_hr(self):
        self.blocks_html.append('<hr class="divider" />')

    def render(self):
        lang = "ar" if self.is_rtl else "en"
        direction = "rtl" if self.is_rtl else "ltr"
        font_family = "'Cairo', -apple-system, sans-serif" if self.is_rtl else "'Inter', -apple-system, sans-serif"
        align = "right" if self.is_rtl else "left"
        border_side = "right" if self.is_rtl else "left"

        content_body = "\n".join(self.blocks_html)

        html_template = f'''<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(self.title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  document.addEventListener("DOMContentLoaded", function() {{
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'base',
      securityLevel: 'loose',
      fontFamily: '"Cairo", "Inter", -apple-system, sans-serif',
      themeVariables: {{
        fontFamily: '"Cairo", "Inter", -apple-system, sans-serif',
        fontSize: '13px',
        primaryColor: '#eff6ff',
        primaryBorderColor: '#3b82f6',
        primaryTextColor: '#0f172a',
        lineColor: '#475569',
        secondaryColor: '#f8fafc',
        tertiaryColor: '#f1f5f9',
        edgeLabelBackground: '#ffffff',
        clusterBkg: '#f8fafc',
        clusterBorder: '#cbd5e1',
        actorBkg: '#1e293b',
        actorTextColor: '#ffffff',
        actorBorder: '#0f172a',
        actorLineColor: '#64748b',
        signalColor: '#2563eb',
        signalTextColor: '#0f172a',
        labelBoxBkgColor: '#eff6ff',
        labelBoxBorderColor: '#3b82f6',
        labelTextColor: '#1e40af',
        loopTextColor: '#0f172a',
        noteBkgColor: '#fffbeb',
        noteBorderColor: '#f59e0b',
        noteTextColor: '#92400e'
      }},
      flowchart: {{
        curve: 'basis',
        padding: 16,
        useMaxWidth: true,
        htmlLabels: true
      }},
      sequence: {{
        showSequenceNumbers: true,
        useMaxWidth: true,
        actorMargin: 50,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35
      }}
    }});
  }});
</script>
<style>
  @page {{
    size: A4 portrait;
    margin: 18mm 14mm 18mm 14mm;
  }}

  * {{
    box-sizing: border-box;
  }}

  html {{
    direction: {direction};
    background: #f8fafc;
    margin: 0;
    padding: 0;
  }}

  body {{
    font-family: {font_family};
    color: #1e293b;
    background: #ffffff;
    line-height: 1.7;
    font-size: 10pt;
    margin: 0;
    padding: 0;
    direction: {direction};
    text-align: {align};
    overflow-wrap: break-word;
  }}

  @media screen {{
    body {{
      max-width: 900px;
      margin: 30px auto;
      padding: 48px 56px;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
    }}
  }}

  @media print {{
    body {{
      max-width: 100%;
      margin: 0;
      padding: 0;
      border: none;
      box-shadow: none;
      background: #ffffff;
    }}
    .mermaid-card {{
      border: 1px solid #e2e8f0;
      break-inside: avoid;
      page-break-inside: avoid;
      margin: 14px 0;
      padding: 14px 16px;
    }}
    .mermaid-container svg {{
      max-height: 650px !important;
      max-width: 100% !important;
      height: auto !important;
    }}
    table, .callout, pre {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}
    h1, h2, h3 {{
      break-after: avoid;
      page-break-after: avoid;
    }}
  }}

  .header-block {{
    border-bottom: 3px solid #2563eb;
    padding-bottom: 20px;
    margin-bottom: 28px;
  }}

  .badge {{
    display: inline-block;
    background: #2563eb;
    color: #ffffff;
    font-size: 8.5pt;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 6px;
    margin-bottom: 10px;
  }}

  h1 {{
    color: #0f172a;
    font-size: 18pt;
    font-weight: 800;
    margin: 0 0 8px 0;
    line-height: 1.35;
  }}

  .subtitle {{
    color: #475569;
    font-size: 11pt;
    margin-bottom: 14px;
    font-weight: 600;
  }}

  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 10px;
    font-size: 8.5pt;
    color: #64748b;
    background: #f1f5f9;
    padding: 10px 14px;
    border-radius: 8px;
    margin-top: 14px;
  }}

  h2 {{
    color: #0f172a;
    font-size: 13.5pt;
    font-weight: 700;
    margin-top: 28px;
    margin-bottom: 12px;
    border-{border_side}: 4px solid #2563eb;
    padding-{border_side}: 12px;
    line-height: 1.4;
  }}

  h3 {{
    color: #1e293b;
    font-size: 11pt;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 8px;
  }}

  p {{
    margin-top: 0;
    margin-bottom: 12px;
    color: #334155;
  }}

  :not(pre) > code {{
    font-family: 'JetBrains Mono', Consolas, monospace;
    background: #f1f5f9;
    color: #0f172a;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 9pt;
  }}

  .code-container pre {{
    font-family: 'JetBrains Mono', Consolas, monospace;
    background: #0f172a;
    color: #f8fafc;
    padding: 14px 18px;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 8.5pt;
    line-height: 1.5;
    direction: ltr;
    text-align: left;
  }}

  .code-container pre code {{
    background: transparent;
    color: #f8fafc;
    padding: 0;
    border-radius: 0;
    font-size: inherit;
  }}

  .mermaid-card {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px 22px;
    margin: 22px 0;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
  }}

  .mermaid-card-header {{
    display: flex;
    align-items: center;
    justify-content: flex-start;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px dashed #e2e8f0;
  }}

  .mermaid-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    font-size: 8.5pt;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 6px;
  }}

  .mermaid-container {{
    text-align: center;
    overflow-x: auto;
    background: transparent;
    padding: 8px 4px;
  }}

  .mermaid-container svg {{
    max-width: 100% !important;
    height: auto !important;
    font-family: 'Cairo', 'Inter', -apple-system, sans-serif !important;
  }}

  .mermaid-container .node text,
  .mermaid-container .node .label,
  .mermaid-container .edgeLabel,
  .mermaid-container .label text,
  .mermaid-container text.actor,
  .mermaid-container .messageText,
  .mermaid-container .noteText {{
    font-family: 'Cairo', 'Inter', -apple-system, sans-serif !important;
  }}

  .table-container {{
    overflow-x: auto;
    margin: 18px 0;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 8.5pt;
  }}

  th {{
    background: #0f172a;
    color: #ffffff;
    font-weight: 700;
    padding: 10px 12px;
    text-align: {align};
    border: 1px solid #0f172a;
  }}

  td {{
    padding: 9px 12px;
    border: 1px solid #cbd5e1;
    color: #334155;
    text-align: {align};
  }}

  tr:nth-child(even) td {{
    background: #f8fafc;
  }}

  /* Callouts */
  .callout {{
    padding: 14px 18px;
    border-radius: 8px;
    margin: 16px 0;
    border-{border_side}: 4px solid;
  }}

  .callout-title {{
    font-weight: 800;
    font-size: 9pt;
    margin-bottom: 4px;
  }}

  .callout-body {{
    font-size: 9pt;
    color: #334155;
  }}

  .callout-note {{
    background: #eff6ff;
    border-{border_side}-color: #2563eb;
    color: #1e40af;
  }}

  .callout-tip {{
    background: #ecfdf5;
    border-{border_side}-color: #059669;
    color: #065f46;
  }}

  .callout-important {{
    background: #fff1f2;
    border-{border_side}-color: #e11d48;
    color: #9f1239;
  }}

  .callout-warning {{
    background: #fffbeb;
    border-{border_side}-color: #d97706;
    color: #92400e;
  }}

  blockquote {{
    border-{border_side}: 4px solid #94a3b8;
    margin: 14px 0;
    padding: 8px 16px;
    background: #f8fafc;
    color: #475569;
    font-style: italic;
  }}

  hr.divider {{
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 28px 0;
  }}

  li {{
    margin-bottom: 6px;
    color: #334155;
  }}
</style>
</head>
<body>

<div class="header-block">
  <div class="badge">{html.escape(self.organization or "RESEARCH WHITEPAPER")}</div>
  <h1>{html.escape(self.title)}</h1>
  {f'<div class="subtitle">{html.escape(self.subtitle)}</div>' if self.subtitle else ''}
  <div class="meta-grid">
    <div><strong>{"الباحث:" if self.is_rtl else "Author:"}</strong> {html.escape(self.author or "Research Team")}</div>
    <div><strong>{"الجهة:" if self.is_rtl else "Organization:"}</strong> {html.escape(self.organization or "Enterprise")}</div>
    <div><strong>{"التاريخ:" if self.is_rtl else "Date:"}</strong> {html.escape(self.date_str or "")}</div>
  </div>
</div>

{content_body}

</body>
</html>'''
        return html_template
