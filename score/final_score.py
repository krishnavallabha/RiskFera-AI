# scoring/final_score.py
# ============================================================
# RISKFERA AI — M7: Final Scoring & Ranking Pipeline
#
# What this file does:
#   1. Loads cleaned_targets.csv (from M2)
#   2. Runs all 3 engines on every company
#   3. Combines scores using InnovaTech's weights
#   4. Sorts best to worst
#   5. Saves ranked_targets.csv and top5_targets.csv
#
# Run:
#   python scoring/final_score.py
#
# Needs:
#   data/cleaned_targets.csv     ← run data_loader.py first
#   engines/risk_engine.py       ← M3
#   engines/synergy_energy.py    ← M4  (note: your file is named synergy_energy.py)
#   engines/feasibility_engine.py← M5
#   config.py                    ← M6
# ============================================================

import pandas as pd
import os
import sys

# ── Path setup — allows importing from parent folder ─────────────────────────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ── Import config ─────────────────────────────────────────────────────────────
from config import INNOVATECH

# ── Import from YOUR actual engine files ─────────────────────────────────────
# Risk Engine (M3)
from engines.risk_engine import (
    compute_risk_score,
    get_risk_label,
    get_risk_reasons,
    get_risk_breakdown,
    get_risk_summary
)

# Synergy Engine (M4) — your file is named synergy_energy.py
from engines.synergy_energy import (
    compute_synergy_score,
    get_synergy_label,
    get_synergy_reasons
)

# Feasibility Engine (M5)
from engines.feasibility_engine import (
    compute_feasibility_score,
    get_feasibility_label,
    get_feasibility_reasons,
    get_feasibility_breakdown,
    get_deal_structure
)


# ============================================================
# FINAL SCORE FORMULA
# ============================================================
#
#   Final Score = 40% × (100 - Risk)    ← Risk is INVERTED
#               + 35% × Synergy
#               + 25% × Feasibility
#
#   Why Risk is inverted:
#     Risk score 80 = very risky = BAD for ranking
#     So (100 - 80) = 20 before applying weight
#     A LOW risk company gets a HIGH contribution here
#
# Weights come from config.py INNOVATECH['final_weights']
# ============================================================

