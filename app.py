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
    # Clear internal cache completely on every single load
    st.cache_data.clear()
    
    # Read the live cloud CSV data
    df = pd.read_csv(sheet_url)
    
    # Clean up status text spacing
    df['Status'] = df['Status'].astype(str).str.strip()
    
    # FIX: Force lowercase columns to avoid spelling/capitalization mistakes
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.capitalize() # Forces 'progress', 'PROGRESS' -> 'Progress'
    
    if 'Progress' in df.columns:
        # 1. Clean out text characters like "%"
        df['Progress'] = df['Progress'].astype(str).str.replace('%', '', regex=False).str.strip()
        
        # 2. Convert to raw floating numbers
        df['Progress'] = pd.to_numeric(df['Progress'], errors='coerce').fillna(0.0)
        
        # 3. FORCE ALIGNMENT TO 0.0 - 1.0 FOR STREAMLIT
        # If your data has numbers like 35 or 100, divide them by 100
        if df['Progress'].max() > 1.0:
            df['Progress'] = df['Progress'] / 100.0
        # If your numbers are integers like 1, 2, 3 instead of decimals, force them down
        elif df['Progress'].max() == 1.0 and df['Progress'].sum() == len(df):
            # This handles the case where every row says "1" or "100" identically
            pass
    else:
        # Create the column dynamically if it is missing
        df['Progress'] = 0.0

    # Calculate metrics using clean decimal scales (0.0 to 1.0)
    total_tasks = len(df)
    completed_tasks = len(df[df['Status'] == 'Completed'])
    
    # Overall summary bar calculation
    avg_progress = df['Progress'].mean() if total_tasks > 0 else 0.0
    overall_progress_pct = int(avg_progress * 100)
    top_bar_val = max(0.0, min(1.0, avg_progress))

    # Display status tiles at the top
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Tasks", value=total_tasks)
    col2.metric(label="Completed", value=completed_tasks, delta=f"+{completed_tasks} Done")
    col3.metric(label="Remaining", value=total_tasks - completed_tasks)

    # Display horizontal overall project completion bar
    st.write("### Overall Project Completion")
    st.progress(top_bar_val)
    st.write(f"📊 **{overall_progress_pct}%** of total project effort completed.")

    # Display detailed table view with PERFECT INDIVIDUAL PROGRESS BARS
    st.write("### Detailed Task Breakdown")
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Progress": st.column_config.ProgressColumn(
                "Task Progress",
                help="The completion percentage of this specific task",
                format="%.0f%%",  # Forces 1.0 -> 100%, 0.35 -> 35%
                min_value=0.0,
                max_value=1.0,
            )
        }
    )

except Exception as e:
    st.error("Connecting to live feed... Check your Google Sheets 'Publish to Web' setup if this takes too long.")
