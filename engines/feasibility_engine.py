# engines/feasibility_engine.py
# ============================================================
# RISKFERA AI - Feasibility Engine (M5)
# Answers: Can InnovaTech realistically acquire this company?
#
# Score: 0-100. HIGHER = MORE ACQUIRABLE.
# Used in final formula as: 0.25 x feasibility_score
#
# Signal weights:
#   S1  Market Cap vs Budget   : 40 pts
#   S2  P/E vs InnovaTech      : 25 pts
#   S3  Equity Dilution        : 20 pts
#   S4  Integration Complexity : 15 pts
#   Total                      : 100 pts
#
# USAGE:
#   from engines.feasibility_engine import (
#       compute_feasibility_score,
#       get_feasibility_label,
#       get_feasibility_reasons,
#       get_deal_structure
#   )
#   or run standalone:
#   python engines/feasibility_engine.py
# ============================================================

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ── Column Names (from column_map.txt) ───────────────────────
COL_NAME        = 'name'
COL_MCAP        = 'mar_cap_rscr'
COL_PE          = 'p_e'
COL_RET_3YR     = '3yrs_return'
COL_OPM         = 'opm'
COL_SECTOR      = 'sector'

# ── InnovaTech Acquisition Constraints ───────────────────────
INNOVATECH_MCAP         = 1911.0   # InnovaTech market cap (Rs. Cr)
INNOVATECH_PE           = 24.5     # InnovaTech current P/E
MAX_DEAL_VALUE          = 180.0    # Hard budget ceiling (Rs. Cr)
MAX_CASH_OUTFLOW        = 108.0    # 60% of 180 = max cash component
MIN_NONCASH_PCT         = 0.40     # Minimum 40% must be non-cash
ACQ_PREMIUM             = 0.25     # 25% acquisition premium assumed
MAX_DILUTION_PCT        = 5.0      # Target max equity dilution (%)

# ── Safe Number Reader ────────────────────────────────────────
def _n(row, col, default=0.0):
    """Safely read a number from a row. Returns default if missing or NaN."""
    val = row.get(col, default)
    try:
        f = float(val)
        return default if np.isnan(f) else f
    except:
        return default


# ============================================================
# SIGNAL FUNCTIONS
# Each returns (points, reason_string)
# points : int  - feasibility points (higher = more feasible)
# reason : str  - plain English explanation
# ============================================================

def _signal_budget(row):
    """
    Signal 1 - Market Cap vs Budget (max 40 pts)

    What it checks:
      Can InnovaTech actually afford this company?
      Deal value = MCap x 1.25 (25% acquisition premium).
      Hard ceiling is Rs.180 Cr from the hackathon brief.

      Comfortable  : deal <= Rs.126 Cr (70% of budget)
      Fits          : deal <= Rs.180 Cr (within budget)
      Stretch       : deal <= Rs.216 Cr (20% over budget, earn-out possible)
      Hard fail     : deal  > Rs.216 Cr (too expensive, no structuring fixes this)

    This is the most important signal (40 pts) because it is
    a hard constraint. No amount of synergy justifies a deal
    that breaches InnovaTech's financial capacity.
    """
    mcap = _n(row, COL_MCAP)
    deal = mcap * (1 + ACQ_PREMIUM)

    if mcap <= 0:
        return 0, "Market cap data unavailable - cannot assess budget fit."

    if deal <= 126:
        return 40, (f"Deal value Rs.{deal:.1f}Cr is well within the Rs.180Cr budget "
                    f"(MCap Rs.{mcap:.1f}Cr + 25% premium) - comfortable headroom.")
    elif deal <= 180:
        headroom = 180 - deal
        return 28, (f"Deal value Rs.{deal:.1f}Cr fits within Rs.180Cr budget "
                    f"with Rs.{headroom:.1f}Cr headroom - manageable with standard structuring.")
    elif deal <= 216:
        over = deal - 180
        return 12, (f"Deal value Rs.{deal:.1f}Cr exceeds budget by Rs.{over:.1f}Cr - "
                    f"stretch target, would require earn-out deferral or renegotiation.")
    else:
        return 0, (f"Deal value Rs.{deal:.1f}Cr significantly exceeds Rs.180Cr budget - "
                   f"not feasible within current acquisition constraints.")