def compute_final_score(risk, synergy, feasibility, weights):
    """
    Combines 3 engine scores into one attractiveness score.

    Parameters:
        risk        : float — risk score 0-100 (higher = riskier)
        synergy     : float — synergy score 0-100 (higher = better fit)
        feasibility : float — feasibility score 0-100 (higher = more doable)
        weights     : dict  — from INNOVATECH['final_weights']

    Returns:
        float — final attractiveness score 0-100
    """
    score = (
        weights['risk']        * (100 - risk)   +   # inverted: low risk = good
        weights['synergy']     * synergy         +
        weights['feasibility'] * feasibility
    )
    return round(float(score), 2)


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_model(
    input_path  = 'data/cleaned_targets.csv',
    output_path = 'output/ranked_targets.csv'
):
    """
    Runs the full RISKFERA scoring model on the cleaned dataset.

    Steps:
        1. Load CSV
        2. Score every company with all 3 engines
        3. Compute final attractiveness score
        4. Sort by score descending
        5. Add labels
        6. Save outputs

    Returns:
        pandas DataFrame — full ranked results
    """

    # ── Step 1: Load data ─────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("RISKFERA AI — Final Scoring Pipeline")
    print("=" * 60)

    if not os.path.isfile(input_path):
        print(f"\n❌ ERROR: {input_path} not found.")
        print("   Run data_loader.py first to generate cleaned_targets.csv")
        return None

    df = pd.read_csv(input_path)
    print(f"\n✅ Loaded {len(df)} companies from {input_path}")

    # ── Detect name column ────────────────────────────────────────────────────
    # Handles whatever column name data_loader.py produced
    name_col = next(
        (c for c in df.columns if 'name' in c.lower() or 'company' in c.lower()),
        df.columns[0]
    )
    print(f"   Name column detected: '{name_col}'")
    print(f"   Sectors found: {df['sector'].nunique() if 'sector' in df.columns else 'N/A'}")

    # ── Step 2: Run all 3 engines ─────────────────────────────────────────────
    print("\nScoring companies...")
    print("   Running Risk Engine      ...", end=" ")
    df['risk_score']        = df.apply(compute_risk_score,        axis=1)
    print(f"done  (range: {df['risk_score'].min():.0f}–{df['risk_score'].max():.0f})")

    print("   Running Synergy Engine   ...", end=" ")
    df['synergy_score']     = df.apply(compute_synergy_score,     axis=1)
    print(f"done  (range: {df['synergy_score'].min():.1f}–{df['synergy_score'].max():.1f})")

    print("   Running Feasibility Engine ...", end=" ")
    df['feasibility_score'] = df.apply(compute_feasibility_score, axis=1)
    print(f"done  (range: {df['feasibility_score'].min():.1f}–{df['feasibility_score'].max():.1f})")

    # ── Step 3: Compute final attractiveness score ────────────────────────────
    w = INNOVATECH['final_weights']

    df['attractiveness_score'] = df.apply(
        lambda row: compute_final_score(
            row['risk_score'],
            row['synergy_score'],
            row['feasibility_score'],
            w
        ),
        axis=1
    )

    print(f"\n   Final score range: {df['attractiveness_score'].min():.1f}–{df['attractiveness_score'].max():.1f}")

    # ── Step 4: Sort best to worst ────────────────────────────────────────────
    df = df.sort_values('attractiveness_score', ascending=False).reset_index(drop=True)
    df['rank'] = df.index + 1

    # ── Step 5: Add human-readable labels ────────────────────────────────────
    df['risk_label']        = df['risk_score'].apply(get_risk_label)
    df['synergy_label']     = df['synergy_score'].apply(get_synergy_label)
    df['feasibility_label'] = df['feasibility_score'].apply(get_feasibility_label)

    # ── Step 6: Save outputs ──────────────────────────────────────────────────
    os.makedirs('output', exist_ok=True)

    df.to_csv(output_path, index=False)
    df.head(5).to_csv('output/top5_targets.csv', index=False)

    print(f"\n✅ Saved: {output_path}  ({len(df)} rows)")
    print(f"✅ Saved: output/top5_targets.csv  (top 5 only)")

    # ── Print Top 5 table ─────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("🏆 TOP 5 ACQUISITION CANDIDATES")
    print("=" * 60)

    top5 = df.head(5)

    for _, row in top5.iterrows():
        print(f"\n#{int(row['rank'])}  {row[name_col]}")
        print(f"    Sector       : {row.get('sector', 'N/A')}")
        print(f"    Risk         : {row['risk_score']:.0f}/100  {row['risk_label']}")
        print(f"    Synergy      : {row['synergy_score']:.1f}/100  {row['synergy_label']}")
        print(f"    Feasibility  : {row['feasibility_score']:.1f}/100  {row['feasibility_label']}")
        print(f"    FINAL SCORE  : {row['attractiveness_score']:.2f}/100")

        # Deal structure for each top 5 company
        deal = get_deal_structure(row.to_dict())
        print(f"    Deal Value   : ₹{deal['deal_value_cr']}Cr  "
              f"({'✅ within budget' if deal['feasible'] else '⚠️ over budget'})")
        print(f"    Structure    : Cash ₹{deal['cash_cr']}Cr ({deal['cash_pct']}%)  "
              f"+ Equity ₹{deal['equity_cr']}Cr  "
              f"+ Earn-out ₹{deal['earnout_cr']}Cr")
        print(f"    Dilution     : {deal['dilution_pct']}%")

    # ── Score distribution summary ────────────────────────────────────────────
    print()
    print("=" * 60)
    print("📊 FULL UNIVERSE DISTRIBUTION")
    print("=" * 60)

    print(f"\nRisk Distribution:")
    print(f"   Low Risk      (0–20)  : {(df['risk_score'] <= 20).sum()} companies")
    print(f"   Moderate Risk (21–40) : {((df['risk_score'] > 20) & (df['risk_score'] <= 40)).sum()} companies")
    print(f"   Elevated Risk (41–60) : {((df['risk_score'] > 40) & (df['risk_score'] <= 60)).sum()} companies")
    print(f"   High Risk     (61+)   : {(df['risk_score'] > 60).sum()} companies")

    print(f"\nSynergy Distribution:")
    print(f"   High Synergy     (75+)  : {(df['synergy_score'] >= 75).sum()} companies")
    print(f"   Moderate Synergy (55–74): {((df['synergy_score'] >= 55) & (df['synergy_score'] < 75)).sum()} companies")
    print(f"   Low Synergy      (35–54): {((df['synergy_score'] >= 35) & (df['synergy_score'] < 55)).sum()} companies")
    print(f"   Misaligned       (<35)  : {(df['synergy_score'] < 35).sum()} companies")

    print(f"\nFeasibility Distribution:")
    print(f"   Highly Feasible          (70+)  : {(df['feasibility_score'] >= 70).sum()} companies")
    print(f"   Feasible with Structuring(50–69): {((df['feasibility_score'] >= 50) & (df['feasibility_score'] < 70)).sum()} companies")
    print(f"   Stretch Target           (30–49): {((df['feasibility_score'] >= 30) & (df['feasibility_score'] < 50)).sum()} companies")
    print(f"   Not Feasible             (<30)  : {(df['feasibility_score'] < 30).sum()} companies")

    print(f"\nFinal Score Distribution:")
    print(f"   Strong candidates (65+) : {(df['attractiveness_score'] >= 65).sum()} companies")
    print(f"   Good candidates  (50–64): {((df['attractiveness_score'] >= 50) & (df['attractiveness_score'] < 65)).sum()} companies")
    print(f"   Weak candidates  (35–49): {((df['attractiveness_score'] >= 35) & (df['attractiveness_score'] < 50)).sum()} companies")
    print(f"   Not recommended  (<35)  : {(df['attractiveness_score'] < 35).sum()} companies")

    print()
    print("=" * 60)
    print("✅ RISKFERA scoring complete")
    print("=" * 60)
    print()

    return df


# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    df = run_model()
