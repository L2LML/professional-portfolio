"""
colors.py — Single source of truth for all dashboard colors.

Every page imports from here so the same concept is always
represented by the same color across the entire dashboard.
"""

# ── Brand ─────────────────────────────────────────────────────
NAVY        = "#1E2761"   # primary — titles, dominant bars
BLUE        = "#0284C7"   # secondary — highlights, trends
LIGHT_BG    = "#F4F7FF"   # page background
CARD_BG     = "#FFFFFF"
GRID        = "#E2E8F0"
TEXT_DARK   = "#1A1A2E"
TEXT_MID    = "#64748B"

# ── Semantic (same meaning everywhere) ───────────────────────
GREEN   = "#047857"   # good / paid / on track / low risk
AMBER   = "#D97706"   # watch / aging / moderate
RED     = "#DC2626"   # bad / denied / overdue / high risk
GRAY    = "#94A3B8"   # neutral / expired / withdrawn
PURPLE  = "#7C3AED"   # variable / investment products

# ── Claim status (used on every page that shows status) ──────
STATUS_COLORS = {
    "paid":         NAVY,
    "approved":     GREEN,
    "under_review": BLUE,
    "pending":      AMBER,
    "denied":       RED,
    "withdrawn":    GRAY,
}

# ── Policy types (same color whenever a product appears) ─────
PRODUCT_COLORS = {
    "Term Life":      GRAY,     # temporary — no cash value
    "Whole Life":     NAVY,     # permanent flagship
    "Universal Life": BLUE,     # permanent flexible
    "Variable Life":  PURPLE,   # permanent investment-linked
    "Final Expense":  GREEN,    # small permanent
}

# ── Aging flags ───────────────────────────────────────────────
AGING_COLORS = {
    "ON TRACK": GREEN,
    "AGING":    AMBER,
    "OVERDUE":  RED,
}

# ── Green→Amber→Red scale (for continuous risk metrics) ──────
RISK_SCALE = [
    [0.0, GREEN],
    [0.5, AMBER],
    [1.0, RED],
]

# ── Sequential blue scale (for volume/revenue metrics) ───────
BLUE_SCALE = [
    [0.0, "#DBEAFE"],
    [1.0, NAVY],
]

# ── Agents — qualitative (8 distinct, accessible colors) ─────
AGENT_COLORS = [
    NAVY, BLUE, GREEN, AMBER, RED, PURPLE, "#0891B2", "#B45309"
]
