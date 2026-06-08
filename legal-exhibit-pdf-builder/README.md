# Legal Exhibit PDF Builder

A Python automation tool that compiles evidence documents, photos, and receipts from an Excel tracker into a single paginated PDF exhibit package — complete with cover page, table of contents, exhibit headers, and page stamps. Built for administrative and legal filings.

---

## Overview

Managing dozens of photos, receipts, estimates, and documents for a legal or administrative filing is tedious and error-prone. This tool automates the entire assembly process:

1. Read an **Excel tracker** (exhibit log) to know what files to include and in what order
2. Pull in **images and PDFs** from a source folder (supports JPG, PNG, HEIC, HEIF, PDF, TIFF, BMP, WEBP)
3. Build a **paginated PDF** where each exhibit gets its own labeled page(s) with a header and caption
4. Write **page numbers back** into the tracker spreadsheet automatically

The result is a professional, court-ready exhibit package generated in seconds.

---

## Features

- 📋 **Excel-driven** — exhibit order, titles, and status all controlled from a spreadsheet
- 📸 **HEIC/HEIF support** — handles iPhone photos natively via `pillow-heif`
- 📄 **Mixed media** — seamlessly combines images and PDF documents in one output
- 🏷️ **Auto-headers** — each exhibit gets a labeled header with exhibit number and title
- 🔢 **Page numbering** — footer page numbers written back to the Excel tracker automatically
- 🔍 **Status filtering** — only includes exhibits marked as ready (✅ submitted, 📸 found, 📄 attached)
- 📐 **Layout options** — single or multi-column image layout via `--cols` flag
- 👁️ **Preview mode** — `--preview` flag to inspect output before finalizing
- ⚡ **Fast rebuild** — re-run anytime the tracker or files change; output regenerates in seconds

---

## Scripts

| Script | Purpose |
|--------|---------|
| `build_appeal_pdf.py` | Main builder — reads Excel tracker, assembles full exhibit PDF |
| `image_to_pdf.py` | Utility — places individual images onto letter-size PDF pages with captions |

---

## Requirements

```
reportlab>=4.0.0
Pillow>=10.0.0
pillow-heif>=0.15.0
opencv-python>=4.8.0
```

Install with:
```bash
pip3 install -r requirements.txt
```

---

## Usage

```bash
# Basic run — uses default paths from script
python3 build_appeal_pdf.py

# Custom output file
python3 build_appeal_pdf.py --output MyExhibits.pdf

# Two-column image layout
python3 build_appeal_pdf.py --cols 2

# Preview mode
python3 build_appeal_pdf.py --preview

# All options
python3 build_appeal_pdf.py --cols 2 --output Appeal_Exhibits.pdf --preview
```

---

## Excel Tracker Format

The script reads a sheet named **"Master Exhibit Log"** with the following key columns:

| Column | Purpose |
|--------|---------|
| Exhibit # | Exhibit label (e.g. A, B, 1, 2) |
| Title | Exhibit title shown in PDF header |
| File Name | Source file name in the photos folder |
| Status | Controls inclusion (✅ = include, blank = skip) |
| PDF Page | Written back automatically after build |

---

## Output

The generated PDF includes:
- **Exhibit header** on each page showing exhibit number and title
- **Captions** under each image
- **Page numbers** in the footer
- **Mixed content** — photos and document PDFs flow together seamlessly

---

## Use Cases

- Property tax assessment appeals
- Insurance claims documentation
- Legal exhibit packages
- Administrative hearing filings
- Any scenario requiring organized, paginated evidence compilation

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| `reportlab` | PDF generation and layout |
| `Pillow` | Image processing and format conversion |
| `pillow-heif` | iPhone HEIC/HEIF photo support |
| `opencv-python` | Image preprocessing |
| `openpyxl` | Excel tracker read/write |
| `Python 3.10+` | Runtime |

---

## Skills Demonstrated

- Python scripting and automation
- PDF generation with ReportLab
- Excel integration (read/write via openpyxl)
- File system traversal and multi-format media handling
- CLI tool design with argparse
- Practical problem-solving for real administrative workflows
