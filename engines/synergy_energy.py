import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ── Column Names (from column_map.txt) ───────────────────────────────────────
COL_ROCE      = 'roce'
COL_OPM       = 'opm'
COL_SALES_3YR = 'sales_var_3yrs'
COL_EPS_3YR   = 'eps_var_3yrs'
COL_SECTOR    = 'sector'

# ── InnovaTech Benchmarks ─────────────────────────────────────────────────────
INNOVATECH_ROCE       = 22.1
INNOVATECH_OPM        = 12.8
INNOVATECH_SALES_CAGR = 20.0

SECTOR_FIT_MAP = {
    'it - software':       100,
    'it - services':       100,
    'fintech':              80,
    'telecom - services':   60,
    'telecom - equipments': 45,
    'finance':              40,
    'power':                25,
}

# ── Synergy Weights ───────────────────────────────────────────────────────────
WEIGHTS = {
    'roce':         0.25,
    'opm':          0.25,
    'growth':       0.20,
    'sector_fit':   0.20,
    'eps_momentum': 0.10,
}

# ── Safe Number Reader ────────────────────────────────────────────────────────
def _n(row, col, default=0.0):
    """Safely read a number from a row. Returns default if missing or NaN."""
    val = row.get(col, default)
    try:
        f = float(val)
        return default if np.isnan(f) else f
    except:
        return default

# ── Individual Score Functions ────────────────────────────────────────────────
def get_roce_score(row):
    roce_val = _n(row, COL_ROCE)                        
    score = (roce_val / INNOVATECH_ROCE) * 100          
    return min(max(score, 0), 100)                      

def get_opm_score(row):
    opm_val = _n(row, COL_OPM)
    score = (opm_val / INNOVATECH_OPM) * 100
    return min(max(score, 0), 100)

def get_growth_score(row):
    sales_val = _n(row, COL_SALES_3YR)
    score = (sales_val / INNOVATECH_SALES_CAGR) * 100
    return min(max(score, 0), 100)

def get_eps_score(row):
    eps_val = _n(row, COL_EPS_3YR)
    score = (eps_val / 20.0) * 100
    return min(max(score, 0), 100)

def get_sector_score(row):
    sector_val = str(row.get(COL_SECTOR, '')).strip().lower()
    return SECTOR_FIT_MAP.get(sector_val, 30)

# ── Main Synergy Score Function ───────────────────────────────────────────────
def compute_synergy_score(row):
    """
    Synergy Score: 0-100. HIGHER = BETTER FIT with InnovaTech.

    Weights:
        ROCE         25%
        OPM          25%
        Sales Growth 20%
        Sector Fit   20%
        EPS Momentum 10%
    """
    roce_score   = get_roce_score(row)
    opm_score    = get_opm_score(row)
    growth_score = get_growth_score(row)
    sector_score = get_sector_score(row)
    eps_score    = get_eps_score(row)

    final_score = (
        (roce_score   * WEIGHTS['roce'])         +
        (opm_score    * WEIGHTS['opm'])          +
        (growth_score * WEIGHTS['growth'])       +
        (sector_score * WEIGHTS['sector_fit'])   +
        (eps_score    * WEIGHTS['eps_momentum'])
    )

    return round(float(final_score), 2)

# ── Label Function ────────────────────────────────────────────────────────────
def get_synergy_label(score):
    if   score >= 75: return "🟢 High Synergy"
    elif score >= 55: return "🟡 Moderate Synergy"
    elif score >= 35: return "🟠 Low Synergy"
    else:             return "🔴 Misaligned"

# ── Reasons Function ──────────────────────────────────────────────────────────
def get_synergy_reasons(row):
    reasons = []

    roce_val   = _n(row, COL_ROCE)
    opm_val    = _n(row, COL_OPM)
    sales_val  = _n(row, COL_SALES_3YR)
    eps_val    = _n(row, COL_EPS_3YR)
    sector_val = str(row.get(COL_SECTOR, '')).strip()
    sector_fit = SECTOR_FIT_MAP.get(sector_val.lower(), 30)

    # ROCE reason
    if roce_val >= INNOVATECH_ROCE:
        reasons.append(f"✅ ROCE {roce_val:.1f}% meets InnovaTech's {INNOVATECH_ROCE}% benchmark")
    else:
        reasons.append(f"⚠️ ROCE {roce_val:.1f}% below InnovaTech's {INNOVATECH_ROCE}% benchmark")

    # OPM reason
    if opm_val >= INNOVATECH_OPM:
        reasons.append(f"✅ Margin {opm_val:.1f}% aligned with InnovaTech's {INNOVATECH_OPM}% profile")
    else:
        reasons.append(f"⚠️ Margin {opm_val:.1f}% below InnovaTech — may dilute group margins")

    # Sales growth reason
    if sales_val >= 15:
        reasons.append(f"✅ 3-year revenue growth of {sales_val:.0f}% — strong momentum")
    elif sales_val < 0:
        reasons.append(f"⚠️ Revenue declined {abs(sales_val):.0f}% over 3 years")
    else:
        reasons.append(f"ℹ️ Revenue grew {sales_val:.0f}% over 3 years — moderate growth")

    # Sector reason
    if sector_fit >= 80:
        reasons.append(f"✅ Sector '{sector_val}' is core to InnovaTech's transformation goals")
    elif sector_fit < 50:
        reasons.append(f"ℹ️ Sector '{sector_val}' is adjacent — synergy requires integration effort")
    else:
        reasons.append(f"ℹ️ Sector '{sector_val}' has moderate strategic overlap with InnovaTech")

    # EPS reason
    if eps_val >= 0:
        reasons.append(f"✅ EPS grew {eps_val:.0f}% over 3 years — shareholders benefiting")
    else:
        reasons.append(f"⚠️ EPS declined {abs(eps_val):.0f}% over 3 years — value erosion signal")

    return reasons

# ── Self Test ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    tests = [
        {
            'label': 'High Synergy',
            COL_ROCE: 25, COL_OPM: 15, COL_SALES_3YR: 25,
            COL_EPS_3YR: 22, COL_SECTOR: 'it - software'
        },
        {
            'label': 'Medium Synergy',
            COL_ROCE: 15, COL_OPM: 10, COL_SALES_3YR: 10,
            COL_EPS_3YR: 5, COL_SECTOR: 'fintech'
        },
        {
            'label': 'Low Synergy',
            COL_ROCE: 5, COL_OPM: 3, COL_SALES_3YR: -5,
            COL_EPS_3YR: -10, COL_SECTOR: 'power'
        },
    ]

    print("SYNERGY ENGINE — SELF TEST")
    print("=" * 50)
    for t in tests:
        score = compute_synergy_score(t)
        label = get_synergy_label(score)
        print(f"\n{t['label']}: {score}/100  {label}")
        for reason in get_synergy_reasons(t):
            print(f"   {reason}")

    print("\n" + "=" * 50)
    print("✅ Expected: High ~80+   Medium ~50   Low ~15-20")