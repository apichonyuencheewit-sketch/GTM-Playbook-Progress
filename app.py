import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Auto-refresh the screen every 10 seconds for real-time monitoring
st_autorefresh(interval=10000, key="datarefresh")

st.title("📋 Live Task Progress Monitoring")
st.subheader("Real-time project tracking for leadership review")

# PASTE YOUR GOOGLE SHEET CSV LINK HERE
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRRNZW0MtJj3COI8JqrcGgqTqIry8PaiIUHj7HRYYvAZ9Z8l35fNdYVqeXoia11AvdDabdOC0nwlDNO/pub?gid=0&single=true&output=csv"

try:
    # Clear cache and read the live cloud CSV data
    df = pd.read_csv(sheet_url)
    
    # Clean up string formatting
    df['Status'] = df['Status'].astype(str).str.strip()
    
    # FIX: Clean the Progress column so it turns text like "65%" or "65" into a pure number 65
    if 'Progress' in df.columns:
        df['Progress'] = df['Progress'].astype(str).str.replace('%', '', regex=False)
        df['Progress'] = pd.to_numeric(df['Progress'], errors='coerce').fillna(0)
    else:
        df['Progress'] = 0

    # Calculate overall project metrics
    total_tasks = len(df)
    completed_tasks = len(df[df['Status'] == 'Completed'])
    
    # Calculate overall progress by averaging the column directly (e.g. Average of 100, 50, 0 is 50%)
    overall_progress_pct = int(df['Progress'].mean()) if total_tasks > 0 else 0
    # Ensure it stays within bounds for the top progress bar component
    top_bar_val = max(0, min(100, overall_progress_pct)) / 100.0

    # Display status tiles at the top
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Tasks", value=total_tasks)
    col2.metric(label="Completed", value=completed_tasks, delta=f"+{completed_tasks} Done")
    col3.metric(label="Remaining", value=total_tasks - completed_tasks)

    # Display horizontal overall project completion bar
    st.write("### Overall Project Completion")
    st.progress(top_bar_val)
    st.write(f"📊 **{overall_progress_pct}%** of total project effort completed.")

    # Convert to 0.0 - 1.0 format ONLY at the final visual layer for Streamlit's ProgressColumn
    df_visual = df.copy()
    df_visual['Progress'] = df_visual['Progress'] / 100.0

    # Display detailed table view with INDIVIDUAL PROGRESS BARS
    st.write("### Detailed Task Breakdown")
    st.dataframe(
        df_visual, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Progress": st.column_config.ProgressColumn(
                "Task Progress",
                help="The completion percentage of this specific task",
                format="%.0f%%",
                min_value=0.0,
                max_value=1.0,
            )
        }
    )

except Exception as e:
    st.error("Connecting to live feed... Check your Google Sheets 'Publish to Web' setup if this takes too long.")
