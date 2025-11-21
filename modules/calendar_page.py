import streamlit as st
import datetime
import calendar
from modules import database

def render_calendar_page():
    st.markdown("<h1 style='text-align: center;'>Activity Calendar</h1>", unsafe_allow_html=True)

    # Date Selection (Default to current month or allow navigation)
    # For simplicity, let's show the current month or a specific month if requested.
    # The user asked for "since February 2025". 
    # Let's add a month selector.
    
    today = datetime.date.today()
    
    # Generate list of months from Feb 2025 to Today
    start_date = datetime.date(2025, 2, 1)
    months = []
    curr = start_date
    while curr <= today:
        months.append(curr)
        # Move to next month
        if curr.month == 12:
            curr = datetime.date(curr.year + 1, 1, 1)
        else:
            curr = datetime.date(curr.year, curr.month + 1, 1)
            
    # Reverse to show latest first
    months.reverse()
    
    # Format for selectbox
    month_options = [d.strftime("%B %Y") for d in months]
    selected_month_str = st.selectbox("Select Month", month_options)
    
    # Parse selected month
    selected_month_date = datetime.datetime.strptime(selected_month_str, "%B %Y").date()
    year = selected_month_date.year
    month = selected_month_date.month
    
    cal = calendar.monthcalendar(year, month)
    
    # Fetch data for the whole month from DB
    _, last_day = calendar.monthrange(year, month)
    month_start = datetime.date(year, month, 1)
    month_end = datetime.date(year, month, last_day)
    
    db_data = database.get_data_range(month_start, month_end)
    
    # Debug info
    st.info(f"Loaded {len(db_data)} days of data for {month_options[0] if month_options else ''}")
    
    # Header
    cols = st.columns(7)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, day in enumerate(days):
        cols[i].markdown(f"<div class='calendar-header'>{day}</div>", unsafe_allow_html=True)

    # Grid
    for week in cal:
        # Calculate weekly points for highlighting
        weekly_total = 0
        for day in week:
            if day == 0: continue
            d_date = datetime.date(year, month, day)
            d_data = db_data.get(d_date)
            if d_data:
                weekly_total += d_data.get("points", 0)
        
        row_class = "week-row-highlight" if weekly_total >= 40 else ""
        
        # Create columns with a container for styling if possible, 
        # but Streamlit columns don't support direct styling easily.
        # We might need to wrap the whole row in HTML or just style individual cells if we can't style the row.
        # Actually, we can generate the whole week as HTML to control the row style.
        # But to keep it simple with Streamlit columns, let's try to wrap the content.
        # Alternatively, we can use a single HTML block for the calendar grid, but that loses Streamlit's layout ease.
        # Let's stick to columns but maybe add a background to the cells if the week is good?
        # Or better: Just render the whole calendar as HTML? No, that's too much change.
        # Let's try to inject a div around the week? Streamlit doesn't allow nesting columns in divs easily.
        # Compromise: If week goal met, we can add a special style to the cells or use a container.
        # Let's try to use st.container with a custom class if possible, or just style the cells.
        # The user asked to "highlight the whole week row".
        # Let's build the HTML for the row manually.
        
        html_row = f"<div class='calendar-row {row_class}' style='display: flex; justify-content: space-around; padding: 5px; border-radius: 10px; margin-bottom: 5px;'>"
        
        for i, day in enumerate(week):
            if day == 0:
                html_row += "<div style='width: 14%;'></div>"
                continue
            
            current_date = datetime.date(year, month, day)
            day_data = db_data.get(current_date)
            points = day_data["points"] if day_data else 0
            if points is None: points = 0
            
            steps = day_data.get("steps", 0) if day_data else 0
            activities = day_data.get("activities", []) if day_data else []
            
            # Tooltip
            tooltip_lines = [f"Steps: {steps}"]
            for act in activities:
                act_type = act.get('activityType', {}).get('typeKey', 'Activity')
                duration = act.get('duration', 0) // 60
                avg_hr = act.get('averageHR', 0)
                tooltip_lines.append(f"{act_type}: {duration}m (HR: {avg_hr})")
            tooltip_text = "&#10;".join(tooltip_lines)

            # Logic
            classes = ["mini-circle"]
            if points >= 8:
                classes.append("completed")
            
            class_str = " ".join(classes)
            
            html_row += f"""<div class="calendar-day" style="width: 14%;"><span style="align-self: flex-start; color: #888;">{day}</span><div class="{class_str}">{points if points > 0 else "-"}</div><span class="tooltip-text">{tooltip_text}</span></div>"""
        
        html_row += "</div>"
        st.markdown(html_row, unsafe_allow_html=True)
