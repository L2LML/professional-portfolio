"""05_Lessons_Learned.py — Closeout summary + lessons learned per project."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from data.load_data import load_projects, load_final_summary, load_lessons_learned
from data.colors import PROJECT_ORDER, PROJECT_SHORT_NAMES

st.set_page_config(page_title="Lessons Learned — DTW PM Dashboard", page_icon="📚", layout="wide")
st.title("📚 Lessons Learned & Closeout")
st.caption("Final summary vs. baseline and lessons learned — sourced from each project's Closeout Report.")

projects = load_projects()
final_summary = load_final_summary()
lessons = load_lessons_learned()

sel = st.sidebar.multiselect(
    "Project", PROJECT_ORDER, default=PROJECT_ORDER,
    format_func=lambda p: PROJECT_SHORT_NAMES.get(p, p),
)
if not sel:
    st.info("Select at least one project in the sidebar.")
    st.stop()

SECTION_ICON = {
    "Went Well": "✅",
    "Could Improve": "🛠️",
    "Recommendations": "💡",
    "Outstanding / Transition": "➡️",
}
SECTION_ORDER = ["Went Well", "Could Improve", "Recommendations", "Outstanding / Transition"]

tabs = st.tabs([PROJECT_SHORT_NAMES.get(p, p) for p in sel])
for tab, project_id in zip(tabs, sel):
    with tab:
        proj_row = projects[projects["project_id"] == project_id].iloc[0]
        fs = final_summary[final_summary["project_id"] == project_id]
        proj_lessons = lessons[lessons["project_id"] == project_id]

        st.markdown(
            f"**{proj_row['project_name']}** · closed out at Month {proj_row['duration_months']} "
            f"(project management artifacts for this dashboard capture a Month {proj_row['current_month']} status-report snapshot "
            "plus this final closeout)."
        )

        st.subheader("Final Summary vs. Baseline")
        st.dataframe(
            fs.rename(columns={
                "dimension": "Dimension", "baseline": "Baseline", "final": "Final (Actual)", "variance": "Variance",
            })[["Dimension", "Baseline", "Final (Actual)", "Variance"]],
            width="stretch", hide_index=True,
        )

        st.divider()
        st.subheader("Lessons Learned")

        col_a, col_b = st.columns(2)
        cols = {"Went Well": col_a, "Could Improve": col_b, "Recommendations": col_a, "Outstanding / Transition": col_b}
        for section in SECTION_ORDER:
            items = proj_lessons[proj_lessons["section"] == section].sort_values("order")["text"].tolist()
            with cols[section]:
                st.markdown(f"**{SECTION_ICON[section]} {section}**")
                for item in items:
                    st.markdown(f"- {item}")
                st.markdown("")
