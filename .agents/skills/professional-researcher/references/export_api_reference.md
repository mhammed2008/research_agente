# Export Engine API Reference

This document provides Python developers with code examples for invoking the PDF and Word export builders directly within custom scripts.

---

## 1. High-Level Conversion via `convert_file`

The simplest method converts a Markdown or JSON file directly:

```python
from export_engine import convert_file

# Dual export to PDF and DOCX
results = convert_file(
    input_path="research_report.md",
    pdf_path="deliverable.pdf",
    docx_path="deliverable.docx",
    title="Custom Executive Title",
    author="Lead Investigator",
    org="TeknoKeys Intelligence",
    date_str="September 2026"
)

print(results["pdf"])   # Path to output PDF
print(results["docx"])  # Path to output DOCX
```

---

## 2. Low-Level Programmatic PDF Building via `PDFReportBuilder`

```python
from pdf_builder import PDFReportBuilder

builder = PDFReportBuilder(
    filename="executive_brief.pdf",
    title="Core Architecture Evaluation",
    subtitle="Analysis of Microservices vs Monolith",
    author="Principal Architect",
    organization="Enterprise Engineering",
    date_str="September 2026"
)

# 1. Generate Cover Page
builder.build_cover_page()

# 2. Add Content
builder.add_heading("1. Executive Summary", level=1)
builder.add_paragraph("This evaluation provides empirical benchmarks...")

# 3. Add Callout
builder.add_callout(
    text="Deploying without rate-limiting increases latency under load.",
    title="CAPACITY WARNING",
    callout_type="warning"
)

# 4. Add Comparison Table
headers = ["Architecture", "Throughput (RPS)", "P99 Latency"]
rows = [
    ["Monolith", "12,400", "42ms"],
    ["Microservices", "18,900", "78ms"],
    ["Serverless", "8,200", "240ms"]
]
builder.add_table(headers, rows)

# 5. Compile to PDF
builder.save()
```

---

## 3. Low-Level Programmatic Word Building via `DocxReportBuilder`

```python
from docx_builder import DocxReportBuilder

builder = DocxReportBuilder(
    filename="executive_brief.docx",
    title="Core Architecture Evaluation",
    subtitle="Analysis of Microservices vs Monolith",
    author="Principal Architect",
    organization="Enterprise Engineering",
    date_str="September 2026"
)

builder.build_cover_page()
builder.add_heading("1. Executive Summary", level=1)
builder.add_paragraph("This evaluation provides empirical benchmarks...")

builder.add_callout(
    text="Hardware Security Modules must be certified under FIPS 140-3 Level 3.",
    title="COMPLIANCE REQUIREMENT",
    callout_type="important"
)

headers = ["Vendor", "FIPS Level", "Unit Price"]
rows = [
    ["Vendor A", "FIPS 140-2 Level 3", "$12,000"],
    ["Vendor B", "FIPS 140-3 Level 4", "$18,500"]
]
builder.add_table(headers, rows)

builder.save()
```
