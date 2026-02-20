# 🏁 RISKFERA AI — Milestone-Based Parallel Development Plan
### Every milestone is independent. Pick one, build it, merge it.

---

## HOW THIS WORKS

Each milestone is a **self-contained unit of work** with:
- Clear inputs (what you need before starting)
- Clear outputs (what you deliver when done)
- Zero dependency on what your partner is currently building

Both of you look at the milestone board, pick one that's unblocked, and build it.
When done, commit and pick the next unblocked one.
No waiting. No blocking.

---

## 🗺️ FULL MILESTONE MAP

```
FOUNDATION
├── M1: Project Setup & Folder Structure        [~1 hr]  ← Do this TOGETHER first
└── M2: Data Loader & Cleaned CSV               [~2 hrs] ← Unblocks everything

ENGINES (all three run in parallel once M2 is done)
├── M3: Risk Engine                             [~2 hrs]
├── M4: Synergy Engine                          [~2 hrs]
└── M5: Feasibility Engine                      [~2 hrs]

SCORING & CONFIG
├── M6: config.py — Innovatech Profile          [~1 hr]  ← Can start Day 1, no dependencies
└── M7: Final Scoring & Ranking Pipeline        [~1.5 hrs] ← Needs M3, M4, M5

DASHBOARD (builds in layers, each layer is one milestone)
├── M8:  Dashboard — Ranked Table + Sidebar     [~2 hrs] ← Needs M7
├── M9:  Dashboard — Company Deep Dive Panel    [~2 hrs] ← Needs M8
├── M10: Dashboard — Radar Chart                [~1.5 hrs] ← Needs M8
└── M11: Dashboard — Top 5 Comparison + Export [~1 hr]  ← Needs M8

DECK (each slide group is one milestone)
├── M12: Deck — Problem + Framework Slides (1–4)       [~2 hrs] ← No dependencies
├── M13: Deck — Engine Methodology Slides (5–7)        [~2 hrs] ← Needs M3,M4,M5 output
├── M14: Deck — Target Deep Dive Slides (8–10)         [~3 hrs] ← Needs M7 + external research
├── M15: Deck — Valuation + Deal Structure (11–12)     [~2 hrs] ← Needs M14
├── M16: Deck — PMI + Risks + Recommendation (13–15)   [~2 hrs] ← Needs M14
└── M17: Deck — Final Polish & Consistency Check       [~1 hr]  ← Needs all deck milestones

SUBMISSION
└── M18: README + Zip + Upload                  [~1 hr]  ← Needs everything
```

---

## 📋 DEPENDENCY CHART

```
M1 (Setup)
 └── M2 (Data Loader)
      ├── M3 (Risk Engine)      ─────┐
      ├── M4 (Synergy Engine)   ─────┤──► M7 (Final Score) ──► M8 (Dashboard Table)
      ├── M5 (Feasibility Engine)────┘                              ├── M9  (Deep Dive)
      └── M6 (Config) ──────────────►  M7                          ├── M10 (Radar Chart)
                                                                    └── M11 (Top5 + Export)

M12 (Deck slides 1–4) ── no dependencies, start anytime
M13 (Deck slides 5–7) ── needs M3, M4, M5 output printed
M14 (Deck slides 8–10)── needs M7 output + external research on chosen company
M15 (Deck slides 11–12)─ needs M14
M16 (Deck slides 13–15)─ needs M14
M17 (Final polish) ────── needs M12–M16

M18 (Submit) ──────────── needs everything
```

**Milestones with zero dependencies (start immediately on Day 1):**
- M1, M6, M12

---

## 📦 MILESTONE DETAILS

---

### M1 — Project Setup & Folder Structure
**⏱ ~1 hour | Do together at the start | Unblocks: everything**

**Inputs:** Nothing — just your laptops

**Outputs:**
- GitHub repo created and both people cloned
- Full folder structure created
- All libraries installed and confirmed working
- Both people can run `python --version` and `streamlit hello` without errors

**Exactly what to do:**
```bash
# Person creating the repo
git init riskfera-ai
cd riskfera-ai
mkdir data engines scoring dashboard output deck

# Create empty placeholder files so git tracks folders
touch data/.gitkeep engines/.gitkeep scoring/.gitkeep
touch dashboard/.gitkeep output/.gitkeep deck/.gitkeep

# Create requirements.txt
echo "pandas
numpy
scikit-learn
plotly
streamlit
openpyxl
xlrd" > requirements.txt

# Install
pip install -r requirements.txt

# Commit
git add .
git commit -m "M1: project structure"
git push

# Other person
git clone <repo-url>
pip install -r requirements.txt
```

**Done when:** Both people can `git pull` and see the folder structure. Libraries installed on both machines.

---

### M2 — Data Loader & Cleaned CSV
**⏱ ~2 hours | Needs: M1 | Unblocks: M3, M4, M5, M7, M8**

**Inputs:** `data/dataset.xlsx` (the provided hackathon file)

**Outputs:**
- `data/cleaned_targets.csv` — standardized, numeric, no NaN values
- Console print of: exact column names, sector list, market cap range, company count
- `data/column_map.txt` — one-line mapping of original → cleaned column names

