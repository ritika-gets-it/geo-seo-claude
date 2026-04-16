"""
Page 5: Insights, OKR & Social
Weekly commentary, baseline/OKR tracking, and social media performance.
Three tabs in one page.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import (
    load_weekly_ga4_summary, load_weekly_gsc_summary,
    load_weekly_ai_breakdown, format_duration, format_wow,
)
from config import COLORS, WEEKS, OKR_TARGETS, ORGANIC_BASELINE, SOCIAL_PLATFORMS

st.set_page_config(page_title="Insights, OKR & Social", page_icon="💡", layout="wide")
st.markdown("# 💡 Insights, OKR & Social")
st.markdown("Weekly commentary, Q2 target tracking, and social performance.")
st.markdown("---")

with st.spinner("Loading data..."):
    ga4_weekly = load_weekly_ga4_summary()
    gsc_weekly = load_weekly_gsc_summary()
    ai_breakdown = load_weekly_ai_breakdown()

if ga4_weekly.empty:
    st.error("No data available.")
    st.stop()

tab_insights, tab_okr, tab_social = st.tabs(["Weekly Insights", "Baseline & OKR", "Social Performance"])

# ═══════════════════════════════════════════════════════════
# Tab 1: Weekly Insights
# ═══════════════════════════════════════════════════════════

with tab_insights:
    week_labels = [w["label"] for w in WEEKS]
    selected = st.selectbox("Select week", week_labels, index=len(week_labels) - 1, key="ins_w")
    idx = week_labels.index(selected)
    current = ga4_weekly.iloc[idx] if idx < len(ga4_weekly) else None

    if current is not None:
        st.markdown(f"## Week of {selected}")

        # Auto metrics
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Sessions", f"{int(current['sessions']):,}",
                  delta=format_wow(current.get("sessions_wow")) if pd.notna(current.get("sessions_wow")) else None)
        k2.metric("Users", f"{int(current['users']):,}")
        gsc_row = gsc_weekly.iloc[idx] if not gsc_weekly.empty and idx < len(gsc_weekly) else None
        if gsc_row is not None:
            k3.metric("GSC Clicks", f"{int(gsc_row['clicks']):,}")
            k4.metric("GSC Impressions", f"{int(gsc_row['impressions']):,}")
        k5.metric("AI Sessions", f"{int(current['ai_sessions']):,}")

        st.markdown("---")

        # Auto observations
        st.markdown("### Auto-Generated Observations")
        obs = []
        if pd.notna(current.get("sessions_wow")):
            w = current["sessions_wow"]
            obs.append(f"Sessions {'up' if w > 0 else 'down'} {abs(w):.1f}% WoW.")
        if current["bounce_rate"] > 70:
            obs.append(f"Bounce rate {current['bounce_rate']}% — elevated. Check for campaign or bot traffic.")
        elif current["bounce_rate"] < 60:
            obs.append(f"Bounce rate {current['bounce_rate']}% — strong engagement.")
        if current["ai_sessions"] > 0:
            obs.append(f"AI traffic: {int(current['ai_sessions']):,} sessions ({current['ai_share']}%).")
        else:
            obs.append("No AI referral traffic this week.")
        if gsc_row is not None and gsc_row["avg_position"] < 5:
            obs.append(f"Search position strong at {gsc_row['avg_position']}.")

        for i, o in enumerate(obs, 1):
            st.markdown(f"{i}. {o}")

        st.markdown("---")

        # Manual commentary
        st.markdown("### Team Commentary")
        st.text_input("Headline", placeholder="One-line summary of the week...", key=f"h_{selected}")
        st.text_area("Observations", placeholder="Additional notes...", height=120, key=f"o_{selected}")
        st.text_input("Key Question for Team", placeholder="e.g., Should we increase newsroom cadence?", key=f"q_{selected}")
        st.text_area("Recommendations", placeholder="1. ...\n2. ...", height=100, key=f"r_{selected}")
        st.caption("Commentary is session-only. Export to a shared doc for persistence.")

# ═══════════════════════════════════════════════════════════
# Tab 2: Baseline & OKR
# ═══════════════════════════════════════════════════════════

with tab_okr:
    latest = ga4_weekly.iloc[-1]
    baseline = ORGANIC_BASELINE

    st.markdown("### Organic Baseline vs Latest Week")
    st.markdown(f"**Baseline:** {baseline['week']} | **Latest:** {latest['week']}")

    comparison = [
        {"Metric": "Sessions", "Baseline": f"{baseline['sessions']:,}", "Latest": f"{int(latest['sessions']):,}",
         "Change": f"{round((latest['sessions'] - baseline['sessions']) / baseline['sessions'] * 100, 1):+.1f}%"},
        {"Metric": "Users", "Baseline": f"{baseline['users']:,}", "Latest": f"{int(latest['users']):,}",
         "Change": f"{round((latest['users'] - baseline['users']) / baseline['users'] * 100, 1):+.1f}%"},
        {"Metric": "Bounce Rate", "Baseline": f"{baseline['bounce_rate']}%", "Latest": f"{latest['bounce_rate']}%",
         "Change": f"{round(latest['bounce_rate'] - baseline['bounce_rate'], 1):+.1f}pp"},
        {"Metric": "Engagement Rate", "Baseline": f"{baseline['engagement_rate']}%",
         "Latest": f"{latest['engagement_rate']}%",
         "Change": f"{round(latest['engagement_rate'] - baseline['engagement_rate'], 1):+.1f}pp"},
    ]

    latest_gsc = gsc_weekly.iloc[-1] if not gsc_weekly.empty else None
    if latest_gsc is not None:
        comparison.extend([
            {"Metric": "GSC Clicks", "Baseline": f"{baseline['gsc_clicks']:,}",
             "Latest": f"{int(latest_gsc['clicks']):,}",
             "Change": f"{round((latest_gsc['clicks'] - baseline['gsc_clicks']) / baseline['gsc_clicks'] * 100, 1):+.1f}%"},
            {"Metric": "GSC Impressions", "Baseline": f"{baseline['gsc_impressions']:,}",
             "Latest": f"{int(latest_gsc['impressions']):,}",
             "Change": f"{round((latest_gsc['impressions'] - baseline['gsc_impressions']) / baseline['gsc_impressions'] * 100, 1):+.1f}%"},
            {"Metric": "GSC Avg Position", "Baseline": f"{baseline['gsc_avg_position']}",
             "Latest": f"{latest_gsc['avg_position']}",
             "Change": f"{round(baseline['gsc_avg_position'] - latest_gsc['avg_position'], 1):+.1f} positions"},
        ])

    st.dataframe(pd.DataFrame(comparison), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Context Notes")
    st.markdown("""
    1. **Feb sessions inflated by email campaigns** — 280 + 3,360 email sessions in weeks 2-3 with 70-80% bounce.
    2. **True organic baseline is ~4,000-5,000 sessions/week** (~18,000/month) excluding email.
    3. **Bounce rate improving organically** — trend from 69.5% (Feb) toward 62.6% target.
    4. **Post-campaign decay** — traffic spikes from announcements normalize within 1-2 weeks.
    """)

    st.markdown("---")
    st.markdown("### Monthly OKR Trajectory")

    months = {}
    for _, row in ga4_weekly.iterrows():
        month = row["week"][:3]
        if month not in months:
            months[month] = {"sessions": 0, "bounces": [], "weeks": 0}
        months[month]["sessions"] += row["sessions"]
        months[month]["bounces"].append(row["bounce_rate"])
        months[month]["weeks"] += 1

    m_df = pd.DataFrame([{"Month": m, "Sessions": int(d["sessions"]),
                           "Bounce %": round(sum(d["bounces"]) / len(d["bounces"]), 1)}
                          for m, d in months.items()])

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=m_df["Month"], y=m_df["Sessions"], marker_color=COLORS["info"]))
        fig.add_hline(y=OKR_TARGETS["sessions_target_q2"], line_dash="dash", line_color="green",
                      annotation_text=f"Target: {OKR_TARGETS['sessions_target_q2']:,}")
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), title="Monthly Sessions")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=m_df["Month"], y=m_df["Bounce %"],
                              marker_color=[COLORS["success"] if b <= OKR_TARGETS["bounce_target_q2"]
                                           else COLORS["warning"] for b in m_df["Bounce %"]]))
        fig2.add_hline(y=OKR_TARGETS["bounce_target_q2"], line_dash="dash", line_color="green",
                      annotation_text=f"Target: {OKR_TARGETS['bounce_target_q2']}%")
        fig2.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), title="Monthly Bounce Rate")
        st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# Tab 3: Social Performance
# ═══════════════════════════════════════════════════════════

with tab_social:
    st.markdown("### Monthly Social Media Metrics")
    st.markdown("*Data from Agorapulse (when connected) or manual entry.*")

    months = ["Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026"]
    selected_month = st.selectbox("Month", months, index=len(months) - 1, key="soc_m")

    social_data = [{"Platform": p, "Followers": "—", "Net New": "—",
                    "Reach": "—", "Engagement %": "—", "Posts": "—"}
                   for p in SOCIAL_PLATFORMS]
    st.dataframe(pd.DataFrame(social_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Agorapulse Integration")
    st.info("""
    **To connect Agorapulse:**
    1. Go to Agorapulse > Settings > API
    2. Generate an API key
    3. Share it and we'll auto-populate this table

    Once connected, follower counts, reach, engagement, and posting cadence
    will update automatically.
    """)

    st.markdown("---")
    st.markdown("### Quick Manual Entry")

    col1, col2 = st.columns(2)
    with col1:
        for platform in SOCIAL_PLATFORMS[:3]:
            st.markdown(f"**{platform}**")
            st.number_input(f"Followers", 0, key=f"{platform}_f")
            st.number_input(f"Engagement %", 0.0, step=0.1, key=f"{platform}_e")
    with col2:
        for platform in SOCIAL_PLATFORMS[3:]:
            st.markdown(f"**{platform}**")
            st.number_input(f"Followers", 0, key=f"{platform}_f")
            st.number_input(f"Engagement %", 0.0, step=0.1, key=f"{platform}_e")

    st.caption("Manual entries are session-only.")

st.markdown("---")
st.caption("Data: GA4, GSC | Manual: Commentary, Social metrics")
