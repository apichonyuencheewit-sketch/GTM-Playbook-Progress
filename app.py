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
        # Convert values to strings to scrub away any existing '%' characters
        df['Progress'] = df['Progress'].astype(str).str.replace('%', '', regex=False)
        # Force into a clean floating number
        df['Progress'] = pd.to_numeric(df['Progress'], errors='coerce').fillna(0.0)
        
        # Core alignment: Ensure everything uses a standard 0-100 integer metric system
        if df['Progress'].max() <= 1.0 and df['Progress'].sum() > 0:
            df['Progress'] = df['Progress'] * 100.0
    else:
        df['Progress'] = 0.0

    # Calculate top metrics
    total_tasks = len(df)
    completed_tasks = len(df[df['Status'] == 'Completed'])
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

    st.write("### Detailed Task Breakdown")
    
    # FIX: Build the ENTIRE HTML table in a single string variable first
    html_table = """
    <table style="width:100%; border-collapse: collapse; font-family: sans-serif; background-color: #0e1117;">
        <tr style="background-color: #1e222b; border-bottom: 2px solid #4c566a; text-align: left;">
            <th style="padding: 12px; color: #eceff4;">Task Name</th>
            <th style="padding: 12px; color: #eceff4;">Status</th>
            <th style="padding: 12px; color: #eceff4;">Due Date</th>
            <th style="padding: 12px; color: #eceff4;">Priority</th>
            <th style="padding: 12px; color: #eceff4; width: 40%;">Task Progress</th>
        </tr>
    """

    # Append rows to our master HTML string variable
    for _, row in df.iterrows():
        prog_val = int(row['Progress'])
        prog_val = max(0, min(100, prog_val))  # Bound safely to 0-100%
        
        # Pick bar color accent based on tracking progression metric
        bar_color = "#ff4b4b" if prog_val < 100 else "#00e676"
        
        # HTML progress tracking structure inject
        html_progress_bar = f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="background-color: #2e3440; border-radius: 10px; width: 100%; height: 12px; overflow: hidden; border: 1px solid #434c5e; min-width: 100px;">
                <div style="background-color: {bar_color}; width: {prog_val}%; height: 100%; border-radius: 10px;"></div>
            </div>
            <span style="font-weight: bold; min-width: 40px; color: #eceff4;">{prog_val}%</span>
        </div>
        """
        
        html_table += f"""
        <tr style="border-bottom: 1px solid #3b4252;">
            <td style="padding: 12px; color: #e5e9f0;">{row.get('Task Name', 'N/A')}</td>
            <td style="padding: 12px; color: #e5e9f0;"><span style="background-color:#434c5e; padding:3px 8px; border-radius:5px; font-size:12px;">{row.get('Status', 'N/A')}</span></td>
            <td style="padding: 12px; color: #e5e9f0;">{row.get('Due Date', 'N/A')}</td>
            <td style="padding: 12px; color: #e5e9f0;">{row.get('Priority', 'N/A')}</td>
            <td style="padding: 12px;">{html_progress_bar}</td>
        </tr>
        """
        
    html_table += "</table>"

    # Print the entire table structure at once
    st.markdown(html_table, unsafe_allow_html=True)

except Exception as e:
    st.error("Connecting to live feed... Check your Google Sheets 'Publish to Web' setup if this takes too long.")
