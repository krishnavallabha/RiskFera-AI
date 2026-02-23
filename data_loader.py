# data_loader.py
# ============================================================
# RISKFERA AI - Data Loader & Cleaner
# Milestone: M2
#
# USAGE:
#   python data_loader.py
#
# OUTPUTS:
#   data/cleaned_targets.csv
#   data/column_map.txt
# ============================================================

import pandas as pd
import numpy as np
import os
import sys


# ============================================================
# CONFIRMED CLEANED COLUMN NAMES (from your actual dataset)
# ============================================================
#   sno
#   name
#   p_e
#   mar_cap_rscr          <- market cap
#   div_yld
#   np_qtr_rscr           <- quarterly net profit
#   qtr_profit_var
#   sales_qtr_rscr        <- quarterly sales
#   qtr_sales_var
#   roce
#   opm
#   sales_var_3yrs
#   profit_var_3yrs
#   3yrs_return
#   roe_3yr
#   ebidt_var_3yrs
#   eps_var_3yrs
#   sector
# ============================================================


def load_raw(path='data/dataset.csv'):
    if not os.path.isfile(path):
        print(f"ERROR: File not found: {path}")
        print("Place dataset.csv inside the data/ folder and re-run.")
        sys.exit(1)
    try:
        df = pd.read_csv(path, encoding='latin-1')
        print(f"Loaded: {path} ({len(df)} rows x {len(df.columns)} columns)")
        return df
    except Exception as e:
        print(f"ERROR: Could not read file: {e}")
        sys.exit(1)


def clean_column_names(df):
    original = df.columns.tolist()

    df.columns = (
        df.columns
        .str.replace('\xa0', ' ', regex=False)
        .str.strip()
        .str.lower()
        .str.replace(r'[₹%().,]',   '',  regex=True)
        .str.replace(r'[/\\]',       '_', regex=True)
        .str.replace(r'[^a-z0-9]+',  '_', regex=True)
        .str.strip('_')
    )

    cleaned = df.columns.tolist()

    os.makedirs('data', exist_ok=True)
    with open('data/column_map.txt', 'w', encoding='utf-8') as f:
        f.write("ORIGINAL COLUMN NAME                          ->  CLEANED NAME\n")
        f.write("=" * 75 + "\n")
        for orig, clean in zip(original, cleaned):
            f.write(f"{orig:<45}  ->  {clean}\n")

    print(f"Column map saved -> data/column_map.txt")
    print(f"{len(cleaned)} columns standardized")
    return df


def enforce_numeric(df):
    text_cols = ['name', 'sector']
    for col in df.columns:
        if col not in text_cols:
            if df[col].dtype == object:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(',', '', regex=False)
                    .str.strip()
                )
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def add_derived_columns(df):
    # Quarterly sales -> annualized revenue
    if 'sales_qtr_rscr' in df.columns:
        df['annual_revenue_est'] = df['sales_qtr_rscr'] * 4
        print("annual_revenue_est = sales_qtr_rscr x 4")
    else:
        print("WARNING: sales_qtr_rscr not found - check column_map.txt")

    # Quarterly profit -> annualized profit
    if 'np_qtr_rscr' in df.columns:
        df['annual_profit_est'] = df['np_qtr_rscr'] * 4
        print("annual_profit_est  = np_qtr_rscr x 4")
    else:
        print("WARNING: np_qtr_rscr not found - check column_map.txt")

    # Profit margin
    if 'annual_profit_est' in df.columns and 'annual_revenue_est' in df.columns:
        df['profit_margin_est'] = (
            df['annual_profit_est'] / df['annual_revenue_est'] * 100
        ).round(2)
        print("profit_margin_est  = annual_profit / annual_revenue x 100")

    return df