def _signal_pe(row):
    """
    Signal 2 - P/E vs InnovaTech (max 25 pts)

    What it checks:
      Is this acquisition EPS accretive or dilutive?
      InnovaTech trades at 24.5x P/E.

      Buying below 24.5x = each rupee of target earnings
      costs less than InnovaTech's own earnings are valued.
      This is EPS accretive - good for shareholders.

      Buying above 24.5x = paying more per rupee of earnings
      than InnovaTech itself is valued. Dilutive unless
      synergies quickly close the gap.

      Missing P/E usually means loss-making company.
      Partial credit given to avoid unfairly penalizing
      high-growth companies not yet profitable.
    """
    pe = _n(row, COL_PE, default=-1)

    # Check raw value for truly missing data
    raw = row.get(COL_PE, None)
    if raw is None or (isinstance(raw, float) and np.isnan(raw)):
        return 8, "P/E unavailable - company may be loss-making, partial feasibility assumed."

    if pe <= 0:
        return 8, "Negative or zero P/E - company is loss-making, EPS accretion not assessable."
    elif pe < 10:
        return 25, (f"P/E of {pe:.1f}x is deeply below InnovaTech's {INNOVATECH_PE}x - "
                    f"highly accretive acquisition, strong value entry point.")
    elif pe < INNOVATECH_PE:
        return 20, (f"P/E of {pe:.1f}x is below InnovaTech's {INNOVATECH_PE}x - "
                    f"acquisition is EPS accretive, good valuation entry.")
    elif pe < 35:
        return 10, (f"P/E of {pe:.1f}x is slightly above InnovaTech's {INNOVATECH_PE}x - "
                    f"mildly dilutive, synergies needed to justify premium.")
    elif pe < 50:
        return 4,  (f"P/E of {pe:.1f}x significantly above InnovaTech's {INNOVATECH_PE}x - "
                    f"dilutive acquisition, requires strong synergy case.")
    else:
        return 0,  (f"P/E of {pe:.1f}x is very expensive relative to InnovaTech's {INNOVATECH_PE}x - "
                    f"highly dilutive, difficult to justify financially.")


def _signal_dilution(row):
    """
    Signal 3 - Equity Swap Dilution (max 20 pts)

    What it checks:
      How much would InnovaTech's existing shareholders be
      diluted by the equity component of the deal?

      Deal structure: 60% cash + 40% equity swap (minimum).
      Equity component = deal value x 40% (at minimum).
      Dilution % = equity component / InnovaTech MCap x 100.

      InnovaTech MCap = Rs.1911 Cr.
      Target: dilution below 5% to be acceptable.

      Low dilution = small deal = small equity swap needed.
      High dilution = large deal = more InnovaTech shares issued.
    """
    mcap = _n(row, COL_MCAP)
    if mcap <= 0:
        return 10, "Market cap unavailable - dilution cannot be calculated, partial score assumed."

    deal          = mcap * (1 + ACQ_PREMIUM)
    cash_comp     = min(deal * 0.60, MAX_CASH_OUTFLOW)
    equity_comp   = deal - cash_comp
    dilution_pct  = (equity_comp / INNOVATECH_MCAP) * 100

    if dilution_pct < 1.0:
        return 20, (f"Equity swap of Rs.{equity_comp:.1f}Cr causes only {dilution_pct:.2f}% dilution - "
                    f"negligible impact on InnovaTech shareholders.")
    elif dilution_pct < 2.5:
        return 16, (f"Equity swap of Rs.{equity_comp:.1f}Cr causes {dilution_pct:.2f}% dilution - "
                    f"low and acceptable dilution for InnovaTech shareholders.")
    elif dilution_pct < MAX_DILUTION_PCT:
        return 10, (f"Equity swap of Rs.{equity_comp:.1f}Cr causes {dilution_pct:.2f}% dilution - "
                    f"moderate but within the {MAX_DILUTION_PCT}% target threshold.")
    else:
        return 3,  (f"Equity swap of Rs.{equity_comp:.1f}Cr causes {dilution_pct:.2f}% dilution - "
                    f"above {MAX_DILUTION_PCT}% threshold, may face shareholder resistance.")