**Complete code:**
```python
# data_loader.py
import pandas as pd
import numpy as np
import os

def load_and_clean(path='data/dataset.xlsx'):
    df = pd.read_excel(path)

    print("=" * 60)
    print(f"RAW: {len(df)} companies, {len(df.columns)} columns")
    print("RAW COLUMNS:", df.columns.tolist())

    # Standardize column names
    original_cols = df.columns.tolist()
    df.columns = (df.columns
                  .str.strip()
                  .str.lower()
                  .str.replace(r'[^\w\s]', '', regex=True)
                  .str.replace(r'\s+', '_', regex=True)
                  .str.replace('₹', '', regex=False)
                  .str.replace('%', 'pct', regex=False))

    clean_cols = df.columns.tolist()
    print("\nCLEAN COLUMNS:", clean_cols)
    print("\nSECTORS:\n", df['sector'].value_counts() if 'sector' in df.columns else "sector col not found")

    # Save column map for other modules to reference
    with open('data/column_map.txt', 'w') as f:
        for orig, clean in zip(original_cols, clean_cols):
            f.write(f"{orig}  →  {clean}\n")

    # Force numeric on all non-name, non-sector columns
    skip_cols = ['sector'] + [c for c in df.columns if 'name' in c or 'company' in c]
    for col in df.columns:
        if col not in skip_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Derived columns
    sales_col  = next((c for c in df.columns if 'sales' in c and 'quarterly' in c), None)
    profit_col = next((c for c in df.columns if 'profit' in c and 'quarterly' in c
                       and 'variance' not in c), None)

    if sales_col and profit_col:
        df['annual_revenue_est'] = df[sales_col]  * 4
        df['annual_profit_est']  = df[profit_col] * 4
        df['profit_margin_est']  = (df['annual_profit_est'] / df['annual_revenue_est'] * 100).round(2)
        print(f"\nDerived columns added using: {sales_col}, {profit_col}")
    else:
        print("\n⚠️  Could not auto-detect sales/profit columns. Check column_map.txt and add manually.")

    # Flag data-limited companies
    df['data_limited'] = df.isnull().sum(axis=1) > 3

    # Fill remaining NaNs with column median
    df = df.fillna(df.median(numeric_only=True))

    # Market cap summary
    mcap_col = next((c for c in df.columns if 'market' in c and 'cap' in c), None)
    if mcap_col:
        print(f"\nMARKET CAP RANGE: ₹{df[mcap_col].min():.0f}Cr — ₹{df[mcap_col].max():.0f}Cr")
        feasible = df[df[mcap_col] * 1.25 <= 180]
        print(f"FEASIBLE TARGETS (deal ≤ ₹180Cr): {len(feasible)} companies")

    print(f"\nDATA LIMITED (>3 missing fields): {df['data_limited'].sum()} companies")
    print("=" * 60)

    return df

if __name__ == '__main__':
    df = load_and_clean()
    df.to_csv('data/cleaned_targets.csv', index=False)
    print(f"\n✅ Saved: data/cleaned_targets.csv ({len(df)} rows)")
```

**Done when:** `data/cleaned_targets.csv` exists, has no NaN in numeric columns, and `data/column_map.txt` shows all column mappings. Share `column_map.txt` in your group chat immediately — both partners need it.

---

### M3 — Risk Engine
**⏱ ~2 hours | Needs: M2 (column names only) | Unblocks: M7, M13**

**Inputs:** `data/column_map.txt` (to confirm exact column names)

**Outputs:** `engines/risk_engine.py` — fully working, tested

**How to verify it works before real data:**
```bash
python engines/risk_engine.py
# Should print scores for 3 test companies: ~10, ~45, ~80
```

**Complete code:**
```python
# engines/risk_engine.py
import numpy as np

# ── UPDATE THESE after checking data/column_map.txt ──────────────────────────
COL_QTR_PROFIT_VAR  = 'quarterly_profit_variance_pct'
COL_PROFIT_VAR_3YR  = 'profit_variance_3_years_pct'
COL_EBIDT_VAR_3YR   = 'ebidt_variance_3_years_pct'
COL_OPM             = 'operating_profit_margin_pct'
COL_DIV_YIELD       = 'dividend_yield_pct'
COL_EPS_VAR_3YR     = 'eps_variance_3_years_pct'

def _n(row, col):
    """Safe numeric extraction."""
    v = row.get(col, 0)
    try:
        f = float(v)
        return 0.0 if np.isnan(f) else f
    except:
        return 0.0

def compute_risk_score(row):
    """
    Risk Score: 0–100. HIGHER = RISKIER.
    ┌──────────────────────────────────┬────────┐
    │ Signal                           │ Max pts│
    ├──────────────────────────────────┼────────┤
    │ Quarterly Profit Variance        │  30    │
    │ 3-Year Profit Variance           │  25    │
    │ 3-Year EBIDT Variance            │  20    │
    │ Operating Profit Margin          │  15    │
    │ Dividend Yield (distress proxy)  │   5    │
    │ EPS 3-Year Variance              │   5    │
    └──────────────────────────────────┴────────┘
    """
    s = 0

    # Signal 1 — Quarterly Profit Variance (30 pts)
    qpv = abs(_n(row, COL_QTR_PROFIT_VAR))
    s += 30 if qpv > 50 else 15 if qpv > 25 else 5 if qpv > 10 else 0

    # Signal 2 — 3-Year Profit Variance (25 pts)
    pv3 = _n(row, COL_PROFIT_VAR_3YR)
    s += 25 if pv3 < -20 else 15 if pv3 < -10 else 8 if pv3 < 0 else 0

    # Signal 3 — 3-Year EBIDT Variance (20 pts)
    e3 = _n(row, COL_EBIDT_VAR_3YR)
    s += 20 if e3 < -15 else 12 if e3 < -5 else 5 if e3 < 0 else 0

    # Signal 4 — Operating Profit Margin (15 pts)
    opm = _n(row, COL_OPM)
    s += 15 if opm < 0 else 10 if opm < 3 else 5 if opm < 7 else 0

    # Signal 5 — Dividend Yield distress proxy (5 pts)
    dy = _n(row, COL_DIV_YIELD)
    s += 5 if dy > 8 else 3 if (dy == 0 and opm < 5) else 0

    # Signal 6 — EPS 3-Year Variance (5 pts)
    eps = _n(row, COL_EPS_VAR_3YR)
    s += 5 if eps < -20 else 2 if eps < 0 else 0

    return min(int(s), 100)

def get_risk_label(score):
    if   score < 20: return "🟢 Low Risk"
    elif score < 40: return "🟡 Moderate Risk"
    elif score < 60: return "🟠 Elevated Risk"
    else:            return "🔴 High Risk"

def get_risk_reasons(row):
    reasons = []
    qpv = abs(_n(row, COL_QTR_PROFIT_VAR))
    pv3 = _n(row, COL_PROFIT_VAR_3YR)
    e3  = _n(row, COL_EBIDT_VAR_3YR)
    opm = _n(row, COL_OPM)
    eps = _n(row, COL_EPS_VAR_3YR)
    dy  = _n(row, COL_DIV_YIELD)

    if qpv <= 10 and pv3 >= 0 and opm >= 10:
        reasons.append("✅ Stable earnings with no major red flags")
    if qpv > 25:
        reasons.append(f"⚠️ Quarterly profit swung {qpv:.0f}% — unpredictable earnings")
    if pv3 < -10:
        reasons.append(f"⚠️ Profit declined {abs(pv3):.0f}% over 3 years")
    if e3 < -10:
        reasons.append(f"⚠️ EBITDA contracted {abs(e3):.0f}% over 3 years")
    if opm < 5:
        reasons.append(f"⚠️ Operating margin of {opm:.1f}% is dangerously thin")
    if eps < -15:
        reasons.append(f"⚠️ EPS fell {abs(eps):.0f}% over 3 years — value destruction")
    if dy > 8:
        reasons.append(f"⚠️ Dividend yield {dy:.1f}% unusually high — possible value trap")
    if not reasons:
        reasons.append("ℹ️ No major flags — standard due diligence applies")
    return reasons

def get_risk_breakdown(row):
    qpv = abs(_n(row, COL_QTR_PROFIT_VAR))
    pv3 = _n(row, COL_PROFIT_VAR_3YR)
    e3  = _n(row, COL_EBIDT_VAR_3YR)
    opm = _n(row, COL_OPM)
    dy  = _n(row, COL_DIV_YIELD)
    eps = _n(row, COL_EPS_VAR_3YR)
    return {
        'Quarterly Profit Variance': 30 if qpv>50 else 15 if qpv>25 else 5 if qpv>10 else 0,
        '3-Year Profit Variance':    25 if pv3<-20 else 15 if pv3<-10 else 8 if pv3<0 else 0,
        '3-Year EBIDT Variance':     20 if e3<-15  else 12 if e3<-5   else 5 if e3<0  else 0,
        'Operating Margin':          15 if opm<0   else 10 if opm<3   else 5 if opm<7  else 0,
        'Dividend Yield Proxy':      5  if dy>8    else 3  if (dy==0 and opm<5) else 0,
        'EPS 3-Year Trend':          5  if eps<-20 else 2  if eps<0   else 0,
    }

# ── SELF TEST ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    tests = [
        {'label': 'Low Risk',    COL_QTR_PROFIT_VAR:5,  COL_PROFIT_VAR_3YR:18,  COL_EBIDT_VAR_3YR:22,  COL_OPM:18,  COL_DIV_YIELD:1.5, COL_EPS_VAR_3YR:20},
        {'label': 'Medium Risk', COL_QTR_PROFIT_VAR:28, COL_PROFIT_VAR_3YR:-8,  COL_EBIDT_VAR_3YR:-3,  COL_OPM:8,   COL_DIV_YIELD:3.0, COL_EPS_VAR_3YR:-5},
        {'label': 'High Risk',   COL_QTR_PROFIT_VAR:65, COL_PROFIT_VAR_3YR:-35, COL_EBIDT_VAR_3YR:-22, COL_OPM:-2,  COL_DIV_YIELD:10,  COL_EPS_VAR_3YR:-30},
    ]
    print("RISK ENGINE — SELF TEST")
    print("=" * 50)
    for t in tests:
        score = compute_risk_score(t)
        print(f"{t['label']}: {score}/100  {get_risk_label(score)}")
        for r in get_risk_reasons(t): print(f"   {r}")
        print()
    print("✅ Expected: Low~10  Medium~40  High~80+")
```

