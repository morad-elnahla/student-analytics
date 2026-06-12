import pandas as pd
import numpy as np
import warnings
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import base64, io
from PIL import Image
from pymongo import MongoClient

warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Analytics · Kayfa",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Logo ───────────────────────────────────────────────────────────────────────
def _clean_logo(path):
    try:
        img = Image.open(path).convert("RGBA")
        arr = np.array(img)
        white = (arr[:, :, 0] > 230) & (arr[:, :, 1] > 230) & (arr[:, :, 2] > 230)
        arr[white, 3] = 0
        buf = io.BytesIO()
        Image.fromarray(arr).save(buf, "PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""

LOGO_B64 = _clean_logo("logo.png")
LOGO_IMG = f'<img src="data:image/png;base64,{LOGO_B64}" style="{{s}}">'

# ── Palette ────────────────────────────────────────────────────────────────────
PRIMARY = "#6366f1"
GREEN   = "#2ecc71"
RED     = "#e74c3c"
ORANGE  = "#f97316"
BLUE    = "#3498db"
PURPLE  = "#9b59b6"

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');

html,body,[class*="css"],.stApp {
    font-family:'DM Sans',sans-serif !important;
}
.main .block-container {
    padding-top:1.8rem !important;
    padding-bottom:3rem !important;
    max-width:1400px !important;
}

/* ── KPI Cards ── */
.kpi-card {
    background:rgba(99,102,241,0.04);
    border:1px solid rgba(99,102,241,0.15);
    border-radius:16px;
    padding:1.4rem 1.7rem 1.2rem;
    position:relative;
    overflow:hidden;
    height:100%;
}
.kpi-card-1::before { content:''; position:absolute; top:0;left:0;right:0;height:3px; background:linear-gradient(90deg,#6366f1,#818cf8); border-radius:16px 16px 0 0; }
.kpi-card-2::before { content:''; position:absolute; top:0;left:0;right:0;height:3px; background:linear-gradient(90deg,#2ecc71,#27ae60); border-radius:16px 16px 0 0; }
.kpi-card-3::before { content:''; position:absolute; top:0;left:0;right:0;height:3px; background:linear-gradient(90deg,#f97316,#fb923c); border-radius:16px 16px 0 0; }
.kpi-card-4::before { content:''; position:absolute; top:0;left:0;right:0;height:3px; background:linear-gradient(90deg,#e74c3c,#f87171); border-radius:16px 16px 0 0; }
.kpi-card-5::before { content:''; position:absolute; top:0;left:0;right:0;height:3px; background:linear-gradient(90deg,#9b59b6,#8e44ad); border-radius:16px 16px 0 0; }
.kpi-label {
    font-size:0.66rem;
    font-weight:700;
    letter-spacing:0.13em;
    text-transform:uppercase;
    margin-bottom:0.6rem;
    opacity:0.6;
}
.kpi-value {
    font-family:'Inter',sans-serif !important;
    font-size:2.2rem;
    font-weight:800;
    line-height:1;
    margin-bottom:0.35rem;
    letter-spacing:-0.03em;
}
.kpi-blue   { color:#6366f1; }
.kpi-green  { color:#2ecc71; }
.kpi-orange { color:#f97316; }
.kpi-red    { color:#e74c3c; }
.kpi-purple { color:#9b59b6; }
.kpi-sub    { font-size:0.73rem; font-weight:500; opacity:0.5; }

/* ── Section headers ── */
.sec-head {
    display:flex;
    align-items:center;
    gap:0.8rem;
    margin:2.2rem 0 1rem;
}
.sec-dot {
    width:8px;height:8px;
    border-radius:50%;
    background:#6366f1;
    flex-shrink:0;
}
.sec-title {
    font-size:1rem;
    font-weight:800;
    color:#6366f1;
    letter-spacing:0.06em;
    text-transform:uppercase;
    white-space:nowrap;
}
.sec-line {
    flex:1;
    height:1px;
    background:rgba(99,102,241,0.2);
}

/* ── Insight boxes ── */
.insight {
    background:rgba(99,102,241,0.06);
    border:1px solid rgba(99,102,241,0.2);
    border-left:3px solid #6366f1;
    border-radius:0 12px 12px 0;
    padding:1.1rem 1.4rem;
    margin-top:0.6rem;
    font-size:0.95rem;
    line-height:1.75;
}
.itag {
    display:inline-flex;
    align-items:center;
    gap:0.3rem;
    background:rgba(99,102,241,0.12);
    color:#6366f1;
    font-size:0.72rem;
    font-weight:700;
    letter-spacing:0.09em;
    text-transform:uppercase;
    padding:0.22rem 0.75rem;
    border-radius:20px;
    margin-bottom:0.55rem;
    border:1px solid rgba(99,102,241,0.2);
}
.stAlert { border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)


# ── MongoDB connection ───────────────────────────────────────────────────────
def _get_mongo_uri():
    # Works both locally (.env via os.environ) and on Streamlit Cloud (st.secrets)
    if "MONGO_URI" in st.secrets:
        return st.secrets["MONGO_URI"]
    return os.getenv("MONGO_URI")


@st.cache_resource
def get_client():
    uri = _get_mongo_uri()
    return MongoClient(uri)


@st.cache_data(ttl=3600)
def load_collection(name):
    client = get_client()
    db = client["kayfa_analytics"]
    docs = list(db[name].find({}, {"_id": 0}))
    return pd.DataFrame(docs)


# ── Load all precomputed collections from Atlas ──────────────────────────────
att_group      = load_collection("group_attendance")        # Q1
type_stats     = load_collection("score_by_type")            # Q2
course_stats   = load_collection("course_performance")       # Q3
q4_df          = load_collection("attendance_vs_grade")       # Q4
q5_df          = load_collection("engagement_vs_performance") # Q5
concept_fail   = load_collection("concept_failures")          # Q6
mastery_trend_raw = load_collection("concept_mastery_trend")  # Q7
sub_grade      = load_collection("late_submission_effect")    # Q8
# Fix: is_late might come back as string "True"/"False" from MongoDB
if len(sub_grade) > 0 and "is_late" in sub_grade.columns:
    sub_grade["is_late"] = sub_grade["is_late"].map(
        {True: True, False: False, "True": True, "False": False, 1: True, 0: False}
    )
combined       = load_collection("engagement_over_time")      # Q9
age_stats      = load_collection("age_band_analysis")         # Q10
clusters_df    = load_collection("student_clusters")          # Q11
q12_df         = load_collection("group_size_discrepancy")    # Q12
q13_df         = load_collection("nonviable_group")           # Q13
q13_profile = load_collection("q13_profile_comparison")
top10          = load_collection("at_risk_students")          # Q14
trend_df       = load_collection("group_grade_trends")        # Q15
grade_trend_raw = load_collection("group_grade_trends_raw")   # Q15 raw lines
master         = load_collection("master_students")           # KPIs


# ── Helpers ────────────────────────────────────────────────────────────────────
def qlayout(fig, h=400):
    fig.update_layout(
        height=h,
        margin=dict(t=50, b=18, l=10, r=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        template="plotly_white",
        font=dict(family="DM Sans", size=11),
        title_font=dict(family="DM Sans", size=13, weight=600),
    )
    fig.update_xaxes(gridcolor="rgba(0,0,0,0.05)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0.05)", zeroline=False)
    return fig

def insight_box(emoji, tag, text):
    return (f"<div class='insight'>"
            f"<div class='itag'>{emoji} {tag}</div><br>{text}</div>")

def sec(title):
    return (f"<div class='sec-head'>"
            f"<span class='sec-dot'></span>"
            f"<span class='sec-title'>{title}</span>"
            f"<span class='sec-line'></span></div>")


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;padding:0 0 0.6rem">
  <div>
    <div style="font-size:2rem;font-weight:800;letter-spacing:-0.02em;line-height:1.1">
      <span style="color:#6366f1;font-size:1.50rem;font-weight:700;
                    letter-spacing:0.08em;text-transform:uppercase;display:block;
                    margin-bottom:0.3rem">Week #2 Task:</span>
      Student Analytics Dashboard
    </div>
    <div style="font-size:0.78rem;margin-top:0.2rem;font-weight:500;opacity:0.5">
      ~500 students · 10 groups · 7 courses · 6-month term &nbsp;·&nbsp;
      Kayfa AI &amp; Data Analytics &nbsp;·&nbsp; Week 2 &nbsp;·&nbsp; Powered by MongoDB Atlas
    </div>
  </div>
  {LOGO_IMG.format(s="height:50px;flex-shrink:0;position:relative;top:-60px")}
</div>
<hr style="margin:0.4rem 0 1.2rem;opacity:0.15">
""", unsafe_allow_html=True)


# ── KPIs ───────────────────────────────────────────────────────────────────────
total_students = len(master)
avg_att        = master["attendance_rate"].mean() if "attendance_rate" in master.columns else 0
avg_grade      = master["avg_grade_pct"].mean() if "avg_grade_pct" in master.columns else 0
avg_logins     = master["login_count"].mean() if "login_count" in master.columns else 0
at_risk_count  = int(((master["attendance_rate"] < 60) & (master["avg_grade_pct"] < 60)).sum()) \
    if {"attendance_rate", "avg_grade_pct"}.issubset(master.columns) else 0

c1, c2, c3, c4, c5 = st.columns(5)
for col, label, val, cls, sub, card_cls in [
    (c1, "Students",          f"{total_students:,}",   "kpi-blue",   "across the platform",        "kpi-card-1"),
    (c2, "Avg Attendance",    f"{avg_att:.1f}%",        "kpi-green",  "platform attendance rate",   "kpi-card-2"),
    (c3, "Avg Grade",         f"{avg_grade:.1f}%",      "kpi-orange", "across all assessments",     "kpi-card-3"),
    (c4, "Avg Logins",        f"{avg_logins:.0f}",      "kpi-purple", "per student (term)",         "kpi-card-5"),
    (c5, "At-Risk Students",  f"{at_risk_count}",       "kpi-red",    "low att. AND low grade",     "kpi-card-4"),
]:
    with col:
        st.markdown(f"""
        <div class='kpi-card {card_cls}'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-value {cls}'>{val}</div>
          <div class='kpi-sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊  Q1–Q3: Attendance & Grades",
    "🔗  Q4–Q5: Attendance & Engagement",
    "📚  Q6–Q7: Concept Mastery",
    "⏰  Q8–Q10: Submissions & Time",
    "🎯  Q11–Q13: Segmentation & Groups",
    "🚨  Q14–Q15: At-Risk & Trends",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 · Q1 Q2 Q3
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:

    # ── Q1 ───────────────────────────────────────────────────────────────────
    st.markdown(sec("Q1 · Attendance Rate per Group — Which Sit Below Platform Average?"), unsafe_allow_html=True)

    platform_avg = att_group["att_rate"].mean()
    if "status" in att_group.columns:
        att_group = att_group.rename(columns={"status": "status_label"})

    COLOR_MAP_ATT = {
        "Well Below Average (>10 pp)": RED,
        "Below Average": ORANGE,
        "At / Above Average": GREEN,
    }

    fig = px.bar(att_group.sort_values("att_rate"), x="att_rate", y="group_name", orientation="h",
                 color="status_label", color_discrete_map=COLOR_MAP_ATT,
                 title="Q1 — Attendance Rate per Group",
                 labels={"att_rate": "Attendance Rate (%)", "group_name": "Group",
                         "status_label": "Status"},
                 text=att_group["att_rate"].round(1).astype(str) + "%")
    fig.add_vline(x=platform_avg, line_dash="dash", line_color="navy",
                  annotation_text=f"Platform avg {platform_avg:.1f}%",
                  annotation_position="top right")
    fig.update_layout(xaxis_range=[0, 100], legend_title="Status",
                      yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(qlayout(fig, 500), use_container_width=True)

    below_groups = att_group[att_group["status_label"] == "Well Below Average (>10 pp)"]["group_name"].tolist()
    st.markdown(
        insight_box("💡", "INSIGHTS",
                    f"Platform average attendance is <b>{platform_avg:.1f}%</b>. "
                    f"Groups flagged in red — <b>{', '.join(below_groups) if below_groups else 'none'}</b> — "
                    "sit more than 10 percentage points below average, signalling a structural attendance "
                    "problem. These cohorts should be the first target for an academic intervention check."),
        unsafe_allow_html=True,
    )

    # ── Q2 ───────────────────────────────────────────────────────────────────
    st.markdown(sec("Q2 · Score Distribution by Assessment Type — Where Is Performance Most Volatile?"), unsafe_allow_html=True)

    ORDER = ["quiz", "assignment", "practical", "exam"]
    TYPE_COLORS = {"quiz": BLUE, "assignment": PURPLE, "practical": GREEN, "exam": RED}

    type_stats_ordered = type_stats[type_stats["type"].isin(ORDER)].copy()
    type_stats_ordered["type"] = pd.Categorical(type_stats_ordered["type"], categories=ORDER, ordered=True)
    type_stats_ordered = type_stats_ordered.sort_values("type")

    most_volatile = type_stats.loc[type_stats["std"].idxmax(), "type"] if len(type_stats) else "N/A"

    # Box-style summary using precomputed quartiles (median, q25, q75, std)
    fig = go.Figure()
    for _, row in type_stats_ordered.iterrows():
        fig.add_trace(go.Box(
            name=row["type"],
            q1=[row["q25"]], median=[row["median"]], q3=[row["q75"]],
            lowerfence=[max(0, row["q25"] - 1.5 * (row["q75"] - row["q25"]))],
            upperfence=[min(100, row["q75"] + 1.5 * (row["q75"] - row["q25"]))],
            marker_color=TYPE_COLORS.get(row["type"], BLUE),
            showlegend=False,
        ))
    fig.update_layout(title="Q2 — Score Distribution by Assessment Type",
                       yaxis_title="Score (%)", xaxis_title="Assessment Type")
    st.plotly_chart(qlayout(fig, 450), use_container_width=True)

    st.markdown(
        insight_box("💡", "INSIGHTS",
                    f"Most volatile assessment type: <b>{most_volatile}</b> (highest std deviation). "
                    "A wider IQR (taller box) means students in the same cohort end up with very different outcomes — "
                    "pointing to inconsistent preparation, question difficulty variance, or grading subjectivity. "
                    "Exams typically have the lowest median (highest pressure) while practicals reward hands-on learners."),
        unsafe_allow_html=True,
    )

    # ── Q3 ───────────────────────────────────────────────────────────────────
    st.markdown(sec("Q3 · Course Average Grade — Highest vs Lowest, How Does Spread Differ?"), unsafe_allow_html=True)

    course_stats_sorted = course_stats.sort_values("avg", ascending=False)

    fig = px.bar(course_stats_sorted, x="course_name", y="avg",
                 error_y="std", color="avg",
                 color_continuous_scale="RdYlGn",
                 text=course_stats_sorted["avg"].round(1).astype(str) + "%",
                 title="Q3 — Average Grade by Course (error bars = std dev)",
                 labels={"avg": "Average Grade (%)", "course_name": "Course"})
    fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30)
    fig.update_traces(textposition="outside")
    st.plotly_chart(qlayout(fig, 450), use_container_width=True)

    if len(course_stats_sorted) >= 2:
        top_course = course_stats_sorted.iloc[0]
        bot_course = course_stats_sorted.iloc[-1]
        st.markdown(
            insight_box("💡", "INSIGHTS",
                        f"Highest average: <b>{top_course['course_name']}</b> ({top_course['avg']:.1f}%). "
                        f"Lowest average: <b>{bot_course['course_name']}</b> ({bot_course['avg']:.1f}%). "
                        "A large gap signals curriculum-level difficulty mismatch — harder courses don't just "
                        "lower the mean, they widen the spread, meaning struggling students fall further behind."),
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 · Q4 Q5
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:

    # ── Q4 ───────────────────────────────────────────────────────────────────
    st.markdown(sec("Q4 · Attendance ↔ Average Grade — Quantify the Relationship"), unsafe_allow_html=True)

    if len(q4_df) > 5:
        r = q4_df["attendance_rate"].corr(q4_df["avg_grade_pct"])
        slope, intercept = np.polyfit(q4_df["attendance_rate"], q4_df["avg_grade_pct"], 1)

        fig = px.scatter(q4_df, x="attendance_rate", y="avg_grade_pct",
                         color="course_name", hover_data=["group_name"] if "group_name" in q4_df.columns else None,
                         title=f"Q4 — Attendance vs Average Grade  (r = {r:.3f})",
                         labels={"attendance_rate": "Attendance Rate (%)",
                                 "avg_grade_pct": "Average Grade (%)",
                                 "course_name": "Course"})
        xr = np.linspace(q4_df["attendance_rate"].min(), q4_df["attendance_rate"].max(), 100)
        fig.add_trace(go.Scatter(x=xr, y=slope * xr + intercept, mode="lines",
                                 line=dict(color="black", width=2, dash="dash"),
                                 name="OLS trend", showlegend=False))
        fig.update_traces(marker_size=5, opacity=0.7, selector=dict(mode="markers"))
        st.plotly_chart(qlayout(fig, 500), use_container_width=True)

        strength = "Strong" if abs(r) > 0.6 else ("Moderate" if abs(r) > 0.3 else "Weak")
        direction = "positive" if r > 0 else "negative"
        st.markdown(
            insight_box("💡", "INSIGHTS",
                        f"Pearson r = <b>{r:.3f}</b> — <b>{strength} {direction}</b> correlation. "
                        f"R² = <b>{r**2:.3f}</b>, meaning attendance explains <b>{r**2*100:.1f}%</b> of grade variance. "
                        "Students who show up more tend to score higher — but other factors (engagement, prior "
                        "knowledge) also drive performance. High-attendance / low-grade outliers deserve individual investigation."),
            unsafe_allow_html=True,
        )
    else:
        st.info("Not enough data for Q4.")

    # ── Q5 ───────────────────────────────────────────────────────────────────
    st.markdown(sec("Q5 · Engagement (Logins + Video) ↔ Academic Performance"), unsafe_allow_html=True)

    if len(q5_df) > 5:
        r_login = q5_df["login_count"].corr(q5_df["avg_grade_pct"])
        r_video = q5_df["video_watch_minutes"].corr(q5_df["avg_grade_pct"])

        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=[
                                f"Login Frequency vs Grade  (r={r_login:.3f})",
                                f"Video Watch Time vs Grade  (r={r_video:.3f})"])

        fig.add_trace(go.Scatter(x=q5_df["login_count"], y=q5_df["avg_grade_pct"],
                                 mode="markers", marker=dict(color=BLUE, size=5, opacity=0.6),
                                 showlegend=False), row=1, col=1)
        s1, i1 = np.polyfit(q5_df["login_count"], q5_df["avg_grade_pct"], 1)
        xr1 = np.linspace(q5_df["login_count"].min(), q5_df["login_count"].max(), 100)
        fig.add_trace(go.Scatter(x=xr1, y=s1 * xr1 + i1, mode="lines",
                                 line=dict(color="navy", dash="dash"), showlegend=False), row=1, col=1)

        fig.add_trace(go.Scatter(x=q5_df["video_watch_minutes"], y=q5_df["avg_grade_pct"],
                                 mode="markers", marker=dict(color=GREEN, size=5, opacity=0.6),
                                 showlegend=False), row=1, col=2)
        s2, i2 = np.polyfit(q5_df["video_watch_minutes"], q5_df["avg_grade_pct"], 1)
        xr2 = np.linspace(q5_df["video_watch_minutes"].min(), q5_df["video_watch_minutes"].max(), 100)
        fig.add_trace(go.Scatter(x=xr2, y=s2 * xr2 + i2, mode="lines",
                                 line=dict(color="darkgreen", dash="dash"), showlegend=False), row=1, col=2)

        fig.update_xaxes(title_text="Login Count", row=1, col=1)
        fig.update_xaxes(title_text="Video Watch (min)", row=1, col=2)
        fig.update_yaxes(title_text="Average Grade (%)", row=1, col=1)
        fig.update_yaxes(title_text="Average Grade (%)", row=1, col=2)
        fig.update_layout(title="Q5 — Engagement vs Academic Performance")
        st.plotly_chart(qlayout(fig, 450), use_container_width=True)

        stronger = "Login frequency" if abs(r_login) >= abs(r_video) else "Video watch time"
        st.markdown(
            insight_box("💡", "INSIGHTS",
                        f"Login r = <b>{r_login:.3f}</b> · Video r = <b>{r_video:.3f}</b>. "
                        f"<b>{stronger}</b> is the stronger predictor of academic performance. "
                        "If login frequency dominates, simply showing up on the platform predicts grades better "
                        "than passive content consumption. A weak correlation on both would suggest quality of "
                        "engagement (quiz attempts, forum participation) matters more than quantity."),
            unsafe_allow_html=True,
        )
    else:
        st.info("Not enough data for Q5.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 · Q6 Q7
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:

    # ── Q6 ───────────────────────────────────────────────────────────────────
    st.markdown(sec("Q6 · Concepts with Highest Failure Rate — Biggest Curriculum Weak Spot"), unsafe_allow_html=True)

    concept_fail_sorted = concept_fail.sort_values("failure_rate", ascending=False)
    top20 = concept_fail_sorted.head(20)

    fig = px.bar(top20, x="failure_rate", y="concept_name", orientation="h",
                 color="course_name",
                 title="Q6 — Top 20 Concepts by Failure Rate",
                 labels={"failure_rate": "Failure Rate (%)", "concept_name": "Concept",
                         "course_name": "Course"},
                 text=top20["failure_rate"].round(1).astype(str) + "%")
    fig.add_vline(x=50, line_dash="dot", line_color="red",
                  annotation_text="50% failure line", annotation_position="top right")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, legend_title="Course")
    st.plotly_chart(qlayout(fig, 600), use_container_width=True)

    if len(concept_fail_sorted) > 0:
        worst = concept_fail_sorted.iloc[0]
        st.markdown(
            insight_box("🔴", "BIGGEST WEAK SPOT",
                        f"Concept: <b>{worst['concept_name']}</b> — "
                        f"Course: <b>{worst['course_name']}</b> — "
                        f"Failure rate: <b>{worst['failure_rate']:.1f}%</b>. "
                        "Any concept above 50% failure means the majority of students who encountered it "
                        "failed to master it — this is a curriculum design signal, not just a student issue. "
                        "This is where redesign (clearer explanations, more exercises, prerequisite checks) should begin."),
            unsafe_allow_html=True,
        )

    # ── Q7 ───────────────────────────────────────────────────────────────────
    st.markdown(sec("Q7 · Weakest Concept Mastery Over Time — Improving, Flat, or Getting Worse?"), unsafe_allow_html=True)

    if len(concept_fail_sorted) > 0 and len(mastery_trend_raw) > 0:
        weakest_concept = concept_fail_sorted.iloc[0]["concept_name"]

        mastery_trend = (mastery_trend_raw
                         .groupby("assessment_no")["mastery_status"]
                         .apply(lambda x: (x == "passed").sum() / len(x) * 100)
                         .reset_index(name="pass_rate")
                         .sort_values("assessment_no"))

        trend_label = "N/A"
        if len(mastery_trend) > 1:
            slope_m, _ = np.polyfit(mastery_trend["assessment_no"], mastery_trend["pass_rate"], 1)
            trend_label = "IMPROVING ↑" if slope_m > 1 else ("DECLINING ↓" if slope_m < -1 else "FLAT →")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=mastery_trend["assessment_no"], y=mastery_trend["pass_rate"],
            mode="lines+markers",
            line=dict(color=RED, width=3),
            marker=dict(size=10), name="Pass rate"))
        fig.add_hrect(y0=0, y1=50, fillcolor="red", opacity=0.07, line_width=0,
                      annotation_text="Majority failing zone", annotation_position="bottom right")
        if len(mastery_trend) > 1:
            s, i = np.polyfit(mastery_trend["assessment_no"], mastery_trend["pass_rate"], 1)
            xr = np.array([mastery_trend["assessment_no"].min(), mastery_trend["assessment_no"].max()])
            fig.add_trace(go.Scatter(x=xr, y=s * xr + i, mode="lines",
                                     line=dict(color="gray", dash="dash"), name="Trend"))
        fig.update_layout(
            title=f"Q7 — Mastery Trend: '{weakest_concept}'  ({trend_label})",
            xaxis_title="Assessment Number (chronological)",
            yaxis_title="Cohort Pass Rate (%)", yaxis_range=[0, 100])
        st.plotly_chart(qlayout(fig, 430), use_container_width=True)

        st.markdown(
            insight_box("💡", "INSIGHTS",
                        f"Trend for '<b>{weakest_concept}</b>': <b>{trend_label}</b>. "
                        "A declining trend means repeated exposure is not helping — the teaching approach "
                        "needs to change. A flat low pass rate means students hit a ceiling they can't break "
                        "(likely a prerequisite gap). An improving trend means instructor interventions are "
                        "having a delayed but real effect."),
            unsafe_allow_html=True,
        )
    else:
        st.info("No concept mastery trend data available.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 · Q8 Q9 Q10
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:

    # ── Q8 ───────────────────────────────────────────────────────────────────
    st.markdown(sec("Q8 · Late Submissions ↔ Lower Scores? Show the Effect"), unsafe_allow_html=True)

    if len(sub_grade) > 10:
        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=["Late vs On-Time Score Distribution",
                                            "Submission Buffer vs Score (hours before deadline)"])
        for label, color in [("On Time", GREEN), ("Late", RED)]:
            subset = sub_grade[sub_grade["is_late_label"] == label]
            fig.add_trace(go.Box(y=subset["pct"], name=label,
                                 marker_color=color, boxmean=True), row=1, col=1)
        ontime = sub_grade[sub_grade["buffer_hours"] > 0]
        fig.add_trace(go.Scatter(x=ontime["buffer_hours"], y=ontime["pct"],
                                 mode="markers", marker=dict(color=BLUE, size=4, opacity=0.5),
                                 name="On-time subs", showlegend=False), row=1, col=2)
        if len(ontime) > 5:
            s3, i3 = np.polyfit(ontime["buffer_hours"], ontime["pct"], 1)
            xr3 = np.linspace(0, ontime["buffer_hours"].quantile(0.95), 100)
            fig.add_trace(go.Scatter(x=xr3, y=s3 * xr3 + i3, mode="lines",
                                     line=dict(color="navy", dash="dash"),
                                     showlegend=False), row=1, col=2)
        fig.update_xaxes(title_text="Hours Before Deadline", row=1, col=2)
        fig.update_yaxes(title_text="Score (%)", row=1, col=1)
        fig.update_yaxes(title_text="Score (%)", row=1, col=2)
        fig.update_layout(title="Q8 — Late Submission Effect on Score")
        st.plotly_chart(qlayout(fig, 450), use_container_width=True)

        late_avg   = sub_grade[sub_grade["is_late"] == True]["pct"].mean()
        ontime_avg = sub_grade[sub_grade["is_late"] == False]["pct"].mean()
        gap = ontime_avg - late_avg if not np.isnan(late_avg) else 0
        st.markdown(
            insight_box("💡", "INSIGHTS",
                        f"On-time avg: <b>{ontime_avg:.1f}%</b> · Late avg: <b>{late_avg:.1f}%</b> · "
                        f"Gap: <b>{gap:.1f} pp</b>. "
                        "Causality can go both ways: weak students may submit late because they struggle, "
                        "OR submitting late (less preparation time) directly causes lower scores. "
                        "Students who submit very last-minute (buffer ≈ 0) also score low, "
                        "suggesting timing itself is a driver."),
            unsafe_allow_html=True,
        )
    else:
        st.info("Not enough submission data.")

    # ── Q9 ───────────────────────────────────────────────────────────────────
    st.markdown(sec("Q9 · Attendance & Engagement Over 6-Month Term — Where Does the Cohort Dip?"), unsafe_allow_html=True)

    if len(combined) > 0:
        # Fix: convert month to datetime before sorting to handle any string format safely
        combined["month_sort"] = pd.to_datetime(combined["month"], errors="coerce")
        combined_sorted = combined.sort_values("month_sort").drop(columns="month_sort")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=combined_sorted["month"], y=combined_sorted["att_rate"],
                                 mode="lines+markers", name="Attendance Rate (%)",
                                 line=dict(color=RED, width=3), marker=dict(size=8)),
                      secondary_y=False)
        fig.add_trace(go.Bar(x=combined_sorted["month"], y=combined_sorted["event_count"],
                             name="Platform Events", opacity=0.5, marker_color=BLUE),
                      secondary_y=True)

        dip_idx = combined_sorted["att_rate"].idxmin()
        dip_month = combined_sorted.loc[dip_idx, "month"]
        dip_att   = combined_sorted.loc[dip_idx, "att_rate"]
        fig.add_annotation(x=dip_month, y=dip_att,
                           text=f"⚠ Dip: {dip_att:.1f}%",
                           showarrow=True, arrowhead=2, arrowcolor="red",
                           font=dict(color="red", size=13))
        fig.update_yaxes(title_text="Attendance Rate (%)", secondary_y=False)
        fig.update_yaxes(title_text="Platform Event Count", secondary_y=True)
        fig.update_layout(title="Q9 — Attendance & Engagement Over 6-Month Term",
                          xaxis_title="Month", legend=dict(x=0.01, y=0.99))
        st.plotly_chart(qlayout(fig, 450), use_container_width=True)

        st.markdown(
            insight_box("💡", "INSIGHTS",
                        f"Lowest attendance month: <b>{dip_month}</b> ({dip_att:.1f}%). "
                        "A simultaneous dip in both attendance AND engagement in the same month rules out "
                        "individual student factors and points to a cohort-wide event. "
                        "Possible explanations: exam period at partner universities, a national holiday cluster, "
                        "an instructor absence, or a platform outage. Kayfa academic leads should cross-reference "
                        "this dip with their academic calendar."),
            unsafe_allow_html=True,
        )
    else:
        st.info("Not enough monthly data.")

    # ── Q10 ──────────────────────────────────────────────────────────────────
    st.markdown(sec("Q10 · Age Bands vs Outcomes — Does Age Relate to Performance?"), unsafe_allow_html=True)

    if len(age_stats) > 0:
        age_long = age_stats.melt(
            id_vars="age_band",
            value_vars=["avg_grade", "avg_attendance", "avg_logins"],
            var_name="metric", value_name="value")
        age_long["metric"] = age_long["metric"].map({
            "avg_grade"     : "Avg Grade (%)",
            "avg_attendance": "Avg Attendance (%)",
            "avg_logins"    : "Avg Logins"})

        fig = px.bar(age_long, x="age_band", y="value", color="metric",
                     barmode="group",
                     title="Q10 — Outcomes by Age Band",
                     labels={"age_band": "Age Band", "value": "Score / Rate", "metric": "Metric"},
                     color_discrete_sequence=[BLUE, RED, GREEN])
        for _, row in age_stats.iterrows():
            fig.add_annotation(x=row["age_band"], y=2,
                               text=f"n={int(row['count'])}", showarrow=False,
                               font=dict(size=10, color="gray"))
        fig.update_layout(xaxis_title="Age Band")
        st.plotly_chart(qlayout(fig, 450), use_container_width=True)

        st.markdown(
            insight_box("💡", "INSIGHTS",
                        "Mature learners (31+) often show higher attendance (more professional discipline) "
                        "but may have more variable grades if technical content requires background they lack. "
                        "The 21–25 band typically dominates platform engagement (more digital-native behaviour). "
                        "If outcomes are roughly flat across age bands, Kayfa's design works well for adult learners "
                        "of all ages. If a specific band underperforms, investigate whether course pacing or support "
                        "resources meet that group's needs."),
            unsafe_allow_html=True,
        )
    else:
        st.info("No age band data available.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 · Q11 Q12 Q13
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:

    # ── Q11 ──────────────────────────────────────────────────────────────────
    st.markdown(sec("Q11 · Student Segmentation — Behavioural Clusters"), unsafe_allow_html=True)

    CLUSTER_COLORS = {
        "High Achievers"          : GREEN,
        "Moderate Performers"     : BLUE,
        "Present but Struggling"  : ORANGE,
        "Disengaged At-Risk"      : RED,
    }

    if len(clusters_df) > 0:
        fig = px.scatter(clusters_df, x="attendance_rate", y="avg_grade_pct",
                         color="cluster_label", color_discrete_map=CLUSTER_COLORS,
                         size="login_count", size_max=15,
                         hover_data=["full_name", "course_name", "failed_concepts"],
                         title="Q11 — Student Segmentation (size = login count)",
                         labels={"attendance_rate": "Attendance Rate (%)",
                                 "avg_grade_pct": "Average Grade (%)",
                                 "cluster_label": "Segment"})
        fig.add_hline(y=60, line_dash="dot", line_color="gray", opacity=0.5)
        fig.add_vline(x=60, line_dash="dot", line_color="gray", opacity=0.5)
        fig.update_traces(marker_opacity=0.75)
        fig.update_layout(legend_title="Student Segment")
        st.plotly_chart(qlayout(fig, 520), use_container_width=True)

        # Segment summary table
        profile = clusters_df.groupby("cluster_label").agg(
            att_rate  = ("attendance_rate", "mean"),
            logins    = ("login_count", "mean"),
            avg_grade = ("avg_grade_pct", "mean"),
            failed_c  = ("failed_concepts", "mean"),
            n         = ("student_id", "count")
        ).round(2).reset_index()

        summary_rows = []
        for _, row in profile.iterrows():
            summary_rows.append({
                "Segment": row["cluster_label"], "# Students": int(row["n"]),
                "Avg Attendance (%)": f"{row['att_rate']:.1f}",
                "Avg Logins": f"{row['logins']:.1f}",
                "Avg Grade (%)": f"{row['avg_grade']:.1f}",
                "Avg Failed Concepts": f"{row['failed_c']:.1f}",
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        st.markdown(
            insight_box("💡", "INSIGHTS",
                        "<b>High Achievers</b> — reinforce and challenge further; they are on track. "
                        "<b>Moderate Performers</b> — low-hanging fruit; a small push in engagement or attendance "
                        "could move many into the top tier. "
                        "<b>Present but Struggling</b> — coming to class but not learning; need academic support "
                        "(tutoring, concept review sessions, peer study groups). "
                        "<b>Disengaged At-Risk</b> — most urgent; low on all dimensions; direct outreach needed."),
            unsafe_allow_html=True,
        )
    else:
        st.info("No cluster data available.")

    # ── Q12 ──────────────────────────────────────────────────────────────────
    st.markdown(sec("Q12 · True Group Sizes vs Self-Reported Counts — Visualise Discrepancies"), unsafe_allow_html=True)

    if len(q12_df) > 0:
        q12 = q12_df.copy()
        q12["true_count"] = q12["true_count"].fillna(0).astype(int)
        q12["discrepancy"] = q12["true_count"] - q12["stated_num_students"]
        q12["flag"] = q12["discrepancy"].abs() > 3
        q12_sorted = q12.sort_values("true_count", ascending=False)

        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=["True vs Stated Group Size",
                                            "Discrepancy (True − Stated)"])
        fig.add_trace(go.Bar(x=q12_sorted["group_name"], y=q12_sorted["true_count"],
                             name="True count", marker_color=GREEN), row=1, col=1)
        fig.add_trace(go.Bar(x=q12_sorted["group_name"], y=q12_sorted["stated_num_students"],
                             name="Stated count", marker_color="#bdc3c7"), row=1, col=1)
        disc_colors = [RED if d < 0 else BLUE for d in q12_sorted["discrepancy"]]
        fig.add_trace(go.Bar(x=q12_sorted["group_name"], y=q12_sorted["discrepancy"],
                             marker_color=disc_colors, name="Discrepancy", showlegend=False), row=1, col=2)
        fig.add_hline(y=0, line_color="black", line_width=1, row=1, col=2)
        fig.update_layout(barmode="group",
                          title="Q12 — Group Headcount: True vs Self-Reported",
                          legend=dict(x=0.01, y=0.99))
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(qlayout(fig, 450), use_container_width=True)

        flagged = q12[q12["flag"]]["group_name"].tolist()
        st.markdown(
            insight_box("💡", "INSIGHTS",
                        f"Groups flagged (discrepancy > ±3 students): <b>{', '.join(flagged) if flagged else 'none'}</b>. "
                        "Groups with a large negative discrepancy (true < stated) were over-reported at registration — "
                        "students enrolled but didn't persist, inflating visible metrics. "
                        "Groups with a large positive discrepancy may have absorbed students from dissolved groups "
                        "and are now oversized, affecting instructor-to-student ratios."),
            unsafe_allow_html=True,
        )
    else:
        st.info("No group-size data available.")

    # ── Q13 ──────────────────────────────────────────────────────────────────
    st.markdown(sec("Q13 · Non-Viable Group — Identify, Find Closest Match, Recommend Merge"), unsafe_allow_html=True)

    if len(q13_df) > 0:
        q13 = q13_df.iloc[0]

        col_info_a, col_info_b = st.columns(2)
        with col_info_a:
            st.metric("Smallest Group", q13.get("smallest_group_name", "—"))
            st.metric("True Count", int(q13.get("true_count", 0)))
        with col_info_b:
            st.metric("Best Match for Merge", q13.get("best_match_name", "—"))
            sim_val = float(q13.get("similarity_score") or 0)
            st.metric("Concept-Profile Similarity", f"{sim_val:.3f}")
        




        # Q13 Profile Comparison Chart
        if len(q13_profile) > 0:

            fig = go.Figure()

            fig.add_trace(go.Bar(
                name=q13.get("smallest_group_name", "Small Group"),
                x=q13_profile["concept"],
                y=q13_profile["small_group_score"]
            ))

            fig.add_trace(go.Bar(
                name=q13.get("best_match_name", "Best Match"),
                x=q13_profile["concept"],
                y=q13_profile["best_match_score"]
            ))

            fig.update_layout(
                barmode="group",
                title="Q13 — Profile Comparison",
                xaxis_title="Concept",
                yaxis_title="Average Score (%)",
                height=450
            )

            st.plotly_chart(fig, use_container_width=True)
                




        # Optional: closest student pair, if present in the document
        if "closest_student_a" in q13 and "closest_student_b" in q13:
            st.markdown(
                insight_box("👥", "CLOSEST STUDENT PAIR",
                            f"<b>{q13['closest_student_a']}</b> (in {q13.get('smallest_group_name','')}) "
                            f"↔ <b>{q13['closest_student_b']}</b> (in {q13.get('best_match_name','')}) — "
                            f"these two students have the most similar concept-mastery profile, "
                            "supporting a smooth merge between the two groups."),
                unsafe_allow_html=True,
            )

        st.markdown(
            insight_box("✅", "RECOMMENDATION",
                        f"<b>{q13.get('smallest_group_name','This group')}</b> has only "
                        f"<b>{int(q13.get('true_count', 0))}</b> students — "
                        "not operationally viable for meaningful group discussions or peer learning. "
                        f"Merging into <b>{q13.get('best_match_name','the best-match group')}</b> "
                        f"(concept-profile similarity = {float(q13.get('similarity_score') or 0):.3f}) minimises academic "
                        "disruption: students will encounter familiar concepts at similar mastery levels. "
                        "<b>Recommended action:</b> Close the small group at end of current month, "
                        "move its students into the best-match group, and notify both instructors for onboarding support."),
            unsafe_allow_html=True,
        )
    else:
        st.info("No non-viable-group data available.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 · Q14 Q15
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[5]:

    # ── Q14 ──────────────────────────────────────────────────────────────────
    st.markdown(sec("Q14 · At-Risk Ranking — Top 10 Students to Contact First"), unsafe_allow_html=True)

    if len(top10) > 0:
        top10_sorted = top10.sort_values("at_risk_score", ascending=False).reset_index(drop=True)
        top10_sorted.index = top10_sorted.index + 1

        fig = px.bar(top10_sorted, x="at_risk_score", y="full_name", orientation="h",
                     color="at_risk_score", color_continuous_scale="Reds",
                     hover_data=["course_name", "attendance_rate", "avg_grade_pct", "failed_concepts"],
                     title="Q14 — Top 10 At-Risk Students (composite score)",
                     labels={"at_risk_score": "At-Risk Score (0–1)", "full_name": "Student"})
        fig.update_layout(coloraxis_showscale=False, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(text=top10_sorted["at_risk_score"].round(3).astype(str), textposition="outside")
        st.plotly_chart(qlayout(fig, 430), use_container_width=True)

        rename_map = {
            "full_name": "Student", "course_name": "Course", "group_name": "Group",
            "attendance_rate": "Attendance (%)", "avg_grade_pct": "Avg Grade (%)",
            "failed_concepts": "Failed Concepts", "at_risk_score": "At-Risk Score"
        }
        display_top10 = top10_sorted.rename(columns=rename_map)
        display_cols = ["Student", "Course", "Attendance (%)", "Avg Grade (%)", "Failed Concepts", "At-Risk Score"]
        if "Group" in display_top10.columns:
            display_cols.insert(2, "Group")
        st.dataframe(display_top10[display_cols].round(2), use_container_width=True)

        st.markdown(
            insight_box("🚨", "ACTION REQUIRED",
                        "The composite at-risk score combines four independent signals — no student makes this list "
                        "by failing on just one dimension. A student at the top is simultaneously absent, disengaged, "
                        "underperforming, AND declining over time. "
                        "Instructors should contact these 10 students before end of Month 1, with the message "
                        "tailored to their dominant risk factor: "
                        "<b>High fail_risk</b> → offer concept review or tutoring · "
                        "<b>High att_risk</b> → investigate barriers to attendance · "
                        "<b>High decline</b> → check for external stressors or platform access issues."),
            unsafe_allow_html=True,
        )
    else:
        st.info("No at-risk data available.")

    # ── Q15 ──────────────────────────────────────────────────────────────────
    st.markdown(sec("Q15 · Group Grade Trends — Who's Trending Up, Who's Sliding Down?"), unsafe_allow_html=True)

    if len(trend_df) > 0:
        trend_sorted = trend_df.sort_values("slope", ascending=False)

        trend_colors = trend_sorted["trend"].map({
            "Trending Up ↑": GREEN,
            "Sliding Down ↓": RED,
            "Stable →": "#95a5a6"
        }).fillna("#95a5a6")

        fig = px.bar(trend_sorted, x="slope", y="group_name", orientation="h",
                     color="trend",
                     color_discrete_map={"Trending Up ↑": GREEN, "Sliding Down ↓": RED, "Stable →": "#95a5a6"},
                     title="Q15 — Group Grade Trend Slope (pp per assessment)",
                     labels={"slope": "Slope (pp / assessment)", "group_name": "Group", "trend": "Trend"})
        fig.add_vline(x=0, line_color="black", line_width=1)
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(qlayout(fig, 480), use_container_width=True)

        # Q15 Line Chart — Grade lines per group over assessments
        if len(grade_trend_raw) > 0:
            trend_color_map_app = trend_sorted.set_index("group_name")["trend"].map({
                "Trending Up ↑": GREEN, "Sliding Down ↓": RED, "Stable →": "#95a5a6"
            }).to_dict()

            fig2 = go.Figure()
            for grp in grade_trend_raw["group_name"].unique():
                gdata = grade_trend_raw[grade_trend_raw["group_name"] == grp].sort_values("assess_no")
                color = trend_color_map_app.get(grp, "#95a5a6")
                trend_lbl_arr = trend_sorted[trend_sorted["group_name"] == grp]["trend"].values
                trend_lbl = trend_lbl_arr[0] if len(trend_lbl_arr) else ""
                fig2.add_trace(go.Scatter(
                    x=gdata["assess_no"], y=gdata["avg_pct"],
                    mode="lines+markers", name=f"{grp} {trend_lbl}",
                    line=dict(color=color, width=2.5), marker=dict(size=6), opacity=0.85))
            fig2.add_hline(y=60, line_dash="dot", line_color="gray", opacity=0.5,
                           annotation_text="60% pass line", annotation_position="bottom right")
            fig2.update_layout(title="Q15 — Group Grade Lines Over Assessments",
                               xaxis_title="Assessment Number", yaxis_title="Avg Grade (%)",
                               yaxis_range=[0, 100], legend=dict(x=1.01, y=1))
            st.plotly_chart(qlayout(fig2, 540), use_container_width=True)

        up_groups   = trend_sorted[trend_sorted["trend"] == "Trending Up ↑"]["group_name"].tolist()
        down_groups = trend_sorted[trend_sorted["trend"] == "Sliding Down ↓"]["group_name"].tolist()
        st.markdown(
            insight_box("💡", "INSIGHTS",
                        f"<b>Trending Up ↑</b>: {', '.join(up_groups) if up_groups else 'none'} — "
                        "these groups suggest effective teaching and improving mastery; study as internal best-practice examples. "
                        f"<b>Sliding Down ↓</b>: {', '.join(down_groups) if down_groups else 'none'} — "
                        "deteriorating groups need urgent attention: course material may be getting progressively "
                        "harder without adequate support, or cumulative knowledge gaps are widening. "
                        "Kayfa should share these trend lines with instructors monthly so interventions happen in real time."),
            unsafe_allow_html=True,
        )
    else:
        st.info("No group trend data available.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("All analytics precomputed and served from MongoDB Atlas · Kayfa AI & Data Analytics Internship · Week 2")