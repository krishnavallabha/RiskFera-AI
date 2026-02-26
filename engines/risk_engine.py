import pandas as pd
import numpy as np
import os
import sys 

# Answers: Can we trust this company's financial performance?
#
# Score: 0-100. HIGHER = RISKIER.
# Used in final formula as: 0.40 x (100 - risk_score)
#
# Signal weights (based on real dataset analysis):
#   S1  Quarterly Profit Variance   : max 20 pts
#   S2  3 Year Profit Variance      : max 30 pts
#   S3  3 Year EBITDA Variance      : max 25 pts
#   S4  Operating Profit Margin     : max 15 pts
#   S5  Dividend Yield              : max  5 pts
#   S6  EPS 3 Year Variance         : max  5 pts
#   Total                           : max 100 pts
#
# USAGE:
#   from engines.risk_engine import (
#       compute_risk_score,
#       get_risk_label,
#       get_risk_reasons,
#       get_risk_breakdown,
#       score_full_dataset
#   )
#   or run standalone:
#   python engines/risk_engine.py

# These match cleaned_targets.csv exactly.
# If you get a KeyError, check data/column_map.txt
COL_NAME            = 'name'
COL_SECTOR          = 'sector'
COL_MCAP            = 'mar_cap_rscr'
COL_OPM             = 'opm'
COL_ROCE            = 'roce'
COL_QTR_PROFIT_VAR  = 'qtr_profit_var'
COL_PROFIT_VAR_3YR  = 'profit_var_3yrs'
COL_EBIDT_VAR_3YR   = 'ebidt_var_3yrs'
COL_EPS_VAR_3YR     = 'eps_var_3yrs'
COL_DIV_YIELD       = 'div_yld'
COL_SALES_VAR_3YR   = 'sales_var_3yrs'
COL_PE              = 'p_e'

# SIGNAL FUNCTIONS
# Each returns (points, reason_string)
#   points : int   - risk points added (0 to max for signal)
#   reason : str   - plain English explanation
#                    empty string if signal did not fire
def _signal_qtr_profit_var(row):
    """
    Signal 1 - Quarterly Profit Variance (max 20 pts)

    What it catches:
      Short term earnings instability. A company whose profit
      swings wildly quarter on quarter is hard to value and
      risky to integrate. Either the business is genuinely
      volatile or earnings are being managed.

    Capped at 20 (not 30) based on dataset analysis where
    this signal was firing on 86% of companies and dominating
    scores. Structural signals (S2, S3) are more meaningful
    for acquisition decisions.
    """
    val = row.get(COL_QTR_PROFIT_VAR, np.nan)

    if pd.isna(val):
        return 5, "Quarterly profit variance data unavailable - partial risk assumed."

    av = abs(val)

    if av > 200:
        return 20, (f"Quarterly profit swung {val:.1f}% - extreme earnings instability, "
                    f"suggests one-off items or severe business disruption.")
    elif av > 100:
        return 16, (f"Quarterly profit swung {val:.1f}% - very high earnings volatility, "
                    f"profit is not predictable quarter on quarter.")
    elif av > 50:
        return 12, (f"Quarterly profit swung {val:.1f}% - significant volatility, "
                    f"earnings consistency is a concern.")
    elif av > 25:
        return 7,  (f"Quarterly profit variance of {val:.1f}% - elevated short term fluctuation, "
                    f"worth monitoring post acquisition.")
    elif av > 10:
        return 3,  (f"Quarterly profit variance of {val:.1f}% - mild fluctuation, "
                    f"broadly within acceptable range.")
    else:
        return 0,  ""


def _signal_profit_var_3yr(row):
    """
    Signal 2 - 3 Year Profit Variance (max 30 pts)

    What it catches:
      Long term structural profit direction. A company can
      have stable quarterly earnings while its annual profits
      slowly deteriorate. This signal catches that drift.
      Structural decline is the most serious risk for an
      acquirer because it cannot be fixed by integration alone.
    """
    val = row.get(COL_PROFIT_VAR_3YR, np.nan)

    if pd.isna(val):
        return 5, "3 year profit trend data unavailable - partial risk assumed."

    if val < -40:
        return 30, (f"Profits collapsed {abs(val):.1f}% over 3 years - severe structural deterioration, "
                    f"business model may be fundamentally broken.")
    elif val < -20:
        return 24, (f"Profits declined {abs(val):.1f}% over 3 years - serious structural deterioration, "
                    f"requires deep due diligence on root cause.")
    elif val < -10:
        return 16, (f"Profits declined {abs(val):.1f}% over 3 years - moderate long term concern, "
                    f"competitive pressures or margin erosion likely.")
    elif val < 0:
        return 8,  (f"Profits declined {abs(val):.1f}% over 3 years - mild downward trend, "
                    f"monitor for continuation.")
    elif val < 10:
        return 2,  (f"Profits grew {val:.1f}% over 3 years - marginal growth, "
                    f"broadly flat performance.")
    else:
        return 0,  ""