**Done when:** Self-test prints three scores roughly matching Low/Medium/High expectations.

---

### M4 — Synergy Engine
**⏱ ~2 hours | Needs: M2 (column names) + M6 (config) | Unblocks: M7, M13**

**Inputs:** `data/column_map.txt`, `config.py`

**Outputs:** `engines/synergy_engine.py` — fully working, tested

**Complete code:**
```python
# engines/synergy_engine.py
import numpy as np, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import INNOVATECH, SECTOR_FIT_MAP

# ── UPDATE after checking column_map.txt ─────────────────────────────────────
COL_ROCE        = 'roce_pct'
COL_OPM         = 'operating_profit_margin_pct'
COL_SALES_3YR   = 'sales_variance_3_years_pct'
COL_EPS_3YR     = 'eps_variance_3_years_pct'
COL_SECTOR      = 'sector'

def _n(row, col, default=0.0):
    v = row.get(col, default)
    try:
        f = float(v)
        return default if np.isnan(f) else f
    except: return default

def compute_synergy_score(row, config=INNOVATECH):
    """
    Synergy Score: 0–100. HIGHER = BETTER FIT with InnovaTech.
    Calibrated against real InnovaTech FY2025 benchmarks.

    ┌────────────────────────────────────┬────────┐
    │ Signal                             │ Weight │
    ├────────────────────────────────────┼────────┤
    │ ROCE vs InnovaTech 22.1% benchmark │  25%   │
    │ OPM  vs InnovaTech 12.8% benchmark │  25%   │
    │ 3-Year Sales Growth                │  20%   │
    │ Sector Strategic Fit               │  20%   │
    │ EPS 3-Year Momentum                │  10%   │
    └────────────────────────────────────┴────────┘
    """
    w = config['synergy_weights']

    roce   = max(0.0, _n(row, COL_ROCE))
    opm    = max(0.0, _n(row, COL_OPM))
    sales3 = _n(row, COL_SALES_3YR)
    eps3   = _n(row, COL_EPS_3YR)
    sector = str(row.get(COL_SECTOR, '')).strip().lower()

    roce_score   = min(100, (roce   / config['target_roce'])        * 100)
    opm_score    = min(100, (opm    / config['target_opm'])         * 100)
    growth_score = min(100, max(0,  (sales3 / config['target_sales_cagr']) * 100))
    sector_score = SECTOR_FIT_MAP.get(sector, 30)
    eps_score    = min(100, max(0,  (eps3 / 20) * 100))

    total = (w['roce']         * roce_score  +
             w['opm']          * opm_score   +
             w['growth']       * growth_score +
             w['sector_fit']   * sector_score +
             w['eps_momentum'] * eps_score)

    return round(float(total), 2)

def get_synergy_label(score):
    if   score >= 75: return "🟢 High Synergy"
    elif score >= 55: return "🟡 Moderate Synergy"
    elif score >= 35: return "🟠 Low Synergy"
    else:             return "🔴 Misaligned"

def get_synergy_reasons(row, config=INNOVATECH):
    reasons = []
    roce   = _n(row, COL_ROCE)
    opm    = _n(row, COL_OPM)
    sales3 = _n(row, COL_SALES_3YR)
    eps3   = _n(row, COL_EPS_3YR)
    sector = str(row.get(COL_SECTOR, '')).strip()
    fit    = SECTOR_FIT_MAP.get(sector.lower(), 30)

    if roce >= config['target_roce']:
        reasons.append(f"✅ ROCE {roce:.1f}% meets InnovaTech's {config['target_roce']}% benchmark")
    else:
        reasons.append(f"⚠️ ROCE {roce:.1f}% below InnovaTech's {config['target_roce']}% benchmark")
    if opm >= config['target_opm']:
        reasons.append(f"✅ Margin {opm:.1f}% aligned with InnovaTech's {config['target_opm']}% profile")
    else:
        reasons.append(f"⚠️ Margin {opm:.1f}% below InnovaTech — may dilute group margins post-acquisition")
    if sales3 >= 15:
        reasons.append(f"✅ 3-year revenue growth of {sales3:.0f}% — strong momentum")
    elif sales3 < 0:
        reasons.append(f"⚠️ Revenue declined {abs(sales3):.0f}% over 3 years")
    if fit >= 80:
        reasons.append(f"✅ Sector '{sector}' is core to InnovaTech's transformation goals")
    elif fit < 50:
        reasons.append(f"ℹ️ Sector '{sector}' is adjacent — synergy requires integration effort")
    if not reasons:
        reasons.append("ℹ️ Moderate strategic alignment — evaluate qualitative fit further")
    return reasons

# ── SELF TEST ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    tests = [
        {'label': 'High Synergy',  COL_ROCE:25, COL_OPM:15, COL_SALES_3YR:25, COL_EPS_3YR:22, COL_SECTOR:'IT Services'},
        {'label': 'Med Synergy',   COL_ROCE:15, COL_OPM:10, COL_SALES_3YR:10, COL_EPS_3YR:5,  COL_SECTOR:'Fintech'},
        {'label': 'Low Synergy',   COL_ROCE:5,  COL_OPM:3,  COL_SALES_3YR:-5, COL_EPS_3YR:-10,COL_SECTOR:'Energy'},
    ]
    print("SYNERGY ENGINE — SELF TEST")
    print("=" * 50)
    for t in tests:
        score = compute_synergy_score(t)
        print(f"{t['label']}: {score}/100  {get_synergy_label(score)}")
        for r in get_synergy_reasons(t): print(f"   {r}")
        print()
    print("✅ Expected: High~75+  Medium~50  Low~25")
```