def _signal_integration(row):
    """
    Signal 4 - Integration Complexity (max 15 pts)

    What it checks:
      Can InnovaTech integrate this company within 6 months?
      High-velocity companies (stock up 60%+ in 3 years) are
      in rapid-change mode - scaling fast, chaotic processes,
      sensitive culture. Harder to integrate quickly.

      Stable or moderate-growth companies have established
      processes and are easier to absorb in 6 months.

      3yr stock return is used as a proxy for business velocity.
      Higher return = faster-moving company = harder integration.

      Also checks OPM - very low margin companies need more
      operational fixes post-acquisition, adding complexity.
    """
    ret3 = _n(row, COL_RET_3YR, default=15.0)  # default to median if missing
    opm  = _n(row, COL_OPM)

    # Base score from stock return (velocity proxy)
    if ret3 < 0:
        # Declining stock - company may be distressed, different kind of complexity
        base = 8
        ret_reason = f"3yr stock return of {ret3:.1f}% (declining) - possible distress, integration risk different in nature."
    elif ret3 < 30:
        base = 15
        ret_reason = f"3yr stock return of {ret3:.1f}% - stable company, integration manageable within 6 months."
    elif ret3 < 60:
        base = 10
        ret_reason = f"3yr stock return of {ret3:.1f}% - moderate growth velocity, integration feasible with care."
    elif ret3 < 100:
        base = 5
        ret_reason = f"3yr stock return of {ret3:.1f}% - high growth velocity, integration within 6 months will be challenging."
    else:
        base = 2
        ret_reason = f"3yr stock return of {ret3:.1f}% - very high velocity company, 6-month integration timeline is aggressive."

    # OPM penalty - thin margin companies need more operational fixes
    if opm < 0:
        opm_penalty = 3
        opm_note = " Company is loss-making - post-acquisition operational fixes add complexity."
    elif opm < 5:
        opm_penalty = 2
        opm_note = " Thin margins require operational improvement work post-acquisition."
    else:
        opm_penalty = 0
        opm_note = ""

    final = max(0, base - opm_penalty)
    reason = ret_reason + opm_note

    return final, reason


# ============================================================
# DEAL STRUCTURE CALCULATOR
# ============================================================

def get_deal_structure(row):
    """
    Calculates the indicative deal structure for a company.
    Enforces the 40% minimum non-cash constraint from the brief.

    Returns:
        dict with full deal breakdown
    """
    mcap = _n(row, COL_MCAP)

    if mcap <= 0:
        return {
            'deal_value_cr':    0,
            'cash_cr':          0,
            'equity_cr':        0,
            'earnout_cr':       0,
            'dilution_pct':     0,
            'cash_pct':         0,
            'noncash_pct':      0,
            'feasible':         False,
            'note':             'Market cap unavailable'
        }

    deal  = round(mcap * (1 + ACQ_PREMIUM), 2)
    feasible = deal <= MAX_DEAL_VALUE

    if feasible:
        # Standard structure: 60% cash, 40% equity swap
        cash   = round(min(deal * 0.60, MAX_CASH_OUTFLOW), 2)
        equity = round(deal - cash, 2)
        earnout = 0.0
        note = "Standard structure: 60% cash + 40% equity swap"
    elif deal <= 216:
        # Stretch: defer part as earn-out, keep cash within limit
        cash    = round(MAX_CASH_OUTFLOW, 2)
        earnout = round((deal - MAX_DEAL_VALUE) * 0.5, 2)
        equity  = round(deal - cash - earnout, 2)
        note = "Stretch structure: max cash + equity swap + earn-out deferral"
    else:
        # Not feasible - show what it would cost for reference
        cash   = round(MAX_CASH_OUTFLOW, 2)
        equity = round(MAX_DEAL_VALUE - cash, 2)
        earnout = round(deal - MAX_DEAL_VALUE, 2)
        note = "Not feasible within Rs.180Cr budget - shown for reference only"

    dilution_pct = round((equity / INNOVATECH_MCAP) * 100, 2)
    cash_pct     = round((cash / deal) * 100, 1) if deal > 0 else 0
    noncash_pct  = round(100 - cash_pct, 1)

    return {
        'deal_value_cr':    deal,
        'cash_cr':          cash,
        'equity_cr':        equity,
        'earnout_cr':       earnout,
        'dilution_pct':     dilution_pct,
        'cash_pct':         cash_pct,
        'noncash_pct':      noncash_pct,
        'feasible':         feasible,
        'note':             note
    }


# ============================================================
# MAIN SCORING FUNCTION
# ============================================================

