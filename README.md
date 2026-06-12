<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Syne&weight=800&size=36&pause=1000&color=6366f1&center=true&vCenter=true&width=600&lines=Kayfa+Student+Analytics+🎓;Data+Wrangling+%26+Storytelling;MongoDB+Atlas+Integrated)](https://git.io/typing-svg)

[![Python](https://img.shields.io/badge/Python-3.10-6366f1?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0c10)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.0-6366f1?style=for-the-badge&logo=pandas&logoColor=white&labelColor=0a0c10)](https://pandas.pydata.org)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-6366f1?style=for-the-badge&logo=plotly&logoColor=white&labelColor=0a0c10)](https://plotly.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live-6366f1?style=for-the-badge&logo=streamlit&logoColor=white&labelColor=0a0c10)](https://streamlit.io)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-6366f1?style=for-the-badge&logo=mongodb&logoColor=white&labelColor=0a0c10)](https://mongodb.com)

> **8 files. 3 formats. 37 data defects. One interactive story to uncover.**

| 🎓 Total Students | 📉 Avg Attendance | 🏆 Avg Grade | 🔍 Analysis Questions |
|:-----------------:|:-----------------:|:-------------:|:---------------------:|
| **~500** | **~75%** | **~68%** | **15** |

**[🚀 Try the Live Dashboard →](https://your-app-link.streamlit.app/)**

</div>

## ✦ Dashboard Preview

### 📊 Executive Overview & KPIs
<p align="center">
  <img src="images/1.png" width="95%" alt="Dashboard Overview">
</p>

### 🎯 Student Segmentation & Risk Analysis
<p align="center">
  <img src="images/2.png" width="95%" alt="Risk Analysis">
</p>

---

## ✦ What is This?

An end-to-end data analytics project built for the **Kayfa AI & Data Analytics Internship · Week 2 Evaluation**.

> *"How do our students learn — and who is at risk of falling behind?"*

This project tackles a complex, messy dataset spread across **CSVs, JSON, and Multi-sheet Excel workbooks**. It involves rigorous data cleaning (fixing 37 planted defects), multi-source joins, and advanced analytics including **K-Means Clustering** and **At-Risk Scoring**, all served via a high-performance **MongoDB Atlas** backend.

---

## ✦ Project Structure

```
kayfa-student-analytics/
├── 📓 student_analytics_cleaning.ipynb     ← Data Cleaning & Quality Audit (37 Issues)
├── 📓 student_analytics_questions.ipynb    ← The 15 Questions Analysis & MongoDB Upload
├── 🎛️ app.py                              ← Streamlit Dashboard (6 Tabs)
├── 📋 requirements.txt                    ← Dependencies
├── 🖼️ images/                             ← Dashboard screenshots
└── 📊 data/                               ← Raw dataset (8 files)
```

---

## ✦ The Pipeline

| # | Phase                  | What Happens |
|---|------------------------|-------------|
| 1 | **Load & Reconcile**   | Extract 8 files from 3 formats; flatten nested JSON; unify 6 Excel sheets. |
| 2 | **Cleaning Rigour**    | Fix **37 planted defects**: duplicates, impossible ages, broken logic, messy status encodings. |
| 3 | **Multi-source Joins** | Merge Students, Groups, Courses, Grades, and Engagement into unified model. |
| 4 | **Precomputed Analytics** | Calculate heavy metrics (clustering, trends) and push to **MongoDB Atlas**. |
| 5 | **Interactive Dashboard** | Multi-page Streamlit app with KPIs, Plotly visuals, and action plans. |

---

## ✦ The 15 Academic Questions

| #     | Question                                      | Difficulty    |
|-------|-----------------------------------------------|---------------|
| Q1-Q3 | Attendance per group & Course-level performance | 🟢 Medium    |
| Q4-Q5 | Attendance/Engagement ↔ Grade correlations     | 🟡 Hard      |
| Q6-Q7 | Curriculum weak spots & Concept mastery        | 🟡 Hard      |
| Q8-Q10| Procrastination effect, Cohort dips & Age      | 🟡 Hard      |
| Q11   | **Student Segmentation:** High-achievers vs At-Risk | 🔴 Very Hard |
| Q12-Q13| Headcount discrepancies & Group viability     | 🔴 Very Hard |
| Q14   | **At-Risk Ranking:** Top 10 students          | 🔴 Very Hard |
| Q15   | **Group Grade Trends:** Trending up vs down   | 🔴 Very Hard |

---

## ✦ Key Findings & Action Plan

| # | Finding | Recommended Action |
|---|--------|-------------------|
| 1 | Strong **Attendance ↔ Grade** correlation | Early intervention below 60% attendance |
| 2 | **Login Frequency** > Video watch time | Gamify daily logins |
| 3 | Concept weak spots in specific modules | Redesign weakest concepts |
| 4 | **Disengaged At-Risk** segment via K-Means | Automated check-in emails |
| 5 | Non-viable groups (< 5 students) | Merge with closest-profile groups |

---

## ✦ Dashboard Features

- **Sidebar Filters** — Course, Group, Demographics  
- **Live KPIs** — Headcount, Avg Attendance, Avg Grade, At-Risk Count  
- **6 Interactive Tabs**: Headlines, Drivers, Curriculum, Behaviour, Segments, Intervention

---

## ✦ Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Language    | Python 3.10                         |
| Analysis    | Pandas · NumPy · Scipy              |
| ML          | Scikit-Learn (K-Means)              |
| Charts      | Plotly                              |
| Database    | MongoDB Atlas                       |
| Dashboard   | Streamlit                           |

---

## ✦ Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. Create `.env` file with your `MONGO_URI`

3. **Run the Dashboard**
   ```bash
   streamlit run app.py
   ```

<div align="center">
Built with ⚡ for Kayfa AI & Data Analytics Internship · Week 2<br>
Synthetic dataset — patterns are realistic but not real-world data.
</div>