**Done when:** Self-test prints scores matching expectations for all three test cases.

---

### M5 — Feasibility Engine
**⏱ ~2 hours | Needs: M2 (column names) + M6 (config) | Unblocks: M7, M13**

**Inputs:** `data/column_map.txt`, `config.py`

**Outputs:** `engines/feasibility_engine.py` — fully working, tested

**Complete code:**
```python
# engines/feasibility_engine.py
import numpy as np, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import ACQUISITION_CONSTRAINTS, INNOVATECH

# ── UPDATE after checking column_map.txt ─────────────────────────────────────
COL_MCAP     = 'market_capitalisation__cr'
COL_PE       = 'p_e'
COL_RET_3YR  = '3_year_return_pct'

def _n(row, col, default=0.0):
    v = row.get(col, default)
    try:
        f = float(v)
        return default if np.isnan(f) else f
    except: return default

def compute_feasibility_score(row, c=ACQUISITION_CONSTRAINTS):
    """
    Feasibility Score: 0–100. HIGHER = MORE ACQUIRABLE within constraints.

    Hard constraints baked in:
    - Max deal value: ₹180 Cr
    - Min 40% non-cash (equity swap or earn-out)
    - Max cash outflow: ₹108 Cr

    ┌────────────────────────────────────┬────────┐
    │ Signal                             │ Max pts│
    ├────────────────────────────────────┼────────┤
    │ Market Cap vs ₹180Cr budget        │  40    │
    │ P/E vs InnovaTech 24.5x            │  25    │
    │ Equity swap dilution               │  20    │
    │ Integration complexity (3yr return)│  15    │
    └────────────────────────────────────┴────────┘
    """
    s    = 0
    mcap = _n(row, COL_MCAP, 9999)
    deal = mcap * 1.25   # Assume 25% acquisition premium

    # Signal 1 — Budget check (40 pts)
    if   deal <= c['max_deal_value_cr'] * 0.70: s += 40
    elif deal <= c['max_deal_value_cr']:         s += 25
    elif deal <= c['max_deal_value_cr'] * 1.20: s += 10
    # else 0

    # Signal 2 — P/E attractiveness (25 pts)
    pe = _n(row, COL_PE)
    if   pe <= 0:                                 s += 10  # can't assess
    elif pe < 15:                                 s += 25  # undervalued
    elif pe < INNOVATECH['current_pe']:           s += 18  # below InnovaTech = accretive
    elif pe < 35:                                 s += 8   # slightly expensive
    # else 0

    # Signal 3 — Equity swap dilution (20 pts)
    noncash   = deal * c['min_noncash_pct']
    dilution  = noncash / c['innovatech_market_cap_cr']
    if   dilution < 0.03: s += 20
    elif dilution < 0.06: s += 12
    elif dilution < 0.10: s += 5
    # else 0

    # Signal 4 — Integration complexity via 3yr return (15 pts)
    ret3 = _n(row, COL_RET_3YR)
    if   ret3 < 30:  s += 15
    elif ret3 < 60:  s += 8
    else:            s += 3

    return min(int(s), 100)

def get_feasibility_label(score):
    if   score >= 70: return "🟢 Highly Feasible"
    elif score >= 50: return "🟡 Feasible with Structuring"
    elif score >= 30: return "🟠 Stretch Target"
    else:             return "🔴 Not Feasible"

def get_deal_structure(row, c=ACQUISITION_CONSTRAINTS):
    mcap        = _n(row, COL_MCAP)
    deal        = round(mcap * 1.25, 1)
    cash        = round(deal * 0.60, 1)
    noncash     = round(deal * 0.40, 1)
    dilution    = round((noncash / c['innovatech_market_cap_cr']) * 100, 2)
    return {
        'deal_value_cr':    deal,
        'cash_cr':          cash,
        'noncash_cr':       noncash,
        'dilution_pct':     dilution,
        'within_budget':    deal <= c['max_deal_value_cr'],
        'cash_ok':          cash <= c['max_cash_outflow_cr'],
    }

def get_feasibility_reasons(row, c=ACQUISITION_CONSTRAINTS):
    reasons  = []
    mcap     = _n(row, COL_MCAP)
    deal     = mcap * 1.25
    pe       = _n(row, COL_PE)
    dilution = (deal * 0.40) / c['innovatech_market_cap_cr'] * 100

    if deal <= c['max_deal_value_cr']:
        reasons.append(f"✅ Deal value ₹{deal:.0f}Cr fits within ₹180Cr budget")
    else:
        reasons.append(f"⚠️ Deal value ₹{deal:.0f}Cr exceeds ₹180Cr — needs creative structuring")
    if 0 < pe < INNOVATECH['current_pe']:
        reasons.append(f"✅ P/E {pe:.1f}x < InnovaTech {INNOVATECH['current_pe']}x — acquisition is EPS accretive")
    elif pe >= INNOVATECH['current_pe']:
        reasons.append(f"⚠️ P/E {pe:.1f}x above InnovaTech's own multiple — dilutive unless synergies offset")
    if dilution < 5:
        reasons.append(f"✅ Equity swap dilution of {dilution:.1f}% is shareholder-friendly")
    else:
        reasons.append(f"⚠️ Equity dilution of {dilution:.1f}% needs board sign-off")
    return reasons

# ── SELF TEST ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    tests = [
        {'label': 'Easy deal',    COL_MCAP:80,  COL_PE:12,  COL_RET_3YR:20},
        {'label': 'Tight deal',   COL_MCAP:130, COL_PE:22,  COL_RET_3YR:45},
        {'label': 'Infeasible',   COL_MCAP:200, COL_PE:45,  COL_RET_3YR:90},
    ]
    print("FEASIBILITY ENGINE — SELF TEST")
    print("=" * 50)
    for t in tests:
        score = compute_feasibility_score(t)
        deal  = get_deal_structure(t)
        print(f"{t['label']}: {score}/100  {get_feasibility_label(score)}")
        print(f"   Deal: ₹{deal['deal_value_cr']}Cr | Cash: ₹{deal['cash_cr']}Cr | Equity: ₹{deal['noncash_cr']}Cr | Dilution: {deal['dilution_pct']}%")
        for r in get_feasibility_reasons(t): print(f"   {r}")
        print()
    print("✅ Expected: Easy~75+  Tight~50  Infeasible~20")
```

