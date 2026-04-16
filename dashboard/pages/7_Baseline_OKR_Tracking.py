"""
Page 7: Baseline & OKR Tracking
Feb baseline vs latest week comparison. Monthly trajectory toward Q2 targets.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import load_weekly_ga4_summary, load_weekly_gsc_summary, format_duration
from config import COLORS, OKR_TARGETS, ORGANIC_BASELINE

st.set_page_config(page_title="Baseline & OKR", page_icon="🎯", layout="wide")
st.markdown("# 🎯 Baseline & OKR Tracking")
st.markdown("Feb 22–28 organic baseline vs latest week. Monthly trajectory toward Q2 targets.")
st.markdown("---")

with st.spinner("Loading data..."):
    ga4_weekly = load_weekly_ga4_summary()
    gsc_weekly = load_weekly_gsc_summary()

if ga4_weekly.empty:
    st.error("No data available.")
    st.stop()

latest = ga4_weekly.iloc[-1]
baseline = ORGANIC_BASELINE

# ─── Baseline Comparison ─────────────────────────────────

st.markdown("### Organic Baseline vs Latest Week")
st.markdown(f"**Baseline:** {baseline['week']} (true organic, no campaign distortion)")
st.markdown(f"**Latest:** {latest['week']}")

comparison = [
    {"Metric": "Sessions", "Baseline": f"{baseline['sessions']:,}", "Latest": f"{int(latest['sessions']):,}",
     "Change": f"{round((latest['sessions'] - baseline['sessions']) / baseline['sessions'] * 100, 1):+.1f}%"},
    {"Metric": "Users", "Baseline": f"{baseline['users']:,}", "Latest": f"{int(latest['users']):,}",
     "Change": f"{round((latest['users'] - baseline['users']) / baseline['users'] * 100, 1):+.1f}%"},
    {"Metric": "Bounce Rate", "Baseline": f"{baseline['bounce_rate']}%", "Latest": f"{latest['bounce_rate']}%",
     "Change": f"{round(latest['bounce_rate'] - baseline['bounce_rate'], 1):+.1f}pp"},
    {"Metric": "Engagement Rate", "Baseline": f"{baseline['engagement_rate']}%", "Latest": f"{latest['engagement_rate']}%",
     "Change": f"{round(latest['engagement_rate'] - baseline['engagement_rate'], 1):+.1f}pp"},
    {"Metric": "Avg Duration", "Baseline": format_duration(baseline['avg_duration_seconds']),
     "Latest": format_duration(latest['avg_duration']),
     "Change": f"{int(latest['avg_duration'] - baseline['avg_duration_seconds']):+d}s"},
]

# Add GSC comparison
latest_gsc = gsc_weekly.iloc[-1] if not gsc_weekly.empty else None
if latest_gsc is not None:
    comparison.extend([
        {"Metric": "GSC Clicks", "Baseline": f"{baseline['gsc_clicks']:,}", "Latest": f"{int(latest_gsc['clicks']):,}",
         "Change": f"{round((latest_gsc['clicks'] - baseline['gsc_clicks']) / baseline['gsc_clicks'] * 100, 1):+.1f}%"},
        {"Metric": "GSC Impressions", "Baseline": f"{baseline['gsc_impressions']:,}", "Latest": f"{int(latest_gsc['impressions']):,}",
         "Change": f"{round((latest_gsc['impressions'] - baseline['gsc_impressions']) / baseline['gsc_impressions'] * 100, 1):+.1f}%"},
        {"Metric": "GSC Avg Position", "Baseline": f"{baseline['gsc_avg_position']}", "Latest": f"{latest_gsc['avg_position']}",
         "Change": f"{round(baseline['gsc_avg_position'] - latest_gsc['avg_position'], 1):+.1f} positions"},
        {"Metric": "GSC CTR", "Baseline": f"{baseline['gsc_ctr']}%", "Latest": f"{latest_gsc['ctr']}%",
         "Change": f"{round(latest_gsc['ctr'] - baseline['gsc_ctr'], 1):+.1f}pp"},
    ])

comp_df = pd.DataFrame(comparison)

def style_change(val):
    if isinstance(val, str):
        if val.startswith("+") and "pp" not in val and "position" not in val:
            return "background-color: #d4edda"
        elif val.startswith("-") and "pp" not in val:
            return "background-color: #f8d7da"
        elif "positions" in val and val.startswith("+"):
            return "background-color: #d4edda"
    return ""

st.dataframe(comp_df.style.applymap(style_change, subset=["Change"]),
             use_container_width=True, hide_index=True)

st.markdown("---")

# ─── Context Notes ────────────────────────────────────────

st.markdown("### Context Notes")
st.markdown("""
1. **Feb sessions inflated by email campaigns** — 280 + 3,360 email sessions in weeks 2–3 with 70–80% bounce.
2. **Excluding email, organic baseline is ~4,000–5,000 sessions/week** or ~18,000/month.
3. **Bounce rate improving organically** — trend from 69.5% (Feb) toward 62.6% target.
4. **Post-campaign decay pattern** — Traffic spikes from announcements follow a surge → normalization within 1–2 weeks.
5. **S1/S2 strategy work** — Tracking whether SEO/AEO sprints show measurable impact vs Feb baseline.
""")

st.markdown("---")

# ─── Monthly OKR Trajectory ──────────────────────────────

st.markdown("### Monthly Trajectory Toward Q2 Targets")

# Calculate monthly approximations from weekly data
months = {}
for _, row in ga4_weekly.iterrows():
    month = row["week"][:3]
    if month not in months:
        months[month] = {"sessions": 0, "bounce_rates": [], "weeks": 0}
    months[month]["sessions"] += row["sessions"]
    months[month]["bounce_rates"].append(row["bounce_rate"])
    months[month]["weeks"] += 1

monthly_data = []
for month, data in months.items():
    avg_bounce = round(sum(data["bounce_rates"]) / len(data["bounce_rates"]), 1)
    monthly_data.append({
        "Month": month, "Sessions": int(data["sessions"]),
        "Bounce Rate": avg_bounce, "Weeks": data["weeks"],
    })

monthly_df = pd.DataFrame(monthly_data)

if not monthly_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Monthly Sessions")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly_df["Month"], y=monthly_df["Sessions"],
                             marker_color=COLORS["info"], name="Actual"))
        fig.add_hline(y=OKR_TARGETS["sessions_target_q2"], line_dash="dash",
                      line_color="green", annotation_text=f"Q2 Target: {OKR_TARGETS['sessions_target_q2']:,}")
        fig.add_hline(y=OKR_TARGETS["sessions_baseline_feb"], line_dash="dot",
                      line_color="grey", annotation_text=f"Feb Baseline: {OKR_TARGETS['sessions_baseline_feb']:,}")
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Monthly Bounce Rate")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=monthly_df["Month"], y=monthly_df["Bounce Rate"],
                              marker_color=[COLORS["success"] if b <= OKR_TARGETS["bounce_target_q2"]
                                           else COLORS["warning"] if b <= OKR_TARGETS["bounce_baseline_feb"]
                                           else COLORS["danger"] for b in monthly_df["Bounce Rate"]],
                              name="Actual"))
        fig2.add_hline(y=OKR_TARGETS["bounce_target_q2"], line_dash="dash",
                      line_color="green", annotation_text=f"Q2 Target: {OKR_TARGETS['bounce_target_q2']}%")
        fig2.add_hline(y=OKR_TARGETS["bounce_baseline_feb"], line_dash="dot",
                      line_color="grey", annotation_text=f"Feb Baseline: {OKR_TARGETS['bounce_baseline_feb']}%")
        fig2.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(monthly_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ─── Key Finding ──────────────────────────────────────────

bounce_change = round(latest["bounce_rate"] - baseline["bounce_rate"], 1)
if abs(bounce_change) < 2:
    st.warning(
        f"**Key Finding:** No significant quality improvement vs Feb baseline. "
        f"Bounce rate {latest['bounce_rate']}% in {latest['week']} vs {baseline['bounce_rate']}% "
        f"in {baseline['week']} (essentially same). Any recent 'improvement' may only be relative to "
        f"abnormal campaign-heavy weeks, not a real gain."
    )
elif bounce_change < -3:
    st.success(
        f"**Key Finding:** Bounce rate improved by {abs(bounce_change):.1f}pp vs baseline "
        f"({latest['bounce_rate']}% vs {baseline['bounce_rate']}%). "
        f"{'On track for Q2 target.' if latest['bounce_rate'] <= OKR_TARGETS['bounce_target_q2'] + 2 else 'Progress but more work needed.'}"
    )

st.markdown("---")
st.caption("Baseline: Feb 22–28 (organic, no campaign distortion) | Targets: Q2 2026")
