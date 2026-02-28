# dashboard/app.py
# ============================================================
# RISKFERA AI — M8: Dashboard (Ranked Table + Sidebar)
#
# Run:
#   streamlit run dashboard/app.py
#
# Needs:
#   output/ranked_targets.csv   ← run scoring/final_score.py first
#   config.py                   ← M6
# ============================================================

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import INNOVATECH, ACQUISITION_CONSTRAINTS

# ── Page config — must be FIRST streamlit call ────────────────────────────────
st.set_page_config(
    page_title="RISKFERA AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global background ── */
[data-testid="stAppViewContainer"] {
    background-color: #0d1b2a;
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #112240;
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * {
    color: #c8d8e8 !important;
}

/* ── Headings ── */
h1 { color: #f4b942 !important; font-size: 2rem !important; }
h2, h3 { color: #f4b942 !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background-color: #112240;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 16px;
}
[data-testid="metric-container"] label {
    color: #8899aa !important;
    font-size: 0.8rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f4b942 !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    overflow: hidden;
}

/* ── Divider ── */
hr { border-color: #1e3a5f !important; }

/* ── Buttons ── */
.stButton > button {
    background-color: #f4b942;
    color: #0d1b2a;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    width: 100%;
}
.stButton > button:hover {
    background-color: #e0a830;
    color: #0d1b2a;
}

/* ── Selectbox + sliders ── */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background-color: #0d1b2a !important;
    border-color: #1e3a5f !important;
}

/* ── Warning / info ── */
.stWarning {
    background-color: #2a1f0d !important;
    border-left: 3px solid #f4b942 !important;
}

/* ── Caption text ── */
.stCaption { color: #8899aa !important; }

/* ── Score badge helper classes ── */
.badge-green  { background:#0a2a1a; color:#00cc88; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.85rem; }
.badge-yellow { background:#2a2000; color:#f4b942; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.85rem; }
.badge-orange { background:#2a1500; color:#ff9944; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.85rem; }
.badge-red    { background:#2a0a0a; color:#ff4b4b; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.85rem; }
</style>
""", unsafe_allow_html=True)


# ── Data loader ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    path = 'output/ranked_targets.csv'
    if not os.path.isfile(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    return df


# ── Helper: detect name column ────────────────────────────────────────────────
def get_name_col(df):
    return next(
        (c for c in df.columns if 'name' in c.lower() or 'company' in c.lower()),
        df.columns[0]
    )


# ── Helper: colour a score cell ───────────────────────────────────────────────
def score_colour(val):
    """
    Used by pandas Styler to colour score columns.
    Green = good, Red = bad.
    """
    if not isinstance(val, (int, float)):
        return ''
    if val >= 65:
        return 'background-color: #0a2a1a; color: #00cc88; font-weight: 700'
    if val >= 45:
        return 'background-color: #2a2000; color: #f4b942; font-weight: 700'
    if val >= 30:
        return 'background-color: #2a1500; color: #ff9944; font-weight: 700'
    return 'background-color: #2a0a0a; color: #ff4b4b; font-weight: 700'


def risk_colour(val):
    """
    Risk is INVERTED — lower risk score = better = green.
    """
    if not isinstance(val, (int, float)):
        return ''
    if val <= 20:
        return 'background-color: #0a2a1a; color: #00cc88; font-weight: 700'
    if val <= 40:
        return 'background-color: #2a2000; color: #f4b942; font-weight: 700'
    if val <= 60:
        return 'background-color: #2a1500; color: #ff9944; font-weight: 700'
    return 'background-color: #2a0a0a; color: #ff4b4b; font-weight: 700'


# ── Re-rank function ──────────────────────────────────────────────────────────
def rerank(df, budget, min_roce, min_synergy, selected_sectors):
    """
    Filters the dataframe based on sidebar controls
    and re-sorts by attractiveness_score.
    """
    if df.empty:
        return df

    d = df.copy()

    # Budget filter — deal value = mcap * 1.25
    mcap_col = next((c for c in d.columns if 'mar_cap' in c or 'market_cap' in c), None)
    if mcap_col:
        d = d[d[mcap_col] * 1.25 <= budget]

    # Minimum ROCE filter
    roce_col = next((c for c in d.columns if c == 'roce'), None)
    if roce_col and min_roce > 0:
        d = d[d[roce_col] >= min_roce]

    # Minimum synergy filter
    if 'synergy_score' in d.columns and min_synergy > 0:
        d = d[d['synergy_score'] >= min_synergy]

    # Sector filter
    if selected_sectors and 'sector' in d.columns:
        d = d[d['sector'].isin(selected_sectors)]

    # Re-sort
    if 'attractiveness_score' in d.columns:
        d = d.sort_values('attractiveness_score', ascending=False).reset_index(drop=True)
        d['rank'] = d.index + 1

    return d


# ============================================================
# LOAD DATA
# ============================================================
df_full = load_data()

if df_full.empty:
    st.error("⚠️ No data found. Run `python scoring/final_score.py` first to generate output/ranked_targets.csv")
    st.stop()

name_col = get_name_col(df_full)
all_sectors = sorted(df_full['sector'].dropna().unique().tolist()) if 'sector' in df_full.columns else []


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Scenario Controls")
    st.caption("Adjust filters to explore different acquisition scenarios")
    st.divider()

    # Budget slider
    st.markdown("**💰 Max Acquisition Budget (₹ Cr)**")
    budget = st.slider(
        label="budget",
        min_value=50,
        max_value=300,
        value=180,
        step=10,
        label_visibility="collapsed"
    )
    st.caption(f"Deal value = MCap × 1.25  |  Max cash = ₹{round(budget * 0.60)}Cr")

    st.divider()

    # ROCE filter
    st.markdown("**📈 Minimum ROCE (%)**")
    min_roce = st.slider(
        label="min_roce",
        min_value=0,
        max_value=40,
        value=0,
        step=2,
        label_visibility="collapsed"
    )
    if min_roce > 0:
        st.caption(f"InnovaTech benchmark: {INNOVATECH['target_roce']}%")

    st.divider()

    # Minimum synergy filter
    st.markdown("**🤝 Minimum Synergy Score**")
    min_synergy = st.slider(
        label="min_synergy",
        min_value=0,
        max_value=80,
        value=0,
        step=5,
        label_visibility="collapsed"
    )

    st.divider()

    # Sector filter
    st.markdown("**🏭 Sectors**")
    selected_sectors = st.multiselect(
        label="sectors",
        options=all_sectors,
        default=all_sectors,
        label_visibility="collapsed"
    )

    st.divider()

    # Export button
    if st.button("⬇️ Export Filtered Results to Excel"):
        filtered_export = rerank(df_full, budget, min_roce, min_synergy, selected_sectors)
        export_path = 'output/filtered_results.xlsx'
        os.makedirs('output', exist_ok=True)
        filtered_export.to_excel(export_path, index=False)
        st.success(f"✅ Saved to {export_path}")

    st.divider()

    # InnovaTech quick reference
    st.markdown("**📌 InnovaTech Benchmarks**")
    st.markdown(f"""
    <div style='font-size:0.8rem; color:#8899aa; line-height:1.8'>
    Revenue: ₹{INNOVATECH['revenue_cr']} Cr<br>
    Net Profit: ₹{INNOVATECH['net_profit_cr']} Cr<br>
    ROCE: {INNOVATECH['roce_pct']}%<br>
    OPM: {INNOVATECH['operating_margin_pct']}%<br>
    P/E: {INNOVATECH['current_pe']}x<br>
    Budget: ₹{ACQUISITION_CONSTRAINTS['max_deal_value_cr']} Cr<br>
    Max Cash: ₹{ACQUISITION_CONSTRAINTS['max_cash_outflow_cr']} Cr
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================
st.markdown("# 🎯 RISKFERA AI")
st.caption("M&A Target Intelligence Platform — InnovaTech Systems FY2025")
st.divider()

# ── Top metrics row ───────────────────────────────────────────────────────────
df_filtered = rerank(df_full, budget, min_roce, min_synergy, selected_sectors)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Companies Screened",
    len(df_full),
    help="Total companies in dataset"
)
col2.metric(
    "Matching Filters",
    len(df_filtered),
    delta=f"{len(df_filtered) - len(df_full)} from filters",
    delta_color="off",
    help="Companies passing current sidebar filters"
)
col3.metric(
    "Sectors Covered",
    df_full['sector'].nunique() if 'sector' in df_full.columns else "—"
)
col4.metric(
    "Max Budget",
    f"₹{budget} Cr",
    help="Acquisition budget including 25% premium"
)
col5.metric(
    "InnovaTech P/E",
    f"{INNOVATECH['current_pe']}x",
    help="Targets below this P/E are EPS accretive"
)

st.divider()


# ============================================================
# RANKED TABLE
# ============================================================
st.subheader(f"📊 Ranked Acquisition Targets  ({len(df_filtered)} companies)")

if df_filtered.empty:
    st.warning("No companies match the current filters. Try relaxing the budget or ROCE slider.")
else:
    # ── Build display dataframe ───────────────────────────────────────────────
    # Only show the most important columns, rename for readability
    display_cols = {
        'rank':                'Rank',
        name_col:              'Company',
        'sector':              'Sector',
        'risk_score':          'Risk ↓',
        'risk_label':          'Risk Label',
        'synergy_score':       'Synergy ↑',
        'synergy_label':       'Synergy Label',
        'feasibility_score':   'Feasibility ↑',
        'feasibility_label':   'Feasibility Label',
        'attractiveness_score':'Final Score ↑',
    }

    # Add market cap if column exists
    mcap_col = next((c for c in df_filtered.columns if 'mar_cap' in c or 'market_cap' in c), None)
    if mcap_col:
        display_cols[mcap_col] = 'MCap (₹Cr)'

    # Only keep columns that exist
    existing_cols = {k: v for k, v in display_cols.items() if k in df_filtered.columns}
    disp = df_filtered[list(existing_cols.keys())].copy()
    disp = disp.rename(columns=existing_cols)

    # Round numeric columns
    for col in ['Risk ↓', 'Synergy ↑', 'Feasibility ↑', 'Final Score ↑']:
        if col in disp.columns:
            disp[col] = disp[col].round(1)

    if 'MCap (₹Cr)' in disp.columns:
        disp['MCap (₹Cr)'] = disp['MCap (₹Cr)'].round(1)

    # ── Apply colour styling ──────────────────────────────────────────────────
    styled = disp.style

    if 'Risk ↓' in disp.columns:
        styled = styled.applymap(risk_colour, subset=['Risk ↓'])

    for col in ['Synergy ↑', 'Feasibility ↑', 'Final Score ↑']:
        if col in disp.columns:
            styled = styled.applymap(score_colour, subset=[col])

    # Highlight top 5 rows with a subtle gold left border effect
    def highlight_top5(row):
        if row.name < 5:
            return ['border-left: 3px solid #f4b942'] + [''] * (len(row) - 1)
        return [''] * len(row)

    styled = styled.apply(highlight_top5, axis=1)

    # Set table properties
    styled = styled.set_properties(**{
        'background-color': '#0d1b2a',
        'color': '#c8d8e8',
        'border-color': '#1e3a5f',
        'font-size': '13px',
    })

    st.dataframe(
        styled,
        use_container_width=True,
        height=500,
        hide_index=True
    )

    # ── Legend ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='font-size:0.75rem; color:#8899aa; margin-top:8px'>
    🟢 <b>Risk ↓</b> lower is safer &nbsp;|&nbsp;
    🟢 <b>Synergy ↑</b> higher = better strategic fit &nbsp;|&nbsp;
    🟢 <b>Feasibility ↑</b> higher = more doable within ₹180Cr &nbsp;|&nbsp;
    ⭐ <b>Final Score</b> = 40%(100−Risk) + 35%(Synergy) + 25%(Feasibility) &nbsp;|&nbsp;
    🥇 Gold border = Top 5
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# QUICK STATS ROW — below the table
# ============================================================
if not df_filtered.empty and 'attractiveness_score' in df_filtered.columns:
    st.divider()
    st.subheader("📈 Quick Stats")

    qs1, qs2, qs3, qs4 = st.columns(4)

    top1 = df_filtered.iloc[0]
    qs1.metric(
        "🥇 Top Candidate",
        str(top1[name_col])[:25],
        f"Score: {top1['attractiveness_score']:.1f}"
    )

    strong = (df_filtered['attractiveness_score'] >= 65).sum()
    qs2.metric(
        "💪 Strong Candidates",
        strong,
        f"Score ≥ 65"
    )

    low_risk = (df_filtered['risk_score'] <= 20).sum() if 'risk_score' in df_filtered.columns else 0
    qs3.metric(
        "🛡️ Low Risk Companies",
        low_risk,
        "Risk score ≤ 20"
    )

    high_syn = (df_filtered['synergy_score'] >= 75).sum() if 'synergy_score' in df_filtered.columns else 0
    qs4.metric(
        "🤝 High Synergy",
        high_syn,
        "Synergy score ≥ 75"
    )


# ============================================================
# TOP 5 CARDS — visual summary of best candidates
# ============================================================
if not df_filtered.empty:
    st.divider()
    st.subheader("🏆 Top 5 Candidates at a Glance")

    top5 = df_filtered.head(5)
    cols = st.columns(min(5, len(top5)))

    for i, (_, row) in enumerate(top5.iterrows()):
        with cols[i]:
            # Determine colour for final score
            score = row.get('attractiveness_score', 0)
            if score >= 65:
                score_color = "#00cc88"
                bg_color    = "#0a2a1a"
            elif score >= 45:
                score_color = "#f4b942"
                bg_color    = "#2a2000"
            else:
                score_color = "#ff4b4b"
                bg_color    = "#2a0a0a"

            risk_val = row.get('risk_score', 0)
            risk_col = "#00cc88" if risk_val <= 20 else "#f4b942" if risk_val <= 40 else "#ff4b4b"

            syn_val = row.get('synergy_score', 0)
            syn_col = "#00cc88" if syn_val >= 65 else "#f4b942" if syn_val >= 45 else "#ff4b4b"

            feas_val = row.get('feasibility_score', 0)
            feas_col = "#00cc88" if feas_val >= 65 else "#f4b942" if feas_val >= 45 else "#ff4b4b"

            company_name = str(row[name_col])
            sector_name  = str(row.get('sector', '—'))

            st.markdown(f"""
            <div style='
                background: #112240;
                border: 1px solid #1e3a5f;
                border-top: 3px solid {score_color};
                border-radius: 10px;
                padding: 14px;
                text-align: center;
                height: 200px;
            '>
                <div style='font-size:1.1rem; font-weight:800; color:{score_color}'>
                    #{int(row.get('rank', i+1))}
                </div>
                <div style='font-size:0.85rem; font-weight:700; color:#ffffff;
                            margin: 6px 0 2px; line-height:1.2;
                            white-space:nowrap; overflow:hidden; text-overflow:ellipsis'>
                    {company_name[:20]}
                </div>
                <div style='font-size:0.7rem; color:#8899aa; margin-bottom:10px;
                            white-space:nowrap; overflow:hidden; text-overflow:ellipsis'>
                    {sector_name[:22]}
                </div>
                <div style='font-size:1.6rem; font-weight:900; color:{score_color};
                            background:{bg_color}; border-radius:8px; padding:4px'>
                    {score:.1f}
                </div>
                <div style='font-size:0.65rem; color:#8899aa; margin-top:8px;
                            display:flex; justify-content:space-around'>
                    <span style='color:{risk_col}'>R:{risk_val:.0f}</span>
                    <span style='color:{syn_col}'>S:{syn_val:.0f}</span>
                    <span style='color:{feas_col}'>F:{feas_val:.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center; color:#8899aa; font-size:0.75rem; padding: 8px 0'>
    RISKFERA AI &nbsp;|&nbsp; M&A Intelligence Platform &nbsp;|&nbsp;
    Final Score = 40%×(100−Risk) + 35%×Synergy + 25%×Feasibility
</div>
""", unsafe_allow_html=True)


# ── M9, M10, M11 code gets added BELOW this line ─────────────────────────────