**Done when:** Self-test prints expected scores and deal breakdowns for all three test cases.

---

### M6 — config.py (Innovatech Profile)
**⏱ ~1 hour | Needs: Nothing | Unblocks: M4, M5, M7**

**Inputs:** Hackathon brief (real numbers already known)

**Outputs:** `config.py` — complete, committed to repo

**Complete code:**
```python
# config.py — Single source of truth for all InnovaTech parameters
# ALL other files import from here. Never hardcode numbers elsewhere.

INNOVATECH = {
    # Real FY2025 financials from hackathon brief
    "revenue_cr":            610,
    "net_profit_cr":         78,
    "operating_margin_pct":  12.8,
    "roce_pct":              22.1,
    "revenue_cagr_pct":      20.5,    # (610/420)^0.5 - 1
    "profit_cagr_pct":       30.2,    # (78/46)^0.5 - 1
    "market_cap_cr":         1911,    # 78 × 24.5
    "cash_reserves_cr":      95,
    "debt_equity_ratio":     0.30,
    "current_pe":            24.5,
    "risk_appetite":         "moderate",

    # Benchmarks for Synergy Engine
    "target_roce":           22.1,
    "target_opm":            12.8,
    "target_sales_cagr":     20.0,

    # Synergy weights — tied to InnovaTech's 4 strategic goals
    "synergy_weights": {
        "roce":          0.25,    # Goal: high-margin, capital-efficient business
        "opm":           0.25,    # Goal: improve recurring revenue share
        "growth":        0.20,    # Goal: revenue momentum in adjacent sectors
        "sector_fit":    0.20,    # Goal: AI/product portfolio strengthening
        "eps_momentum":  0.10     # Quality of earnings signal
    },

    # Final score weights
    "final_weights": {
        "risk":          0.40,    # Moderate risk appetite — quality gate is highest priority
        "synergy":       0.35,    # Strategic fit is the core acquisition thesis
        "feasibility":   0.25     # Hard constraint — deal must close within budget
    }
}

ACQUISITION_CONSTRAINTS = {
    "max_deal_value_cr":           180,
    "min_noncash_pct":             0.40,
    "max_cash_outflow_cr":         108,    # 180 × 0.60
    "max_integration_months":      6,
    "founder_retention_years":     2,
    "synergy_realization_months":  12,
    "innovatech_market_cap_cr":    1911,
}

# ── UPDATE sector names after opening dataset.xlsx ───────────────────────────
# Run data_loader.py and check printed SECTORS output
# Then match exact strings from the dataset here
SECTOR_FIT_MAP = {
    "it services":              100,
    "it":                       100,
    "saas":                     100,
    "software":                  95,
    "fintech":                   80,
    "financial technology":      80,
    "telecommunications":        60,
    "telecom":                   60,
    "energy":                    40,
    "energy & power":            40,
    "power":                     35,
    # Add more after seeing actual dataset sectors
}
```

**Done when:** File committed to repo. Both partners can `from config import INNOVATECH` without errors.

---

### M7 — Final Scoring & Ranking Pipeline
**⏱ ~1.5 hours | Needs: M3, M4, M5, M6, M2 | Unblocks: M8, M13, M14**

**Inputs:** `data/cleaned_targets.csv`, all three engines, `config.py`

**Outputs:** `output/ranked_targets.csv`, `output/top5_targets.csv`

**Complete code:**
```python
# scoring/final_score.py
import pandas as pd
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import INNOVATECH
from engines.risk_engine         import compute_risk_score, get_risk_label, get_risk_reasons
from engines.synergy_engine      import compute_synergy_score, get_synergy_label, get_synergy_reasons
from engines.feasibility_engine  import compute_feasibility_score, get_feasibility_label, get_feasibility_reasons, get_deal_structure

def run_model(input_path='data/cleaned_targets.csv', output_path='output/ranked_targets.csv'):
    df = pd.read_csv(input_path)
    w  = INNOVATECH['final_weights']

    print(f"Running RISKFERA on {len(df)} companies...")

    df['risk_score']        = df.apply(compute_risk_score,        axis=1)
    df['synergy_score']     = df.apply(compute_synergy_score,     axis=1)
    df['feasibility_score'] = df.apply(compute_feasibility_score, axis=1)

    df['attractiveness_score'] = (
        w['risk']        * (100 - df['risk_score'])  +
        w['synergy']     * df['synergy_score']        +
        w['feasibility'] * df['feasibility_score']
    ).round(2)

    df = df.sort_values('attractiveness_score', ascending=False).reset_index(drop=True)
    df['rank']              = df.index + 1
    df['risk_label']        = df['risk_score'].apply(get_risk_label)
    df['synergy_label']     = df['synergy_score'].apply(get_synergy_label)
    df['feasibility_label'] = df['feasibility_score'].apply(get_feasibility_label)

    os.makedirs('output', exist_ok=True)
    df.to_csv(output_path, index=False)
    df.head(5).to_csv('output/top5_targets.csv', index=False)

    name_col = next((c for c in df.columns if 'company' in c or 'name' in c), df.columns[0])
    print("\n🏆 TOP 5:")
    print(df[['rank', name_col, 'sector', 'risk_score',
              'synergy_score', 'feasibility_score', 'attractiveness_score']].head(5).to_string(index=False))
    print(f"\n✅ Saved: {output_path}")
    return df

if __name__ == '__main__':
    run_model()
```

