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
        
        # Fetch detailed data for tooltip
        # We need to fetch data again or store it. 
        # Optimization: We fetched it above but didn't store details. 
        # Let's refactor slightly to store details in weekly_points or fetch again (fetch is fast if cached/local)
        # For simplicity and since we have get_daily_data, let's just re-fetch or better yet, store it in the first loop.
        # Actually, let's just fetch it here, it's local DB or cached.
        
        data = backend.get_daily_data(current_day_date)
        steps = data.get("steps", 0)
        activities = data.get("activities", [])
        
        # Build Tooltip Text
        tooltip_lines = [f"Steps: {steps}"]
        for act in activities:
            act_type = act.get('activityType', {}).get('typeKey', 'Activity')
            duration = act.get('duration', 0) // 60
            avg_hr = act.get('averageHR', 0)
            tooltip_lines.append(f"{act_type}: {duration}m (HR: {avg_hr})")
            
        tooltip_text = "&#10;".join(tooltip_lines) # HTML entity for newline
        
        # Determine classes
        classes = ["activity-circle"]
        
        if current_day_date > today:
            classes.append("future")
            display_text = ""
        else:
            display_text = str(points)
            if points >= 8:
                classes.append("completed")
        
        if week_goal_met:
            classes.append("week-goal")
            
        class_str = " ".join(classes)
        
        html_content += f"""<div class="activity-circle-wrapper"><div class="{class_str}">{display_text}</div><div class="day-label">{day_name}</div><span class="tooltip-text">{tooltip_text}</span></div>"""
        
    html_content += '</div>'
    
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Debug/Info
    st.caption(f"Total Weekly Points: {total_weekly_points} / 40")
