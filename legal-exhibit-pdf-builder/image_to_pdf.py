"""
image_to_pdf.py — Place images uniformly on PDF pages with captions.

Supports: JPG/JPEG, PNG, HEIC, AVI (exported as frame sequence)

Usage:
    python image_to_pdf.py                        # Interactive mode (prompts you)
    python image_to_pdf.py --input /path/to/imgs  # Auto-load a folder
    python image_to_pdf.py --help                 # Show all options

Each image is resized uniformly to fit a fixed cell, with its caption printed
below it. Pages are filled left-to-right, top-to-bottom.
"""

import argparse
import io
import os
import sys
import tempfile
from pathlib import Path

# ── Third-party imports (checked at runtime so the error message is friendly) ─

def _require(pkg, install_name=None):
    import importlib
    try:
        return importlib.import_module(pkg)
    except ImportError:
        name = install_name or pkg
        sys.exit(f"Missing package '{name}'. Run:  pip install {name}")

# ── Page / layout constants ───────────────────────────────────────────────────

PAGE_W_PT  = 8.5 * 72   # Letter width  in points
PAGE_H_PT  = 11.0 * 72  # Letter height in points
MARGIN_PT  = 36          # 0.5 in margins
CAPTION_H  = 28          # Points reserved below each image for caption text
GAP        = 12          # Gap between cells (horizontal and vertical)
HEADER_H   = 32          # Height reserved at top of every page for title
FOOTER_H   = 20          # Height reserved at bottom of every page for page number

# ── Supported extensions ──────────────────────────────────────────────────────

IMG_EXTS   = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
HEIC_EXTS  = {".heic", ".heif"}
VIDEO_EXTS = {".avi", ".mp4", ".mov", ".mkv"}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def convert_heic_to_pil(path: Path):
    """Return a PIL Image from a HEIC/HEIF file."""
    pillow_heif = _require("pillow_heif", "pillow-heif")
    pillow_heif.register_heif_opener()
    Image = _require("PIL.Image", "Pillow")
    from PIL import Image as PILImage
    return PILImage.open(path).convert("RGB")


def extract_avi_frames(path: Path, every_n: int = 1) -> list:
    """
    Extract frames from a video file.
    Returns a list of (PIL.Image, label) tuples.
    every_n: keep every Nth frame (1 = every frame, 30 = ~1 fps for 30fps video).
    """
    cv2 = _require("cv2", "opencv-python")
    from PIL import Image as PILImage

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        print(f"  [warning] Could not open video: {path.name}")
        return []

    total   = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    results = []
    idx     = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % every_n == 0:
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img   = PILImage.fromarray(rgb)
            label = f"{path.stem}  frame {idx + 1}/{total}"
            results.append((img, label))
        idx += 1

    cap.release()
    print(f"  Extracted {len(results)} frames from {path.name} "
          f"(every {every_n} frame(s), {total} total)")
    return results


def pil_to_bytes(img) -> bytes:
    """Convert a PIL Image to JPEG bytes."""
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def collect_images(source_paths: list[Path], every_n: int = 1) -> list:
    """
    Walk source_paths (files or directories) and return a list of
    (caption: str, img_bytes: bytes) tuples, sorted by name.
    """
    from PIL import Image as PILImage  # noqa: F401 — ensure Pillow present

    entries = []

    def process_file(p: Path):
        ext = p.suffix.lower()
        if ext in IMG_EXTS:
            from PIL import Image as PI
            img     = PI.open(p).convert("RGB")
            caption = p.stem
            entries.append((caption, pil_to_bytes(img)))
            print(f"  Loaded image : {p.name}")
        elif ext in HEIC_EXTS:
            img     = convert_heic_to_pil(p)
            caption = p.stem
            entries.append((caption, pil_to_bytes(img)))
            print(f"  Loaded HEIC  : {p.name}")
        elif ext in VIDEO_EXTS:
            frames = extract_avi_frames(p, every_n=every_n)
            for pil_img, label in frames:
                entries.append((label, pil_to_bytes(pil_img)))
        else:
            print(f"  [skip] Unsupported format: {p.name}")

    for src in source_paths:
        if src.is_dir():
            files = sorted(src.iterdir())
            for f in files:
                if f.is_file():
                    process_file(f)
        elif src.is_file():
            process_file(src)
        else:
            print(f"  [warning] Path not found: {src}")

    return entries


# ─────────────────────────────────────────────────────────────────────────────
# PDF builder
# ─────────────────────────────────────────────────────────────────────────────