def _signal_ebidt_var_3yr(row):
    """
    Signal 3 - EBITDA Variance over 3 Years (max 25 pts)

    What it catches:
      Core operational health stripped of accounting choices.
      Unlike net profit, EBITDA removes tax structure, interest,
      and depreciation decisions. If EBITDA is declining while
      net profit grows, the company may be window dressing
      financials through accounting levers.

      This signal catches situations where:
        - Depreciation is being reduced (accounting choice, not real improvement)
        - One-off tax benefits inflate reported profit
        - Debt-funded acquisitions boost profit but weaken operations
    """
    val = row.get(COL_EBIDT_VAR_3YR, np.nan)

    if pd.isna(val):
        return 4, "3 year EBITDA trend data unavailable - partial risk assumed."

    if val < -30:
        return 25, (f"EBITDA collapsed {abs(val):.1f}% over 3 years - "
                    f"core operations severely weakening, not just accounting effects.")
    elif val < -15:
        return 20, (f"EBITDA declined {abs(val):.1f}% over 3 years - "
                    f"core operations weakening seriously, underlying business deteriorating.")
    elif val < -5:
        return 13, (f"EBITDA declined {abs(val):.1f}% over 3 years - "
                    f"moderate operational erosion, cash generation under pressure.")
    elif val < 0:
        return 5,  (f"EBITDA declined {abs(val):.1f}% over 3 years - "
                    f"slight operational softening, watch for continuation.")
    else:
        return 0,  ""


def _signal_opm(row):
    """
    Signal 4 - Operating Profit Margin (max 15 pts)

    What it catches:
      Margin fragility and buffer against adversity.
      Low OPM means the company is operating close to breakeven.
      A single bad quarter, a cost increase, or a client loss
      can push thin-margin businesses into operating losses.
      For an acquirer, this means buying a fragile business
      with almost no room for integration disruption.

    Negative OPM = operating at a loss = automatic maximum points.
    67 companies in your dataset have negative OPM (17%).
    """
    val = row.get(COL_OPM, np.nan)

    if pd.isna(val):
        return 3, "Operating margin data unavailable - partial risk assumed."

    if val < -50:
        return 15, (f"Operating margin is {val:.1f}% - company is severely loss-making at operating level, "
                    f"fundamental viability concern.")
    elif val < 0:
        return 15, (f"Operating margin is {val:.1f}% - company is operating at a loss, "
                    f"revenue does not cover operating costs.")
    elif val < 3:
        return 10, (f"Operating margin is {val:.1f}% - razor thin margin, "
                    f"extremely fragile to any revenue decline or cost increase.")
    elif val < 7:
        return 5,  (f"Operating margin is {val:.1f}% - below average margin, "
                    f"limited buffer against business adversity.")
    elif val < 10:
        return 2,  (f"Operating margin is {val:.1f}% - acceptable but below InnovaTech benchmark of 12.8%.")
    else:
        return 0,  ""


def _signal_div_yield(row):
    """
    Signal 5 - Dividend Yield (max 5 pts)

    What it catches:
      Potential value trap. Unusually high dividend yield
      almost always means the stock price has fallen sharply,
      not that the company became more generous.
      Yield = Dividend / Stock Price.
      When stock price crashes, yield spikes.
      That crash happened for a reason.

    Threshold set at 5% (not 8%) because no company in
    this dataset exceeds 8% yield - would fire on zero
    companies at the higher threshold.
    """
    val = row.get(COL_DIV_YIELD, np.nan)

    if pd.isna(val):
        return 0, ""

    if val > 7:
        return 5, (f"Dividend yield of {val:.1f}% is very high - "
                   f"almost certainly indicates stock price crash, possible value trap.")
    elif val > 5:
        return 4, (f"Dividend yield of {val:.1f}% is elevated - "
                   f"stock may have underperformed significantly, investigate root cause.")
    elif val > 3:
        return 2, (f"Dividend yield of {val:.1f}% is above average - "
                   f"minor flag, monitor alongside other signals.")
    else:
        return 0, ""


