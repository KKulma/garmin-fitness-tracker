import streamlit as st
import datetime

def render_home_page():
    st.markdown("<h1 style='text-align: center;'>Weekly Activity</h1>", unsafe_allow_html=True)

    # Mock Data Generation (Replace with actual data fetching later)
    # Assuming today is Wednesday for demo purposes if not specified
    today = datetime.date.today()
    
    # Calculate start of the week (Monday)
    start_of_week = today - datetime.timedelta(days=today.weekday())
    
    # Mock points for the week
    # Mon: 10 (Goal Met), Tue: 5 (Missed), Wed: 12 (Goal Met), Thu-Sun: Future
    mock_data = {
        0: 10, # Mon
        1: 5,  # Tue
        2: 12, # Wed
        3: 0,  # Thu
        4: 0,  # Fri
        5: 0,  # Sat
        6: 0   # Sun
    }

    total_weekly_points = sum(mock_data.values())
    week_goal_met = total_weekly_points >= 40

    # HTML Construction for Circles
    html_content = '<div class="activity-container">'
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for i in range(7):
        current_day_date = start_of_week + datetime.timedelta(days=i)
        points = mock_data.get(i, 0)
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