def compute_feasibility_score(row):
    """
    Runs all 4 signals on a single company row.
    Returns feasibility score 0-100. Higher = more acquirable.

    Parameters:
        row : dict or pandas Series

    Returns:
        float - feasibility score 0 to 100
    """
    if not isinstance(row, dict):
        row = row.to_dict()

    s1, _ = _signal_budget(row)
    s2, _ = _signal_pe(row)
    s3, _ = _signal_dilution(row)
    s4, _ = _signal_integration(row)

    return round(float(min(100, s1 + s2 + s3 + s4)), 2)


def get_feasibility_breakdown(row):
    """
    Returns exact points per signal and total score.
    Used in dashboard deep dive panel.

    Returns:
        dict - signal names as keys, points as values
    """
    if not isinstance(row, dict):
        row = row.to_dict()

    s1, _ = _signal_budget(row)
    s2, _ = _signal_pe(row)
    s3, _ = _signal_dilution(row)
    s4, _ = _signal_integration(row)

    total = min(100, s1 + s2 + s3 + s4)

    return {
        'Budget Fit      (max 40)': s1,
        'P/E Valuation  (max 25)': s2,
        'Equity Dilution (max 20)': s3,
        'Integration     (max 15)': s4,
        'Total Feasibility Score':  total,
    }


def get_feasibility_label(score):
    """
    Converts numeric score to human readable label.

    Returns:
        str
    """
    if score >= 70:
        return "Highly Feasible"
    elif score >= 50:
        return "Feasible with Structuring"
    elif score >= 30:
        return "Stretch Target"
    else:
        return "Not Feasible"


def get_feasibility_reasons(row):
    """
    Returns plain English reasons for the feasibility score.
    One reason per signal, sorted by points descending.
    Written for a CFO, not a data scientist.

    Returns:
        list of str
    """
    if not isinstance(row, dict):
        row = row.to_dict()

    signals = [
        _signal_budget(row),
        _signal_pe(row),
        _signal_dilution(row),
        _signal_integration(row),
    ]

    # Sort by points descending - most impactful first
    sorted_signals = sorted(signals, key=lambda x: x[0], reverse=True)

    reasons = [reason for _, reason in sorted_signals if reason]

    if not reasons:
        reasons.append("Insufficient data to assess feasibility.")

    return reasons


# ============================================================
# SELF TEST
# ============================================================