def _signal_eps_var_3yr(row):
    """
    Signal 6 - EPS Variance over 3 Years (max 5 pts)

    What it catches:
      Per share value destruction even when total profit grows.
      EPS accounts for share dilution. A company can grow total
      net profit while issuing so many new shares that each
      individual share is worth less. Declining EPS over 3 years
      means the company is either losing money OR diluting
      shareholders through excessive equity issuance.

      For InnovaTech this matters because the deal structure
      includes an equity swap. A target with history of
      EPS dilution suggests loose capital management.
    """
    val = row.get(COL_EPS_VAR_3YR, np.nan)

    if pd.isna(val):
        return 1, "3 year EPS trend unavailable - partial risk assumed."

    if val < -40:
        return 5, (f"EPS collapsed {abs(val):.1f}% over 3 years - "
                   f"severe per share value destruction, significant shareholder dilution.")
    elif val < -20:
        return 5, (f"EPS declined {abs(val):.1f}% over 3 years - "
                   f"per share value being destroyed despite any profit growth.")
    elif val < -10:
        return 3, (f"EPS declined {abs(val):.1f}% over 3 years - "
                   f"moderate per share dilution, worth investigating equity issuance history.")
    elif val < 0:
        return 2, (f"EPS declined {abs(val):.1f}% over 3 years - "
                   f"mild per share dilution.")
    else:
        return 0, ""
    

# COMPOSITE RISK FLAGS
# These are additional checks that look at combinations
# of signals to catch situations individual signals miss.
# They do not add to the 0-100 score but appear in reasons.

def _composite_flags(row):
    """
    Checks for dangerous signal combinations that are worse
    than any individual signal alone.

    Returns:
        list of str - warning messages (empty if none)
    """
    flags = []

    profit3  = row.get(COL_PROFIT_VAR_3YR, np.nan)
    ebidt3   = row.get(COL_EBIDT_VAR_3YR,  np.nan)
    opm      = row.get(COL_OPM,            np.nan)
    qtr      = row.get(COL_QTR_PROFIT_VAR, np.nan)
    eps3     = row.get(COL_EPS_VAR_3YR,    np.nan)
    sales3   = row.get(COL_SALES_VAR_3YR,  np.nan)

    # Flag 1: Profit declining but EBITDA also declining
    # means the decline is operational, not just accounting
    if (not pd.isna(profit3) and not pd.isna(ebidt3)
            and profit3 < -10 and ebidt3 < -10):
        flags.append(
            "COMPOSITE FLAG: Both profit AND EBITDA declining over 3 years - "
            "deterioration is operational, not an accounting artefact."
        )

    # Flag 2: Negative OPM + declining profits
    # company is loss-making AND getting worse
    if (not pd.isna(opm) and not pd.isna(profit3)
            and opm < 0 and profit3 < 0):
        flags.append(
            "COMPOSITE FLAG: Operating at a loss with declining profit trend - "
            "company is burning cash with no near-term recovery signal."
        )

    # Flag 3: Extreme quarterly variance + long term decline
    # short term chaos on top of structural deterioration
    if (not pd.isna(qtr) and not pd.isna(profit3)
            and abs(qtr) > 100 and profit3 < -20):
        flags.append(
            "COMPOSITE FLAG: Extreme quarterly volatility combined with long term profit decline - "
            "earnings are both unstable and structurally deteriorating."
        )

    # Flag 4: Revenue growing but profits declining
    # suggests serious margin compression or cost bloat
    if (not pd.isna(sales3) and not pd.isna(profit3)
            and sales3 > 10 and profit3 < -10):
        flags.append(
            "COMPOSITE FLAG: Revenue growing but profits falling - "
            "serious margin compression or cost structure deteriorating faster than growth."
        )

    # Flag 5: EPS declining despite positive profit trend
    # suggests heavy share dilution
    if (not pd.isna(eps3) and not pd.isna(profit3)
            and profit3 > 10 and eps3 < -10):
        flags.append(
            "COMPOSITE FLAG: Profit growing but EPS declining - "
            "company may be issuing excessive equity, diluting shareholders."
        )

    return flags
def compute_risk_score(row):
    """
    Runs all 6 signals on a single company row.
    Returns risk score 0-100. Higher = riskier.

    Parameters:
        row : dict or pandas Series

    Returns:
        int - risk score 0 to 100
    """
    if not isinstance(row, dict):
        row = row.to_dict()

    s1, _ = _signal_qtr_profit_var(row)
    s2, _ = _signal_profit_var_3yr(row)
    s3, _ = _signal_ebidt_var_3yr(row)
    s4, _ = _signal_opm(row)
    s5, _ = _signal_div_yield(row)
    s6, _ = _signal_eps_var_3yr(row)

    return min(100, s1 + s2 + s3 + s4 + s5 + s6)


