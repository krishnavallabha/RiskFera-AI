# config.py
# ============================================================
# RISKFERA AI — Single Source of Truth
# All InnovaTech financials and acquisition constraints live here.
# NO other file should hardcode numbers — always import from here.
# ============================================================

# ── INNOVATECH SYSTEMS LTD — Real FY2025 Financials ─────────────────────────
INNOVATECH = {

    # Financials from hackathon brief
    "revenue_cr":            610,      # FY2025 Revenue (₹ Cr)
    "net_profit_cr":         78,       # FY2025 Net Profit (₹ Cr)
    "operating_margin_pct":  12.8,     # FY2025 Operating Margin %
    "roce_pct":              22.1,     # FY2025 ROCE %
    "cash_reserves_cr":      95,       # Available cash
    "debt_equity_ratio":     0.30,     # Current D/E
    "current_pe":            24.5,     # Current P/E multiple

    # Derived metrics (computed from brief data)
    "revenue_cagr_pct":      20.5,     # (610/420)^0.5 - 1  [FY23→FY25]
    "profit_cagr_pct":       30.2,     # (78/46)^0.5 - 1    [FY23→FY25]
    "market_cap_cr":         1911,     # Net Profit × P/E = 78 × 24.5

    # Risk profile
    "risk_appetite":         "moderate",
    #Signal weights (based on real dataset analysis):
    "risk_signal_maxpts": {
    "quarterly_profit_var":  20,   
    "profit_var_3yr":        30,   
    "ebitda_var_3yr":        25,
    "operating_margin":      15,
    "dividend_yield":         5,
    "eps_var_3yr":            5,
},
#   Total                           : max 100 pts
#

    # ── Synergy Engine Benchmarks ────────────────────────────────────────────
    # Targets are scored relative to these InnovaTech benchmarks.
    # A target matching or exceeding these scores 100% on that signal.
    "target_roce":           22.1,     # InnovaTech's own ROCE — the bar to clear
    "target_opm":            12.8,     # InnovaTech's own OPM
    "target_sales_cagr":     20.0,     # InnovaTech's revenue CAGR

    # ── Synergy Engine Weights ───────────────────────────────────────────────
    # Weights derived from InnovaTech's 4 stated strategic goals:
    #   1. Strengthen AI & software product portfolio   → sector_fit
    #   2. Enter adjacent industries via IT             → sector_fit + growth
    #   3. Improve recurring revenue share              → opm + roce
    #   4. Unlock revenue & cost synergies              → roce + eps_momentum
    "synergy_weights": {
        "roce":          0.25,   # Capital efficiency — core to product-led shift
        "opm":           0.25,   # Margin quality — recurring revenue proxy
        "growth":        0.20,   # Revenue momentum in target's business
        "sector_fit":    0.20,   # Strategic alignment with InnovaTech's goals
        "eps_momentum":  0.10,   # Quality of earnings signal
    },
    #Signal weights for feasibility engine:
    "feasibility_signal_maxpts": {
    "budget_check":        40,   # Signal 1 — mar_cap_rscr × 1.25 vs ₹180Cr
    "pe_attractiveness":   25,   # Signal 2 — p_e vs 24.5x
    "equity_dilution":     20,   # Signal 3 — calculated from mar_cap_rscr
    "integration":         15,   # Signal 4 — 3yrs_return
},
#   Total                      : 100 pts

    # ── Final Score Weights ──────────────────────────────────────────────────
    # Risk carries highest weight — moderate risk appetite means quality gate first.
    # Synergy next — strategic fit is the core acquisition rationale.
    # Feasibility last — it's a hard constraint, not a preference.
    "final_weights": {
        "risk":          0.40,   # Applied as (100 - risk_score)
        "synergy":       0.35,
        "feasibility":   0.25,
    },
}

# ── ACQUISITION CONSTRAINTS — From Hackathon Brief ───────────────────────────
ACQUISITION_CONSTRAINTS = {
    "max_deal_value_cr":           180,    # Hard ceiling on total deal size
    "min_noncash_pct":             0.40,   # Min 40% must be equity swap or earn-out
    "max_cash_outflow_cr":         108,    # = 180 × (1 - 0.40)
    "max_integration_months":      6,      # Board-mandated integration window
    "founder_retention_years":     2,      # If target is private/founder-led
    "synergy_realization_months":  12,     # Tangible benefits must appear within 1 year
    "innovatech_market_cap_cr":    1911,   # Used for equity swap dilution calculation
    "acquisition_premium_assumed": 0.25,   # 25% premium over market cap (standard Indian IT)
}

# ── SECTOR FIT MAP ───────────────────────────────────────────────────────────
# Maps dataset sector strings → strategic fit score (0–100).
#   UPDATE THESE after running data_loader.py and checking printed sector names.
#     The keys must exactly match the sector strings in your cleaned dataset.
SECTOR_FIT_MAP = {
    # Core — directly aligned with AI/product transformation goals
    "it services":              100,
    "it":                       100,
    "saas":                     100,
    "software":                  95,

    # High — IT as strong enabler, recurring revenue potential
    "fintech":                   80,
    "financial technology":      80,

    # Medium — infrastructure + software overlap
    "telecommunications":        60,
    "telecom":                   60,

    # Adjacent — energy tech / IoT / software angle possible but weaker
    "energy":                    40,
    "energy & power":            40,
    "power":                     35,

    # Default fallback for unrecognised sectors
    "__default__":               30,
}

# ── HISTORICAL FINANCIALS (FY23–FY25) ───────────────────────────────────────
# Included for reference and deck slides. Not used directly by engines.
INNOVATECH_HISTORY = {
    "FY2023": {"revenue_cr": 420, "net_profit_cr": 46, "opm_pct": 11.0, "roce_pct": 18.2},
    "FY2024": {"revenue_cr": 515, "net_profit_cr": 63, "opm_pct": 12.2, "roce_pct": 20.5},
    "FY2025": {"revenue_cr": 610, "net_profit_cr": 78, "opm_pct": 12.8, "roce_pct": 22.1},
}



