"""
colors.py — Single source of truth for all dashboard colors.

One coordinated, muted palette shared with the companion DMAIC deck
(../healthcare-burnout-dmaic/build.js uses the same hex values) so the two
pieces read as one designed body of work rather than two different color
languages. Categorical hues were chosen as a family (similar chroma/
lightness band) rather than maximum-contrast primaries, then validated with
the data-viz skill's CVD/contrast checker (scripts/validate_palette.js).
"""

# ── Brand — dominant + neutral + accent ───────────────────────
DOMINANT       = "#0B3D42"  # deep teal navy — headers, dark slides/panels
DOMINANT_DARK  = "#062A2E"  # darkest variant
NEUTRAL        = "#5C7A78"  # muted secondary text/ink
LIGHT_TINT     = "#E4EDEC"  # card backgrounds, light panels
ACCENT         = "#C1603C"  # muted terracotta — sparing use + Accountability driver

# Single-series charts (a scatter or trend line with no categorical split —
# every mark is "just a unit," not a member of the 4-driver legend) use this,
# never a driver hue. Borrowing e.g. the Accountability color for an
# un-legended chart falsely implies that chart is "about" Accountability.
SERIES_NEUTRAL = DOMINANT

# ── Chart chrome & ink ─────────────────────────────────────────
SURFACE      = "#FCFCFB"
PAGE_PLANE   = "#F9F9F7"
INK_PRIMARY  = "#0B0B0B"
INK_SECONDARY= "#52514E"
INK_MUTED    = "#898781"
GRID         = "#E1E0D9"
BASELINE     = "#C3C2B7"

# ── Root-cause driver categories — one coordinated muted family ──
# (the four "unmotivating characteristics" from the DMAIC analysis)
# Validated as a set: scripts/validate_palette.js "#0F98A0,#C1603C,#6B4C95,#A9832E"
DRIVER_WORKLOAD       = "#0F98A0"  # muted teal
DRIVER_ACCOUNTABILITY = ACCENT     # "#C1603C" muted terracotta — reuses the brand accent
DRIVER_REWARD         = "#6B4C95"  # muted plum
DRIVER_SAFETY         = "#A9832E"  # muted ochre

DRIVER_COLORS = {
    "Workload & Staffing": DRIVER_WORKLOAD,
    "Accountability":      DRIVER_ACCOUNTABILITY,
    "Reward":               DRIVER_REWARD,
    "Safety":                DRIVER_SAFETY,
}
DRIVER_ORDER = list(DRIVER_COLORS.keys())

# ── Rotation cadence — reuses 3 of the 4 driver hues on purpose ──
# (same coordinated family everywhere in the app, rather than a second,
# unrelated categorical palette — one visual language, not two)
ROTATION_COLORS = {
    "Daily":    DRIVER_WORKLOAD,       # "#0F98A0"
    "Weekly":   DRIVER_REWARD,         # "#6B4C95"
    "Half-Day": DRIVER_SAFETY,         # "#A9832E"
}
ROTATION_ORDER = ["Daily", "Weekly", "Half-Day"]

# ── Status palette (reserved — never used for a category) ────────
# Muted traffic-light logic, validated as a set:
# scripts/validate_palette.js "#3E8C5E,#C99A3E,#A8453A"
STATUS_GOOD     = "#3E8C5E"  # Rolled Out / on track
STATUS_WARNING  = "#C99A3E"  # Piloting — WARN on contrast: always paired with a direct label
STATUS_CRITICAL = "#A8453A"  # Not Started / at risk — the only red in the app, muted not neon

INITIATIVE_STATUS_COLORS = {
    "Rolled Out":  STATUS_GOOD,
    "Piloting":    STATUS_WARNING,
    "Not Started": STATUS_CRITICAL,
}

# ── Shift-boundary events — reuse driver hues, not new colors ────
# A late arrival reads as a staffing/coverage-readiness gap (Workload);
# an early departure reads as a skipped-closing-task gap (Accountability).
SHIFT_ARRIVED_LATE = DRIVER_WORKLOAD        # "#0F98A0"
SHIFT_LEFT_EARLY   = DRIVER_ACCOUNTABILITY  # "#C1603C"

# ── Sequential (single hue, light -> dark) for magnitude/heat ────
# Built from the brand teal, ending at the dominant navy.
SEQUENTIAL_TEAL = ["#D6EEEF", "#9FD3D5", "#5FB3B6", "#0F98A0", "#0B3D42"]
