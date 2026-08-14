import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 10 seconds
st_autorefresh(interval=10000, key="datarefresh")

st.title("📋 Live Task Progress Monitoring")
st.subheader("Real-time project tracking for leadership review")

# Google Sheet CSV
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRNZW0MtJj3COI8JqrcGgqTqIry8PaiIUHj7HRYYvAZ9Z8l35fNdYVqeXoia11AvdDabdOC0nwlDNO/pub?gid=0&single=true&output=csv"

try:
    # Read Google Sheet
    df = pd.read_csv(sheet_url)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Normalize column names
    df.rename(columns={
        "progress": "Progress",
        "PROGRESS": "Progress",
        "status": "Status",
        "STATUS": "Status"
    }, inplace=True)

    # Clean Status
    if "Status" in df.columns:
        df["Status"] = df["Status"].astype(str).str.strip()

    # ==========================================================
    # PROGRESS CONVERSION
    # ==========================================================

    if "Progress" in df.columns:

        # Convert everything to string first
        df["Progress"] = df["Progress"].astype(str).str.strip()

        # Remove %
        df["Progress"] = df["Progress"].str.replace(
            "%", "", regex=False
        )

        # Convert to numeric
        df["Progress"] = pd.to_numeric(
            df["Progress"],
            errors="coerce"
        ).fillna(0)

        # IMPORTANT:
        # Google Sheet values such as:
        # 100 -> 1.00
        # 38  -> 0.38
        # 75  -> 0.75

        df["Progress"] = df["Progress"] / 100

        # Safety: keep between 0 and 1
        df["Progress"] = df["Progress"].clip(0, 1)

    else:
        df["Progress"] = 0.0

    # ==========================================================
    # METRICS
    # ==========================================================

    total_tasks = len(df)

    completed_tasks = len(
        df[df["Status"].str.lower() == "completed"]
    )

    avg_progress = (
        df["Progress"].mean()
        if total_tasks > 0
        else 0.0
    )

    overall_progress_pct = round(avg_progress * 100)

    # ==========================================================
    # SUMMARY
    # ==========================================================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Tasks",
        total_tasks
    )

    col2.metric(
        "Completed",
        completed_tasks,
        delta=f"+{completed_tasks} Done"
    )

    col3.metric(
        "Remaining",
        total_tasks - completed_tasks
    )

    # ==========================================================
    # OVERALL PROGRESS
    # ==========================================================

    st.write("### Overall Project Completion")

    st.progress(avg_progress)

    st.write(
        f"📊 **{overall_progress_pct}%** "
        "of total project effort completed."
    )

    # ==========================================================
    # TASK TABLE
    # ==========================================================

    st.write("### Detailed Task Breakdown")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,

        column_config={
            "Progress": st.column_config.ProgressColumn(
                "Task Progress",
                help="Completion percentage of this task",

                # IMPORTANT
                format="%.0f%%",

                min_value=0,
                max_value=1,
            )
        }
    )

except Exception as e:

    st.error(
        "Unable to connect to Google Sheets."
    )

    st.exception(e)
