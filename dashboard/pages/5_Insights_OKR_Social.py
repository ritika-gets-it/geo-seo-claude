"""
Page 5: Insights, OKR & Social
Weekly commentary, baseline/OKR tracking, and social media performance.
Three tabs in one page.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
from datetime import datetime, timedelta

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
# Tab 3: Social Performance (Agorapulse)
# ═══════════════════════════════════════════════════════════

with tab_social:
    st.markdown("### Social Media Performance")
    st.markdown("*Live data from Agorapulse — 11 profiles across Animoca Brands & Minds.*")

    SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
    sys.path.insert(0, SCRIPTS_DIR)

    @st.cache_data(ttl=86400)
    def load_agorapulse_data(since, until):
        try:
            from agorapulse_fetcher import get_all_profiles_summary
            return get_all_profiles_summary(since, until)
        except Exception as e:
            return {"error": str(e)}

    # Date range for social data
    col_s1, col_s2, _ = st.columns([1, 1, 2])
    with col_s1:
        soc_start = st.date_input("From", datetime.now() - timedelta(days=30), key="soc_s")
    with col_s2:
        soc_end = st.date_input("To", datetime.now(), key="soc_e")

    soc_start_str = soc_start.strftime("%Y-%m-%d")
    soc_end_str = soc_end.strftime("%Y-%m-%d")

    with st.spinner("Loading social data from Agorapulse..."):
        social_results = load_agorapulse_data(soc_start_str, soc_end_str)

    if isinstance(social_results, dict) and "error" in social_results:
        st.error(f"Agorapulse connection error: {social_results['error']}")
        st.info("Check that your API key is saved at `~/.claude/google/agorapulse.txt`")
    elif isinstance(social_results, list):
        # Split into Brands and Minds
        brands_data = [r for r in social_results if "Brands" in r.get("name", "")]
        minds_data = [r for r in social_results if "Minds" in r.get("name", "")]

        sub_brands, sub_minds = st.tabs(["Animoca Brands", "Animoca Minds"])

        for tab, data, label in [(sub_brands, brands_data, "Brands"), (sub_minds, minds_data, "Minds")]:
            with tab:
                if not data:
                    st.info(f"No data for Animoca {label}")
                    continue

                rows = []
                error_details = []
                per_profile_details = []
                for profile in data:
                    if profile.get("unsupported"):
                        rows.append({
                            "Platform": profile["platform"],
                            "Status": "Not supported by Agorapulse API",
                        })
                        continue
                    if "error" in profile:
                        rows.append({
                            "Platform": profile["platform"],
                            "Status": "Error",
                        })
                        error_details.append((profile["platform"], profile["error"]))
                        continue

                    audience = profile.get("audience") or {}
                    days = audience.get("data") or []
                    valid_days = [
                        d for d in days
                        if d.get("viewsCount") is not None
                        and d.get("followersCount") is not None
                    ]

                    if not valid_days:
                        rows.append({
                            "Platform": profile["platform"],
                            "Status": "No data for selected range",
                        })
                        continue

                    def _sum(field):
                        return sum((d.get(field) or 0) for d in valid_days)

                    total_views = _sum("viewsCount")
                    total_engagements = _sum("engagementCount")
                    total_likes = _sum("likesCount")
                    total_comments = _sum("receivedCommentsCount")
                    total_shares = _sum("sharesCount")
                    total_videos = _sum("publishedVideoCount")
                    follower_change = _sum("followersGainedCount")
                    end_followers = valid_days[-1]["followersCount"]
                    start_followers = valid_days[0]["followersCount"]
                    eng_rate = (total_engagements / total_views * 100) if total_views else 0.0

                    rows.append({
                        "Platform": profile["platform"],
                        "Followers (end)": f"{end_followers:,}",
                        "Follower Δ": f"{follower_change:+,}",
                        "Views": f"{total_views:,}",
                        "Engagements": f"{total_engagements:,}",
                        "Eng Rate": f"{eng_rate:.2f}%",
                        "Likes": f"{total_likes:,}",
                        "Comments": f"{total_comments:,}",
                        "Shares": f"{total_shares:,}",
                        "Posts": f"{total_videos:,}",
                    })

                    per_profile_details.append({
                        "profile": profile,
                        "valid_days": valid_days,
                        "start_followers": start_followers,
                        "end_followers": end_followers,
                    })

                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                if error_details:
                    with st.expander(f"Full error details ({len(error_details)})"):
                        for platform, err in error_details:
                            st.markdown(f"**{platform}**")
                            st.code(str(err))

                for detail in per_profile_details:
                    profile = detail["profile"]
                    valid_days = detail["valid_days"]

                    with st.expander(f"{profile['platform']} — {profile['name']} (daily detail)"):
                        df = pd.DataFrame(valid_days)
                        df["date"] = pd.to_datetime(df["date"])
                        df = df.sort_values("date")

                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric(
                            "Followers",
                            f"{detail['end_followers']:,}",
                            f"{detail['end_followers'] - detail['start_followers']:+,}",
                        )
                        total_views = int(df["viewsCount"].sum())
                        total_eng = int(df["engagementCount"].sum())
                        m2.metric("Total views", f"{total_views:,}")
                        m3.metric("Total engagements", f"{total_eng:,}")
                        m4.metric(
                            "Avg eng rate",
                            f"{(total_eng / total_views * 100) if total_views else 0:.2f}%",
                        )

                        best = df.loc[df["engagementCount"].idxmax()] if len(df) and df["engagementCount"].max() > 0 else None
                        if best is not None:
                            st.caption(
                                f"Best engagement day: **{best['date'].strftime('%Y-%m-%d')}** — "
                                f"{int(best['engagementCount'])} engagements on {int(best['viewsCount'])} views "
                                f"({best['engagementRatePerView']:.1f}% rate)"
                            )

                        st.markdown("**Daily trend**")
                        trend_cols = [c for c in ["viewsCount", "engagementCount", "followersCount"] if c in df.columns]
                        if trend_cols:
                            st.line_chart(df.set_index("date")[trend_cols], height=220)

                        st.markdown("**Day-by-day**")
                        column_map = [
                            ("date", "Date"),
                            ("followersCount", "Followers"),
                            ("followersGainedCount", "Follower Δ"),
                            ("viewsCount", "Views"),
                            ("engagementCount", "Engagements"),
                            ("engagementRatePerView", "Eng Rate %"),
                            ("likesCount", "Likes"),
                            ("receivedCommentsCount", "Comments"),
                            ("sharesCount", "Shares"),
                            ("publishedVideoCount", "Posts"),
                        ]
                        available = [(src, label) for src, label in column_map if src in df.columns]
                        display_df = df[[src for src, _ in available]].copy()
                        if "date" in display_df.columns:
                            display_df["date"] = pd.to_datetime(display_df["date"]).dt.strftime("%Y-%m-%d")
                        display_df.columns = [label for _, label in available]
                        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### Connected Profiles")
        profiles_table = []
        for r in social_results:
            profiles_table.append({
                "Platform": r["platform"],
                "Account": r["name"],
                "Profile ID": r["profile_uid"],
                "Status": "Error" if "error" in r else "Connected",
            })
        st.dataframe(pd.DataFrame(profiles_table), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.caption("Data: Agorapulse API | 11 profiles | Refreshes daily")

st.markdown("---")
st.caption("Data: GA4, GSC | Manual: Commentary, Social metrics")
