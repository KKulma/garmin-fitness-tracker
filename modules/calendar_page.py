import streamlit as st
import datetime
import calendar

def render_calendar_page():
    st.markdown("<h1 style='text-align: center;'>Activity Calendar</h1>", unsafe_allow_html=True)

    # Mock Data (Extend logic from Home)
    # Let's show Feb 2025 as requested
    year = 2025
    month = 2
    
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    st.subheader(f"{month_name} {year}")

    # Mock Data: Randomly assign points for demo
    # In real app, fetch from DB/API
    mock_calendar_data = {}
    # Just filling some days for visualization
    mock_calendar_data[1] = 10
    mock_calendar_data[5] = 4
    mock_calendar_data[15] = 9
    mock_calendar_data[20] = 12
    
    # Header
    cols = st.columns(7)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, day in enumerate(days):
        cols[i].markdown(f"<div class='calendar-header'>{day}</div>", unsafe_allow_html=True)

    # Grid
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("") # Empty slot
                continue
            
            points = mock_calendar_data.get(day, 0)
            
            # Logic
            classes = ["mini-circle"]
            if points > 8:
                classes.append("completed")
            
            # Weekly goal logic for calendar is tricky without full week data
            # For now, let's assume a mock week goal for the week of the 15th
            if 10 <= day <= 16: 
                classes.append("week-goal")

            class_str = " ".join(classes)
            
            html = f"""<div class="calendar-day"><span style="align-self: flex-start; color: #888;">{day}</span><div class="{class_str}">{points if points > 0 else "-"}</div></div>"""
            cols[i].markdown(html, unsafe_allow_html=True)