def build_pdf(
    entries:     list,          # [(caption, img_bytes), ...]
    output:      Path,
    cols:        int  = 2,
    title:        str       = "",
    page_titles:  list[str] = None,   # per-page titles; falls back to title
    font_size:    int       = 9,
    title_size:   int       = 14,
    page_start:   int       = 1,
):
    """
    Render images uniformly onto letter-sized PDF pages with captions.

    Layout:
      - Optional title on first page
      - Grid of cols × N images per page
      - Each cell = fixed image area + caption row beneath
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader

    # ── Compute cell geometry ─────────────────────────────────────────────

    usable_w = PAGE_W_PT - 2 * MARGIN_PT

    page_titles = page_titles or []
    has_any_title = bool(title or page_titles)

    # Every page has a header (title) and footer (page number)
    header_h = (HEADER_H + GAP) if has_any_title else 0
    footer_h = FOOTER_H + GAP

    # Usable image area height (same on every page)
    usable_img_h = PAGE_H_PT - 2 * MARGIN_PT - header_h - footer_h

    cell_w = (usable_w - (cols - 1) * GAP) / cols
    img_h  = cell_w * 0.75            # 4:3 aspect — images letterboxed into this
    cell_h = img_h + CAPTION_H + GAP  # image + caption + gap

    rows_per_page = max(1, int(usable_img_h / cell_h))
    cells_per_page = rows_per_page * cols

    # Top Y of the image grid (below header, from page top)
    grid_top = PAGE_H_PT - MARGIN_PT - header_h

    # ── Draw ──────────────────────────────────────────────────────────────

    c = canvas.Canvas(str(output), pagesize=letter)
    c.setTitle(title or "Image Document")
    c.setAuthor("image_to_pdf.py")

    page_idx  = 0   # 0-based internal counter
    cell_idx  = 0   # position within current page

    def draw_header_footer():
        """Draw title header and page number footer on the current page."""
        page_num = page_start + page_idx - 1

        # Per-page title overrides the global title; fall back to global
        this_title = (page_titles[page_idx - 1]
                      if page_idx - 1 < len(page_titles)
                      else title)

        # ── Header ──────────────────────────────────────────────────────
        if this_title:
            c.setFont("Helvetica-Bold", title_size)
            c.setFillColor(colors.HexColor("#222222"))
            c.drawCentredString(
                PAGE_W_PT / 2,
                PAGE_H_PT - MARGIN_PT - title_size,
                this_title,
            )
            # Thin rule under title
            rule_y = PAGE_H_PT - MARGIN_PT - title_size - 4
            c.setStrokeColor(colors.HexColor("#aaaaaa"))
            c.setLineWidth(0.5)
            c.line(MARGIN_PT, rule_y, PAGE_W_PT - MARGIN_PT, rule_y)

        # ── Footer ──────────────────────────────────────────────────────
        footer_y = MARGIN_PT - 4
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#666666"))
        c.setStrokeColor(colors.HexColor("#aaaaaa"))
        c.setLineWidth(0.5)
        c.line(MARGIN_PT, MARGIN_PT + 2, PAGE_W_PT - MARGIN_PT, MARGIN_PT + 2)
        c.drawCentredString(PAGE_W_PT / 2, footer_y, f"Page {page_num}")

    def start_page():
        nonlocal page_idx, cell_idx
        cell_idx = 0
        if page_idx > 0:
            c.showPage()
        page_idx += 1
        draw_header_footer()

    start_page()

    for caption, img_bytes in entries:
        # Flip to a new page if this page is full
        if cell_idx >= cells_per_page:
            start_page()

        row = cell_idx // cols
        col = cell_idx % cols

        # Top-left corner of this cell
        x = MARGIN_PT + col * (cell_w + GAP)
        y = grid_top - (row + 1) * img_h - row * (CAPTION_H + GAP)

        # ── Draw image letterboxed into cell_w × img_h ─────────────────

        try:
            ir   = ImageReader(io.BytesIO(img_bytes))
            iw, ih = ir.getSize()
            scale   = min(cell_w / iw, img_h / ih)
            dw, dh  = iw * scale, ih * scale
            dx      = x + (cell_w - dw) / 2   # center horizontally
            dy      = y + (img_h  - dh) / 2   # center vertically

            # Light grey background for the image cell
            c.setFillColor(colors.HexColor("#f0f0f0"))
            c.rect(x, y, cell_w, img_h, fill=1, stroke=0)

            c.drawImage(ir, dx, dy, width=dw, height=dh,
                        preserveAspectRatio=True, mask="auto")
        except Exception as e:
            print(f"  [warning] Could not draw image for '{caption}': {e}")

        # ── Caption ────────────────────────────────────────────────────

        cap_y = y - CAPTION_H + 6      # a few pts above bottom of caption area
        c.setFont("Helvetica", font_size)
        c.setFillColor(colors.HexColor("#333333"))

        # Truncate caption if too wide
        max_chars = int(cell_w / (font_size * 0.52))
        short_cap = (caption[:max_chars - 1] + "…") if len(caption) > max_chars else caption
        c.drawCentredString(x + cell_w / 2, cap_y, short_cap)

        cell_idx += 1

    c.save()
    print(f"\nSaved → {output}  ({page_idx} page(s), {len(entries)} image(s))")


# ─────────────────────────────────────────────────────────────────────────────
# Interactive helper
# ─────────────────────────────────────────────────────────────────────────────

def interactive_mode() -> argparse.Namespace:
    """Prompt the user for settings when no CLI args are given."""
    print("=" * 60)
    print("  Image → PDF  (interactive mode)")
    print("=" * 60)
    print()

    # Source paths
    print("Enter paths to images/folders (one per line).")
    print("Supported: JPG, PNG, HEIC, AVI/MP4/MOV")
    print("Press Enter twice when done.\n")
    paths = []
    while True:
        raw = input("  Path: ").strip()
        if not raw:
            if paths:
                break
            print("  (at least one path is required)")
        else:
            paths.append(Path(raw.strip('"').strip("'")))

    # Output file
    default_out = Path.cwd() / "output.pdf"
    raw_out = input(f"\nOutput PDF path [{default_out}]: ").strip()
    output  = Path(raw_out) if raw_out else default_out

    # Title
    title = input("\nDocument title (optional): ").strip()

    # Columns
    raw_cols = input("\nImages per row [2]: ").strip()
    cols = int(raw_cols) if raw_cols.isdigit() else 2

    # AVI frame sampling
    raw_every = input("\nFor videos, keep every N-th frame [30]: ").strip()
    every_n = int(raw_every) if raw_every.isdigit() else 30

    print("\nPer-page titles (optional). Enter a title for each page, one per line.")
    print("Leave blank to use the same title on all pages. Press Enter twice when done.")
    page_titles = []
    pg = 1
    while True:
        raw_pt = input(f"  Page {pg} title (or blank to stop): ").strip()
        if not raw_pt:
            break
        page_titles.append(raw_pt)
        pg += 1

    raw_pstart = input("\nStarting page number (for master tracker) [1]: ").strip()
    page_start = int(raw_pstart) if raw_pstart.isdigit() else 1

    preview = input("\nOpen PDF automatically when done? [Y/n]: ").strip().lower() != "n"

    ns = argparse.Namespace(
        input=paths,
        output=output,
        title=title,
        page_titles=page_titles,
        cols=cols,
        every_n=every_n,
        font_size=9,
        title_size=14,
        page_start=page_start,
        preview=preview,
    )
    return ns


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Place images uniformly on PDF pages with captions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python image_to_pdf.py                              # interactive
  python image_to_pdf.py --input ~/Photos            # whole folder
  python image_to_pdf.py --input a.jpg b.heic c.avi  # mixed files
  python image_to_pdf.py --input ~/vid.avi --every-n 60  # 1 frame / 2 sec @ 30fps
        """,
    )
    p.add_argument("--input",    nargs="+", type=Path,
                   help="Image files or folders (JPG, PNG, HEIC, AVI, MP4, MOV)")
    p.add_argument("--output",   type=Path, default=Path("output.pdf"),
                   help="Output PDF file (default: output.pdf)")
    p.add_argument("--title",       default="",
                   help="Default title printed on every page header")
    p.add_argument("--page-titles", nargs="+", default=[], dest="page_titles",
                   metavar="TITLE",
                   help="Per-page titles (overrides --title for that page). "
                        "E.g.: --page-titles \"Roof\" \"Basement\" \"Driveway\"")
    p.add_argument("--cols",     type=int, default=2,
                   help="Images per row (default: 2)")
    p.add_argument("--every-n",  type=int, default=30, dest="every_n",
                   help="For videos: keep every N-th frame (default: 30)")
    p.add_argument("--font-size",  type=int, default=9, dest="font_size",
                   help="Caption font size in points (default: 9)")
    p.add_argument("--title-size", type=int, default=14, dest="title_size",
                   help="Title font size in points (default: 14)")
    p.add_argument("--page-start", type=int, default=1, dest="page_start",
                   help="Starting page number (default: 1, set higher to match master tracker)")
    p.add_argument("--preview", action="store_true",
                   help="Open the PDF automatically after saving")
    return p


def main():
    _require("reportlab", "reportlab")
    _require("PIL",       "Pillow")

    parser = parse_args()

    # If no args at all → interactive mode
    if len(sys.argv) == 1:
        args = interactive_mode()
    else:
        args = parser.parse_args()
        if not args.input:
            parser.error("--input is required (or run with no arguments for interactive mode)")

    print(f"\nCollecting images …")
    entries = collect_images(args.input, every_n=args.every_n)

    if not entries:
        sys.exit("No supported images found. Nothing to do.")

    print(f"\nBuilding PDF ({args.cols} column(s)) …")
    build_pdf(
        entries      = entries,
        output       = args.output,
        cols         = args.cols,
        title        = args.title,
        page_titles  = args.page_titles,
        font_size    = args.font_size,
        title_size   = args.title_size,
        page_start   = args.page_start,
    )

    if getattr(args, "preview", False):
        import subprocess, platform
        opener = {"darwin": "open", "win32": "start", "linux": "xdg-open"}.get(
            platform.system().lower(), "xdg-open"
        )
        subprocess.Popen([opener, str(args.output)])


if __name__ == "__main__":
    main()