**Done when:** Terminal prints a clean Top 5 table with no errors. Both CSV files exist in `output/`.

---

### M8 — Dashboard: Ranked Table + Sidebar
**⏱ ~2 hours | Needs: M7 | Unblocks: M9, M10, M11**

**Inputs:** `output/ranked_targets.csv`

**Outputs:** Working Streamlit app showing ranked table, filters, and live re-ranking

**Complete code:**
```python
# dashboard/app.py  —  START HERE, add more milestones below this
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import INNOVATECH, ACQUISITION_CONSTRAINTS

st.set_page_config(page_title="RISKFERA AI", page_icon="🎯", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0d1b2a; }
[data-testid="stSidebar"]           { background-color: #112240; }
h1, h2, h3                          { color: #f4b942; }
</style>""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:    return pd.read_csv('output/ranked_targets.csv')
    except: st.error("Run scoring/final_score.py first"); return pd.DataFrame()

df_full  = load_data()
name_col = next((c for c in df_full.columns if 'company' in c or 'name' in c), df_full.columns[0]) if not df_full.empty else 'company'

# Header
st.title("🎯 RISKFERA AI")
st.caption("M&A Target Intelligence Platform — InnovaTech Systems")
c1,c2,c3,c4 = st.columns(4)
c1.metric("Companies Screened", len(df_full))
c2.metric("Sectors Covered",    df_full['sector'].nunique() if not df_full.empty else 0)
c3.metric("Max Budget",         "₹180 Cr")
c4.metric("InnovaTech P/E",     "24.5x")
st.divider()

# Sidebar
with st.sidebar:
    st.header("⚙️ Scenario Controls")
    budget   = st.slider("Acquisition Budget (₹ Cr)", 50, 300, 180, 10)
    min_roce = st.slider("Min ROCE Filter (%)", 0, 30, 0, 2)
    sectors  = st.multiselect("Sectors",
                   df_full['sector'].dropna().unique().tolist() if not df_full.empty else [],
                   default=df_full['sector'].dropna().unique().tolist() if not df_full.empty else [])
    st.divider()
    if st.button("⬇️ Export to Excel"):
        df_full.to_excel('output/ranked_targets.xlsx', index=False)
        st.success("Saved!")

# Filter + re-rank
def rerank(df, budget, min_roce, sectors):
    if df.empty: return df
    d = df.copy()
    mcap_col = next((c for c in d.columns if 'market' in c and 'cap' in c), None)
    roce_col = next((c for c in d.columns if 'roce' in c), None)
    if mcap_col: d = d[d[mcap_col] * 1.25 <= budget]
    if roce_col and min_roce > 0: d = d[d[roce_col] >= min_roce]
    if sectors:  d = d[d['sector'].isin(sectors)]
    d = d.sort_values('attractiveness_score', ascending=False).reset_index(drop=True)
    d['rank'] = d.index + 1
    return d

df = rerank(df_full, budget, min_roce, sectors)

# Ranked table
st.subheader(f"📊 Ranked Targets ({len(df)} shown)")
if not df.empty:
    disp = df[['rank', name_col, 'sector', 'risk_score',
               'synergy_score', 'feasibility_score', 'attractiveness_score']].copy()
    disp.columns = ['#', 'Company', 'Sector', 'Risk↓', 'Synergy↑', 'Feasibility↑', 'Score↑']

    def colour(v):
        if not isinstance(v, (int,float)): return ''
        if v >= 65: return 'background-color:#1a4731;color:#00cc88'
        if v >= 40: return 'background-color:#3d3200;color:#f4b942'
        return 'background-color:#3d1a1a;color:#ff4b4b'

    st.dataframe(disp.style.applymap(colour, subset=['Risk↓','Synergy↑','Feasibility↑','Score↑']),
                 use_container_width=True, height=420)
else:
    st.warning("No companies match current filters.")

# ── M9, M10, M11 code gets appended BELOW this line ──────────────────────────
```

**Done when:** `streamlit run dashboard/app.py` loads a coloured table. Budget slider re-sorts companies live.

---

### M9 — Dashboard: Company Deep Dive Panel
**⏱ ~2 hours | Needs: M8 | Unblocks: M10, M11**

**What to add:** Paste this block at the bottom of `app.py`

```python
# ── M9: COMPANY DEEP DIVE ─────────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engines.risk_engine         import get_risk_reasons
from engines.synergy_engine      import get_synergy_reasons
from engines.feasibility_engine  import get_feasibility_reasons, get_deal_structure

st.divider()
st.subheader("🔍 Company Deep Dive")

if not df.empty:
    selected = st.selectbox("Select company:", df[name_col].tolist())
    row = df[df[name_col] == selected].iloc[0]

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Score Breakdown**")
        st.metric("🔴 Risk Score",        f"{row['risk_score']:.0f}/100",   delta="Lower is safer",  delta_color="inverse")
        st.metric("🟢 Synergy Score",     f"{row['synergy_score']:.0f}/100", delta="Higher is better")
        st.metric("🔵 Feasibility Score", f"{row['feasibility_score']:.0f}/100", delta="Higher is better")
        st.metric("⭐ Final Score",        f"{row['attractiveness_score']:.1f}/100")
        if row.get('data_limited', False):
            st.warning("⚠️ Data Limited")

    with col_b:
        st.markdown("**Key Financial Metrics**")
        metrics = {
            'ROCE (%)':         next((c for c in df.columns if 'roce' in c), None),
            'Op. Margin (%)':   next((c for c in df.columns if 'operating_profit' in c), None),
            'Market Cap (₹Cr)': next((c for c in df.columns if 'market' in c and 'cap' in c), None),
            'P/E Ratio':        next((c for c in df.columns if c == 'p_e'), None),
            '3yr Sales Growth': next((c for c in df.columns if 'sales_variance_3' in c), None),
            '3yr Profit Growth':next((c for c in df.columns if 'profit_variance_3' in c), None),
        }
        for label, col in metrics.items():
            val = row.get(col, 'N/A') if col else 'N/A'
            st.write(f"**{label}:** {f'{val:.1f}' if isinstance(val, float) else val}")

    with col_c:
        st.markdown("**Why RISKFERA ranked this company:**")
        reasons = (get_risk_reasons(row)[:1] +
                   get_synergy_reasons(row)[:1] +
                   get_feasibility_reasons(row)[:1])
        for r in reasons:
            st.markdown(f"- {r}")

        st.divider()
        st.markdown("**💼 Indicative Deal Structure**")
        deal = get_deal_structure(row)
        st.write(f"Deal Value: **₹{deal['deal_value_cr']}Cr** {'✅' if deal['within_budget'] else '⚠️'}")
        st.write(f"Cash (60%): **₹{deal['cash_cr']}Cr** {'✅' if deal['cash_ok'] else '⚠️'}")
        st.write(f"Equity (40%): **₹{deal['noncash_cr']}Cr**")
        st.write(f"Dilution: **{deal['dilution_pct']}%** {'✅' if deal['dilution_pct']<5 else '⚠️'}")
```