def get_risk_breakdown(row):
    """
    Returns exact points per signal and total score.
    Used in dashboard deep dive panel.

    Returns:
        dict - signal names as keys, points as values
    """
    if not isinstance(row, dict):
        row = row.to_dict()

    s1, _ = _signal_qtr_profit_var(row)
    s2, _ = _signal_profit_var_3yr(row)
    s3, _ = _signal_ebidt_var_3yr(row)
    s4, _ = _signal_opm(row)
    s5, _ = _signal_div_yield(row)
    s6, _ = _signal_eps_var_3yr(row)

    total = min(100, s1 + s2 + s3 + s4 + s5 + s6)

    return {
        'Quarterly Profit Variance (max 20)': s1,
        '3 Year Profit Trend       (max 30)': s2,
        '3 Year EBITDA Trend       (max 25)': s3,
        'Operating Margin          (max 15)': s4,
        'Dividend Yield            (max  5)': s5,
        'EPS 3 Year Trend          (max  5)': s6,
        'Total Risk Score':                   total,
    }


def get_risk_label(score):
    """
    Converts numeric score to human readable risk category.

    Returns:
        str
    """
    if score <= 20:
        return "Low Risk"
    elif score <= 40:
        return "Moderate Risk"
    elif score <= 60:
        return "Elevated Risk"
    else:
        return "High Risk"


def get_risk_color(score):
    """
    Returns a colour string for dashboard display.

    Returns:
        str - 'green', 'yellow', 'orange', or 'red'
    """
    if score <= 20:
        return "green"
    elif score <= 40:
        return "yellow"
    elif score <= 60:
        return "orange"
    else:
        return "red"


def get_risk_reasons(row):
    """
    Returns plain English reasons why the company scored
    the way it did. Includes individual signal reasons
    and composite flags.

    Sorted by impact - highest scoring signals first.
    Maximum 5 reasons to keep dashboard readable.
    Written for a CFO, not a data scientist.

    Returns:
        list of str
    """
    if not isinstance(row, dict):
        row = row.to_dict()

    signals = [
        _signal_profit_var_3yr(row),
        _signal_ebidt_var_3yr(row),
        _signal_opm(row),
        _signal_qtr_profit_var(row),
        _signal_div_yield(row),
        _signal_eps_var_3yr(row),
    ]

    # Sort by points descending - highest impact first
    fired = sorted(
        [(pts, reason) for pts, reason in signals if pts > 0 and reason],
        key=lambda x: x[0],
        reverse=True
    )

    reasons = [reason for _, reason in fired[:4]]

    # Add composite flags (these are qualitative warnings)
    composite = _composite_flags(row)
    if composite:
        reasons.append(composite[0])  # add most important composite flag

    if not reasons:
        reasons.append(
            "No significant risk flags detected across all 6 signals. "
            "Earnings are stable and margins are healthy."
        )

    return reasons


def get_risk_summary(row):
    """
    Returns a single sentence summary of the risk assessment.
    Used in the deck and executive summary.

    Returns:
        str
    """
    if not isinstance(row, dict):
        row = row.to_dict()

    score = compute_risk_score(row)
    label = get_risk_label(score)
    name  = row.get(COL_NAME, 'This company')

    opm      = row.get(COL_OPM, np.nan)
    profit3  = row.get(COL_PROFIT_VAR_3YR, np.nan)
    qtr      = row.get(COL_QTR_PROFIT_VAR, np.nan)

    if score <= 20:
        return (f"{name} presents low financial risk (score {score}/100) with stable earnings, "
                f"healthy margins, and consistent 3-year performance.")
    elif score <= 40:
        return (f"{name} presents moderate financial risk (score {score}/100) with some earnings "
                f"volatility but no structural red flags.")
    elif score <= 60:
        if not pd.isna(opm) and opm < 0:
            return (f"{name} presents elevated financial risk (score {score}/100) - "
                    f"currently operating at a loss with OPM of {opm:.1f}%.")
        elif not pd.isna(profit3) and profit3 < -10:
            return (f"{name} presents elevated financial risk (score {score}/100) - "
                    f"profits declined {abs(profit3):.1f}% over 3 years indicating structural concern.")
        else:
            return (f"{name} presents elevated financial risk (score {score}/100) - "
                    f"multiple financial stress signals detected.")
    else:
        return (f"{name} presents high financial risk (score {score}/100) - "
                f"significant structural and operational concerns, recommend against acquisition.")


def score_full_dataset(df):
    """
    Scores all companies in the cleaned dataset.
    Adds risk_score, risk_label, risk_color columns.

    Parameters:
        df : pandas DataFrame - cleaned_targets.csv

    Returns:
        pandas DataFrame with risk columns added
    """
    df = df.copy()
    df['risk_score'] = df.apply(compute_risk_score, axis=1)
    df['risk_label'] = df['risk_score'].apply(get_risk_label)
    df['risk_color'] = df['risk_score'].apply(get_risk_color)
    return df
