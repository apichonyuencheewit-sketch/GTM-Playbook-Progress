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
    # Read the live cloud CSV data
    df = pd.read_csv(sheet_url)
    
    # Clean up status text spacing
    df['Status'] = df['Status'].astype(str).str.strip()
    
    if 'Progress' in df.columns:
        # 1. Strip out text formatting symbols like "%" safely
        df['Progress'] = df['Progress'].astype(str).str.replace('%', '', regex=False)
        # 2. Turn them into raw floating numbers
        df['Progress'] = pd.to_numeric(df['Progress'], errors='coerce').fillna(0.0)
        
        # 3. FORCE MULTIPLICATION (Bypasses Google Sheet decimal compression)
        # If Google Sheet exports 1.0 (for 100%), this forces it to a true integer value of 100.0
        # If Google Sheet exports 0.35 (for 35%), this forces it to a true integer value of 35.0
        if df['Progress'].max() <= 1.0:
            df['Progress'] = df['Progress'] * 100.0
            
    else:
        df['Progress'] = 0.0

    # Calculate metrics using clean integer percentage scales (0 to 100)
    total_tasks = len(df)
    completed_tasks = len(df[df['Status'] == 'Completed'])
    
    # Overall summary bar calculation
    overall_progress_pct = int(df['Progress'].mean()) if total_tasks > 0 else 0
    top_bar_val = max(0.0, min(100.0, df['Progress'].mean())) / 100.0

    # Display status tiles at the top
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Tasks", value=total_tasks)
    col2.metric(label="Completed", value=completed_tasks, delta=f"+{completed_tasks} Done")
    col3.metric(label="Remaining", value=total_tasks - completed_tasks)

    # Display horizontal overall project completion bar
    st.write("### Overall Project Completion")
    st.progress(top_bar_val)
    st.write(f"📊 **{overall_progress_pct}%** of total project effort completed.")

    # 4. Create a clean visual clone specifically scaled down for Streamlit's ProgressColumn requirements
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
                format="%.0f%%",  # Maps 1.0 cleanly to 100% text
                min_value=0.0,
                max_value=1.0,
            )
        }
    )

except Exception as e:
    st.error("Connecting to live feed... Check your Google Sheets 'Publish to Web' setup if this takes too long.")