**Done when:** Clicking any company in the table shows its full metrics, score breakdown, reasons, and deal structure.

---

### M10 — Dashboard: Radar Chart
**⏱ ~1.5 hours | Needs: M8 | Unblocks: nothing**

**What to add:** Paste this inside the `col_b` block of M9, replacing the metrics section, OR add as a new column.

```python
# ── M10: RADAR CHART ─────────────────────────────────────────────────────────
import plotly.graph_objects as go

# Place this inside the deep dive section, in a dedicated column
st.markdown("**Score Radar**")
cats   = ['Earnings\nQuality', 'Strategic\nSynergy', 'Deal\nFeasibility']
vals   = [100 - row['risk_score'], row['synergy_score'], row['feasibility_score']]
fig = go.Figure(go.Scatterpolar(
    r=vals + [vals[0]], theta=cats + [cats[0]],
    fill='toself',
    line_color='#f4b942',
    fillcolor='rgba(244,185,66,0.15)'
))
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0,100]), bgcolor='#112240'),
    paper_bgcolor='#0d1b2a', font_color='white',
    height=260, margin=dict(l=30,r=30,t=20,b=20), showlegend=False
)
st.plotly_chart(fig, use_container_width=True)
```

**Done when:** Radar chart appears in company deep dive for every selected company.

---

### M11 — Dashboard: Top 5 Bar Chart + Score Distribution
**⏱ ~1 hour | Needs: M8 | Unblocks: nothing**

**What to add:** Paste at bottom of `app.py`

```python
# ── M11: TOP 5 COMPARISON + SCORE DISTRIBUTION ───────────────────────────────
import plotly.graph_objects as go
import plotly.express as px

st.divider()
st.subheader("📈 Universe Overview")

ov1, ov2 = st.columns(2)

with ov1:
    top5 = df.head(5)
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name='Earnings Quality', x=top5[name_col],
        y=100-top5['risk_score'], marker_color='#00cc88'))
    fig_bar.add_trace(go.Bar(name='Synergy',          x=top5[name_col],
        y=top5['synergy_score'],  marker_color='#f4b942'))
    fig_bar.add_trace(go.Bar(name='Feasibility',      x=top5[name_col],
        y=top5['feasibility_score'], marker_color='#4a9eff'))
    fig_bar.update_layout(barmode='group', title='Top 5 — Score Comparison',
        paper_bgcolor='#0d1b2a', plot_bgcolor='#0d1b2a',
        font_color='white', height=320)
    st.plotly_chart(fig_bar, use_container_width=True)

with ov2:
    fig_hist = px.histogram(df, x='attractiveness_score', nbins=20,
        title='Score Distribution Across All Targets',
        color_discrete_sequence=['#f4b942'])
    fig_hist.update_layout(paper_bgcolor='#0d1b2a', plot_bgcolor='#0d1b2a',
        font_color='white', height=320)
    st.plotly_chart(fig_hist, use_container_width=True)
```

**Done when:** Dashboard shows grouped bar chart of top 5 and histogram of all scores at the bottom.

---

### M12 — Deck: Slides 1–4 (Problem + Framework)
**⏱ ~2 hours | Needs: Nothing | Unblocks: M13**

**Inputs:** Hackathon brief

**Outputs:** Slides 1–4 complete in PowerPoint/Canva

| Slide | Title | Key Content |
|-------|-------|-------------|
| 1 | Cover | RISKFERA AI · InnovaTech M&A · Team name |
| 2 | The Problem | Why banker networks fail · 2 unanswered questions · Cost of bad sourcing |
| 3 | InnovaTech Profile | FY23–25 table · 4 strategic goals · All 5 constraints (budget, 40% non-cash, 6mo integration, founder retention, 12mo synergy) |
| 4 | RISKFERA Framework | Flow diagram: Dataset → 3 Engines → Score → Top 5 → One Pick |

**Done when:** Slides 1–4 polished, consistent font/colour, committed to shared folder.

---

### M13 — Deck: Slides 5–7 (Engine Methodology + Results)
**⏱ ~2 hours | Needs: M3, M4, M5 self-tests + M7 output | Unblocks: nothing**

**Inputs:** Engine code (to pull signal tables) + `output/top5_targets.csv`

**Outputs:** Slides 5–7 complete

| Slide | Title | Key Content |
|-------|-------|-------------|
| 5 | Risk Engine | Signal table (6 rows: signal · column · max pts · what it detects) |
| 6 | Synergy Engine | Weights table (5 rows) · Why each weight links to InnovaTech goals |
| 7 | Feasibility + Top 5 | Budget constraint logic · Final score formula · Top 5 ranked table with real scores |

**Done when:** Slide 7 shows real company names and real scores from model output.

---

### M14 — Deck: Slides 8–10 (Target Deep Dive)
**⏱ ~3 hours | Needs: M7 output + 2hrs external research | Unblocks: M15, M16**

**This is the most important milestone in the deck.**

**Before starting:** Pick the final target from Top 5. Spend 1–2 hours researching:
- BSE/NSE filings or company website
- Business model, revenue streams, key clients
- Founding team (for founder retention narrative)
- Recent news, partnerships, any red flags

**Outputs:** Slides 8–10 complete

| Slide | Title | Key Content |
|-------|-------|-------------|
| 8 | Target Overview | Company name · Business model · Revenue streams · Team · RISKFERA score breakdown |
| 9 | Strategic Fit + Synergies | Goal-to-capability grid · Revenue synergies · Cost synergies · Tech synergies · Timeline (Year 1 vs Year 2+) |
| 10 | Financial Assessment | Dataset metrics annualized · Trend analysis · InnovaTech vs Target comparison table |