def flag_data_quality(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df['data_limited'] = df[numeric_cols].isnull().sum(axis=1) > 3
    count = df['data_limited'].sum()
    print(f"Data-limited companies (more than 3 missing fields): {count}")
    return df


def fill_missing(df):
    before = df.isnull().sum().sum()
    df = df.fillna(df.median(numeric_only=True))
    after = df.isnull().sum().sum()
    print(f"NaN values filled: {before} -> {after}")
    return df


def print_summary(df):
    print()
    print("=" * 55)
    print("DATASET SUMMARY")
    print("=" * 55)

    print(f"\nTotal companies : {len(df)}")
    print(f"Total columns   : {len(df.columns)}")

    print("\nSectors:")
    for sector, count in df['sector'].value_counts().items():
        print(f"  {count:>4}  {sector}")

    mc = df['mar_cap_rscr']
    print(f"\nMarket Cap range   : Rs.{mc.min():.2f}Cr - Rs.{mc.max():,.0f}Cr")
    print(f"Median Market Cap  : Rs.{mc.median():.0f}Cr")

    feasible = df[df['mar_cap_rscr'] * 1.25 <= 180]
    print(f"\nFeasible targets (deal <= Rs.180Cr at 25% premium): {len(feasible)}")
    print("Top 8 smallest by market cap:")
    for _, row in feasible.nsmallest(8, 'mar_cap_rscr').iterrows():
        print(f"  {str(row['name']):<32}  Rs.{row['mar_cap_rscr']:.1f}Cr  |  {row['sector']}")

    roce = df['roce'].dropna()
    print(f"\nROCE range       : {roce.min():.1f}% - {roce.max():.1f}%")
    print(f"Median ROCE      : {roce.median():.1f}%")
    print(f"ROCE >= 22.1%    : {(roce >= 22.1).sum()} companies (InnovaTech benchmark)")

    opm = df['opm'].dropna()
    print(f"\nOPM range        : {opm.min():.1f}% - {opm.max():.1f}%")
    print(f"Median OPM       : {opm.median():.1f}%")
    print(f"OPM >= 12.8%     : {(opm >= 12.8).sum()} companies (InnovaTech benchmark)")

    pe = df['p_e'].dropna()
    print(f"\nP/E range        : {pe.min():.1f}x - {pe.max():.1f}x")
    print(f"Median P/E       : {pe.median():.1f}x")
    print(f"P/E < 24.5x      : {(pe < 24.5).sum()} companies (accretive for InnovaTech)")

    print(f"\nData-limited     : {df['data_limited'].sum()} companies flagged")
    print("=" * 55)


def load_and_clean(path='data/dataset.csv'):
    print()
    print("=" * 55)
    print("RISKFERA AI - Data Loader (M2)")
    print("=" * 55)
    print()

    df = load_raw(path)
    df = clean_column_names(df)
    df = enforce_numeric(df)

    print("\nAdding derived columns...")
    df = add_derived_columns(df)

    print("\nFlagging data quality...")
    df = flag_data_quality(df)

    print("\nFilling missing values (median)...")
    df = fill_missing(df)

    print_summary(df)

    out = 'data/cleaned_targets.csv'
    df.to_csv(out, index=False)
    print(f"\nSaved: {out} ({len(df)} rows x {len(df.columns)} columns)")

    print()
    print("=" * 55)
    print("COLUMN NAMES TO USE IN YOUR ENGINE FILES")
    print("=" * 55)
    print()
    print("RISK ENGINE - COL_* constants:")
    print("  COL_QTR_PROFIT_VAR  = 'qtr_profit_var'")
    print("  COL_PROFIT_VAR_3YR  = 'profit_var_3yrs'")
    print("  COL_EBIDT_VAR_3YR   = 'ebidt_var_3yrs'")
    print("  COL_OPM             = 'opm'")
    print("  COL_DIV_YIELD       = 'div_yld'")
    print("  COL_EPS_VAR_3YR     = 'eps_var_3yrs'")
    print()
    print("SYNERGY ENGINE - COL_* constants:")
    print("  COL_ROCE            = 'roce'")
    print("  COL_OPM             = 'opm'")
    print("  COL_SALES_3YR       = 'sales_var_3yrs'")
    print("  COL_EPS_3YR         = 'eps_var_3yrs'")
    print("  COL_SECTOR          = 'sector'")
    print()
    print("FEASIBILITY ENGINE - COL_* constants:")
    print("  COL_MCAP            = 'mar_cap_rscr'")
    print("  COL_PE              = 'p_e'")
    print("  COL_RET_3YR         = '3yrs_return'")
    print()
    print("Next step: python verify_m2.py")
    print()

    return df


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'data/dataset.csv'
    load_and_clean(path=path)
