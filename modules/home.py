import streamlit as st
import datetime
from modules import backend

def render_home_page():
    st.markdown("<h1 style='text-align: center;'>Weekly Activity</h1>", unsafe_allow_html=True)

    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    
    # Fetch data for the week
    # To optimize, we could fetch in batch if backend supported it, but loop is fine for 7 days
    weekly_points = {}
    
    # Progress bar or spinner could be nice here
    with st.spinner("Fetching weekly data..."):
        for i in range(7):
            day_date = start_of_week + datetime.timedelta(days=i)
            if day_date > today:
                weekly_points[i] = 0
                continue
                
            data = backend.get_daily_data(day_date)
            points = backend.calculate_points(data["steps"], data["activities"])
            weekly_points[i] = points

    total_weekly_points = sum(weekly_points.values())
    week_goal_met = total_weekly_points >= 40

    # HTML Construction for Circles
    html_content = '<div class="activity-container">'
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for i in range(7):
        current_day_date = start_of_week + datetime.timedelta(days=i)
        points = weekly_points.get(i, 0)
        day_name = days[i]
        
        # Determine classes
        classes = ["activity-circle"]
        
        if current_day_date > today:
            classes.append("future")
            display_text = ""
        else:
            display_text = str(points)
            if points > 8:
                classes.append("completed")
        
        if week_goal_met:
            classes.append("week-goal")
            
        class_str = " ".join(classes)
        
        html_content += f"""<div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 10px;"><div class="{class_str}">{display_text}</div><div class="day-label">{day_name}</div></div>"""
        
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Debug/Info
    st.caption(f"Total Weekly Points: {total_weekly_points} / 40")