**Done when:** Any judge can understand why this specific company was chosen after reading these 3 slides.

---

### M15 — Deck: Slides 11–12 (Valuation + Deal Structure)
**⏱ ~2 hours | Needs: M14 | Unblocks: nothing**

**Outputs:** Slides 11–12 complete

| Slide | Title | Key Content |
|-------|-------|-------------|
| 11 | Valuation Band | P/E method (15x/20x/25x) + EV/Sales method (2x/3x/4x) · Conservative/Base/Bull table · Recommended value and why |
| 12 | Deal Structure | Total deal value · Cash ₹Xcr (≤108) · Equity swap ₹Xcr · Earn-out ₹Xcr with milestones · Dilution % · Founder lock-in terms |

**Valuation formula reminder:**
```
Annualized Profit = Quarterly Net Profit × 4
P/E Valuation     = Annualized Profit × Multiple (15x / 20x / 25x)

Annualized Revenue = Quarterly Sales × 4
EV/Sales Valuation = Annualized Revenue × Multiple (2x / 3x / 4x)

Acquisition Premium = (Deal Value − Market Cap) / Market Cap × 100
```

**Done when:** Numbers on Slide 12 add up exactly. Cash ≤ ₹108 Cr. Non-cash ≥ 40%.

---

### M16 — Deck: Slides 13–15 (PMI + Risks + Recommendation)
**⏱ ~2 hours | Needs: M14 | Unblocks: M17**

**Outputs:** Slides 13–15 complete

| Slide | Title | Key Content |
|-------|-------|-------------|
| 13 | PMI Plan | Month 1–2: Stabilize · Month 3–4: Systems · Month 5–6: Commercial integration · Synergy metrics table |
| 14 | Risks & Mitigation | 6-row table: Risk · Probability · Impact · Mitigation |
| 15 | Final Recommendation | Acquisition thesis (3 bullets) · **ACQUIRE ✅** · Conditions for approval |

**6 risks to cover on Slide 14:**
1. Integration exceeds 6-month window
2. Founders exit despite retention clause
3. Synergies don't materialise in 12 months
4. Key client concentration at target
5. Overpayment / valuation risk
6. Post-acquisition margin dilution

**Done when:** Slide 15 ends with a confident, single-line verdict.

---

### M17 — Deck: Final Polish
**⏱ ~1 hour | Needs: M12–M16 all done | Unblocks: M18**

**Checklist:**
- [ ] Consistent font throughout (pick one: Calibri, Inter, or Montserrat)
- [ ] Consistent colour scheme (suggest: dark navy + white + gold accent)
- [ ] Every number in deck matches model output exactly
- [ ] Deal structure adds up: Cash + Equity + Earn-out = Total Deal Value
- [ ] No slide exceeds 15 (max allowed)
- [ ] All 11 required components are covered (check against brief)
- [ ] Slide 3 shows all 5 acquisition constraints
- [ ] Slide 12 shows non-cash ≥ 40% of deal value

---

### M18 — README + Zip + Upload
**⏱ ~1 hour | Needs: Everything | Final milestone**

**README.md:**
```markdown
# RISKFERA AI — M&A Target Intelligence for InnovaTech Systems

## Setup
pip install -r requirements.txt

## Step 1: Clean the data
python data_loader.py

## Step 2: Run the model
python scoring/final_score.py

## Step 3: Launch dashboard
streamlit run dashboard/app.py

## Updating for new acquirer data
Edit config.py → re-run Step 2 → dashboard auto-updates
```

**Submission zip structure:**
```
riskfera-ai-submission/
├── requirements.txt
├── README.md
├── config.py
├── data_loader.py
├── data/
│   ├── dataset.xlsx          ← original, unmodified
│   ├── cleaned_targets.csv   ← generated by data_loader.py
│   └── column_map.txt
├── engines/
│   ├── risk_engine.py
│   ├── synergy_engine.py
│   └── feasibility_engine.py
├── scoring/
│   └── final_score.py
├── output/
│   ├── ranked_targets.csv
│   └── top5_targets.csv
├── dashboard/
│   └── app.py
└── deck/
    ├── RISKFERA_Deck.pptx
    └── RISKFERA_Deck.pdf
```

---

## 📊 MILESTONE STATUS BOARD

Copy this into Notion / WhatsApp / sticky note and tick off as you go:

```
MILESTONE                              STATUS      WHO
─────────────────────────────────────────────────────────
M1  Project Setup                      [ ] Todo    Both
M2  Data Loader & CSV                  [ ] Todo    ____
M3  Risk Engine                        [ ] Todo    ____
M4  Synergy Engine                     [ ] Todo    ____
M5  Feasibility Engine                 [ ] Todo    ____
M6  config.py                          [ ] Todo    ____
M7  Final Scoring Pipeline             [ ] Todo    ____
M8  Dashboard: Table + Sidebar         [ ] Todo    ____
M9  Dashboard: Deep Dive Panel         [ ] Todo    ____
M10 Dashboard: Radar Chart             [ ] Todo    ____
M11 Dashboard: Top5 + Export           [ ] Todo    ____
M12 Deck: Slides 1–4                   [ ] Todo    ____
M13 Deck: Slides 5–7                   [ ] Todo    ____
M14 Deck: Slides 8–10 (deep dive)      [ ] Todo    ____
M15 Deck: Slides 11–12 (valuation)     [ ] Todo    ____
M16 Deck: Slides 13–15 (PMI+risks)     [ ] Todo    ____
M17 Deck: Final Polish                 [ ] Todo    ____
M18 README + Zip + Submit              [ ] Todo    Both
─────────────────────────────────────────────────────────
RULE: Pick any unblocked milestone. Mark In Progress.
      Never leave a milestone In Progress for >3 hrs.
```

---

## ⚡ SUGGESTED PICKUP ORDER

**Day 1:** M1 (together) → M6, M2 (parallel, no dependencies)
**Day 2:** M3, M4, M5 (all three in parallel) + M12 (deck slides 1–4, no dependencies)
**Day 3:** M7 (needs M2+M3+M4+M5) → M8 + M13 (parallel once M7 done)
**Day 4:** M9, M10, M11 (all parallel, need M8) + M14, M15, M16 (parallel deck work)
**Day 5:** M17 + M18 (together)

---

*RISKFERA AI | Pick a milestone. Build it. Ship it.*
