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
    
    # Strip accidental extra spacing from text cells
    df['Status'] = df['Status'].astype(str).str.strip()
    
    # Calculate executive metrics
    total_tasks = len(df)
    completed_tasks = len(df[df['Status'] == 'Completed'])
    progress_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    # Display status tiles at the top
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Tasks", value=total_tasks)
    col2.metric(label="Completed", value=completed_tasks, delta=f"+{completed_tasks} Done", delta_color="normal")
    col3.metric(label="Remaining", value=total_tasks - completed_tasks)

    # Display horizontal project visual completion bar
    st.write("### Total Completion Progress")
    st.progress(progress_percentage)
    st.write(f"📊 **{progress_percentage}%** of all assigned tasks are fully completed.")

    # Display detailed table view
    st.write("### Detailed Task Breakdown")
    st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Connecting to live feed... Check your Google Sheets 'Publish to Web' setup if this takes too long.")