if __name__ == '__main__':

    tests = [
        {
            'label':       'Easy Deal',
            'description': 'Small IT company well within budget - expect HIGH feasibility (70+)',
            COL_NAME:   'Globtier Infotec',
            COL_MCAP:    41.5,
            COL_PE:      18.0,
            COL_RET_3YR: 12.0,
            COL_OPM:     14.0,
            COL_SECTOR:  'it - services',
        },
        {
            'label':       'Tight Deal',
            'description': 'Near budget ceiling, P/E above InnovaTech - expect MODERATE (50-69)',
            COL_NAME:   'Elnet Technolog',
            COL_MCAP:   137.3,
            COL_PE:      27.0,
            COL_RET_3YR: 15.0,
            COL_OPM:     63.8,
            COL_SECTOR:  'it - services',
        },
        {
            'label':       'Stretch Target',
            'description': 'Slightly over budget, high P/E - expect STRETCH (30-49)',
            COL_NAME:   'MidSized Tech',
            COL_MCAP:   160.0,
            COL_PE:      45.0,
            COL_RET_3YR: 80.0,
            COL_OPM:      4.0,
            COL_SECTOR:  'fintech',
        },
        {
            'label':       'Not Feasible',
            'description': 'Way over budget - expect NOT FEASIBLE (0-29)',
            COL_NAME:   'LargeCorp',
            COL_MCAP:   5000.0,
            COL_PE:      35.0,
            COL_RET_3YR: 120.0,
            COL_OPM:     18.0,
            COL_SECTOR:  'it - software',
        },
    ]

    print()
    print("=" * 65)
    print("FEASIBILITY ENGINE - SELF TEST")
    print("=" * 65)

    all_passed = True

    for t in tests:
        label  = t.pop('label')
        desc   = t.pop('description')
        name   = t.get(COL_NAME, 'Unknown')

        score     = compute_feasibility_score(t)
        flabel    = get_feasibility_label(score)
        breakdown = get_feasibility_breakdown(t)
        reasons   = get_feasibility_reasons(t)
        deal      = get_deal_structure(t)

        if 'HIGH' in desc.upper() or '70+' in desc:
            passed = score >= 70
        elif 'MODERATE' in desc.upper() or '50-69' in desc:
            passed = 50 <= score <= 69
        elif 'STRETCH' in desc.upper() or '30-49' in desc:
            passed = 30 <= score <= 49
        else:
            passed = score < 30

        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False

        print(f"\n{'='*65}")
        print(f"Company    : {name}  ({label})")
        print(f"Test       : {desc}")
        print(f"Score      : {score}/100  -  {flabel}  [{status}]")
        print()
        print("Signal Breakdown:")
        for signal, pts in breakdown.items():
            if signal == 'Total Feasibility Score':
                continue
            bar  = '#' * int(pts)
            fill = '.' * (40 - len(bar))
            print(f"  {signal:<28}  {pts:>3} pts  |{bar}{fill}|")
        print(f"  {'Total':<28}  {breakdown['Total Feasibility Score']:>3} pts")
        print()
        print("Deal Structure:")
        print(f"  Deal Value      : Rs.{deal['deal_value_cr']:.1f} Cr")
        print(f"  Cash Component  : Rs.{deal['cash_cr']:.1f} Cr  ({deal['cash_pct']}%)")
        print(f"  Equity Swap     : Rs.{deal['equity_cr']:.1f} Cr")
        if deal['earnout_cr'] > 0:
            print(f"  Earn-Out        : Rs.{deal['earnout_cr']:.1f} Cr")
        print(f"  Non-Cash Total  : {deal['noncash_pct']}%  (minimum required: 40%)")
        print(f"  Dilution        : {deal['dilution_pct']}%  (target: below 5%)")
        print(f"  Feasible        : {'Yes' if deal['feasible'] else 'No'}")
        print(f"  Note            : {deal['note']}")
        print()
        print("Reasons:")
        for r in reasons:
            print(f"  - {r}")

    print()
    print("=" * 65)
    print(f"SELF TEST {'PASSED' if all_passed else 'FAILED'}")
    print("=" * 65)

    # Run on real data
    import os
    if os.path.isfile('data/cleaned_targets.csv'):
        print()
        print("=" * 65)
        print("FEASIBILITY ENGINE - REAL DATASET")
        print("=" * 65)

        df = pd.read_csv('data/cleaned_targets.csv')
        df['feasibility_score'] = df.apply(compute_feasibility_score, axis=1)
        df['feasibility_label'] = df['feasibility_score'].apply(get_feasibility_label)

        total = len(df)
        print(f"\nScored {total} companies")
        print()
        print("Feasibility Distribution:")
        print(f"  Highly Feasible          (70+)  : {(df['feasibility_score']>=70).sum()}")
        print(f"  Feasible with Structuring(50-69): {((df['feasibility_score']>=50)&(df['feasibility_score']<70)).sum()}")
        print(f"  Stretch Target           (30-49): {((df['feasibility_score']>=30)&(df['feasibility_score']<50)).sum()}")
        print(f"  Not Feasible             (0-29) : {(df['feasibility_score']<30).sum()}")
        print()

        print("Top 10 Most Feasible IT Companies:")
        feasible_it = df[df['sector'].str.contains('IT', na=False)]
        top10 = feasible_it.nlargest(10, 'feasibility_score')
        print(f"  {'Name':<32} {'Score':>6} {'Label':<28} {'MCap':>8} {'P/E':>6}")
        print(f"  {'-'*32} {'-----':>6} {'-'*28} {'----':>8} {'---':>6}")
        for _, r in top10.iterrows():
            print(f"  {str(r['name']):<32} {r['feasibility_score']:>6.1f} {r['feasibility_label']:<28} {r['mar_cap_rscr']:>8.1f} {r['p_e']:>6.1f}")

        print()
        print("Bottom 5 Least Feasible (for reference):")
        bot5 = df.nsmallest(5, 'feasibility_score')
        for _, r in bot5.iterrows():
            deal = r['mar_cap_rscr'] * 1.25
            print(f"  {str(r['name']):<32} score={r['feasibility_score']:>5.1f}  deal=Rs.{deal:>10.1f}Cr")
    else:
        print("\nNo cleaned_targets.csv found. Run data_loader.py first.")
    print()
