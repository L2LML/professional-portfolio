"""
colors.py — Single source of truth for all dashboard colors.

Dominant/neutral/tint reuse the exact hex values used in the companion
../dtw-it-center-pm-toolkit/ Word/Excel documents (navy header rows, steel
labels, light-blue row shading) so the dashboard reads as the same designed
body of work as the charters and workbooks, not a different visual language.
Categorical and sequential values were chosen as a set, then validated with
the data-viz skill's CVD/contrast checker (scripts/validate_palette.js):
  node scripts/validate_palette.js "#B5651D,#00A3A3" --mode light   -> ALL PASS
  node scripts/validate_palette.js "#3E8C5E,#C99A3E,#A8453A" --mode light -> PASS (yellow WARN on contrast, always paired with a direct label)
"""

# ── Brand — matches the toolkit's Word/Excel documents exactly ───
DOMINANT      = "#1F3864"  # navy — matches docx/xlsx header fill
DOMINANT_DARK = "#122140"
NEUTRAL       = "#44546A"  # steel — matches docx/xlsx label text
LIGHT_TINT    = "#D9E2F3"  # matches docx/xlsx alternating-row shading
ACCENT        = DOMINANT

# Single-series charts (no categorical split) use this, never a project hue —
# borrowing e.g. the Construction color for an un-legended chart would falsely
# imply that chart is "about" Construction.
SERIES_NEUTRAL = DOMINANT

# ── Chart chrome & ink ─────────────────────────────────────────
SURFACE       = "#FCFCFB"
PAGE_PLANE    = "#F9F9F7"
INK_PRIMARY   = "#0B0B0B"
INK_SECONDARY = "#3F3F3F"
INK_MUTED     = "#8A8A86"
GRID          = "#E3E3E0"
BASELINE      = "#C7C7C2"

# ── Project identity — categorical, fixed order, validated as a set ──
PROJECT_CONSTRUCTION = "#B5651D"  # muted burnt orange — Construction/Infrastructure
PROJECT_TECHNOLOGY   = "#00A3A3"  # muted teal — Technology

PROJECT_COLORS = {
    "Construction/Infrastructure": PROJECT_CONSTRUCTION,
    "Technology": PROJECT_TECHNOLOGY,
}
PROJECT_ORDER = ["Construction/Infrastructure", "Technology"]
PROJECT_SHORT_NAMES = {
    "Construction/Infrastructure": "Data Center & NOC Build-Out",
    "Technology": "Network & Systems Modernization",
}

# ── Status palette (reserved — never used for a category) ────────
# Same validated triad used across the portfolio's other dashboards.
STATUS_GOOD     = "#3E8C5E"  # Green / on track
STATUS_WARNING  = "#C99A3E"  # Yellow / at risk — WARN on contrast: always paired with a direct label
STATUS_CRITICAL = "#A8453A"  # Red / off track — the only red in the app, muted not neon

STATUS_COLORS = {"Green": STATUS_GOOD, "Yellow": STATUS_WARNING, "Red": STATUS_CRITICAL}
STATUS_ORDER = ["Green", "Yellow", "Red"]

RAG_FROM_TEXT_KEYWORDS = [
    ("red", STATUS_CRITICAL), ("yellow", STATUS_WARNING), ("amber", STATUS_WARNING),
    ("green", STATUS_GOOD),
]

# ── Sequential (single hue, light -> dark) for magnitude — risk score heat ──
# Built from the brand navy: light tint through to the dominant navy.
# (Categorical lightness-band/chroma-floor checks don't apply to a sequential
# ramp — only lightness monotonicity does; this ramp is monotonically
# decreasing in L from D9E2F3 -> 1F3864.)
SEQUENTIAL_NAVY = ["#D9E2F3", "#A8BEDD", "#5D7FB0", "#33518A", "#1F3864"]


def status_color(label: str) -> str:
    """Map a free-text RAG status string (e.g. 'Yellow — 6 days behind') to its hex."""
    low = (label or "").lower()
    for keyword, color in RAG_FROM_TEXT_KEYWORDS:
        if keyword in low:
            return color
    return INK_MUTED
