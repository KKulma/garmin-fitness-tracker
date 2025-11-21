# streamlit_app.py
from datetime import date, timedelta
import calendar
import streamlit as st

from garmin_points import fetch_points_for_range  # <-- our new module

_CSS = r"""
:root{
  --circle-size: 140px;
  --mini-circle-size: 22px;
  --bg: #ffffff;
  --muted: #e9e9e9;
  --text: #1f2937;
  --text-muted: #4b5563;
  --green: #22c55e;
  --grey-circle-inner: #f3f4f6;
  --inner-green-bg: linear-gradient(180deg,rgba(34,197,94,0.18),rgba(34,197,94,0.08));
}

.app-container{padding:18px 20px;font-family:'Inter',Roboto,Arial;}
.header{text-align:center;margin-bottom:12px;display:none;}

.week-row{
  display:flex;
  flex-direction:row;
  justify-content:space-evenly;
  align-items:center;
  gap:20px;
  width:100%;
  overflow-x:auto;
}

.calendar-container{display:flex;flex-direction:column;gap:30px;padding-top:10px;}
.month-section h2{text-align:center;margin-bottom:10px;color:var(--text);}
.week-row-calendar{display:flex;flex-direction:row;justify-content:space-evenly;align-items:center;gap:8px;}

.circle, .mini-circle{
  border-radius:50%;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  border:2px solid transparent;
  box-shadow:0 1px 0 rgba(0,0,0,0.03);
}
.circle{width:var(--circle-size);height:var(--circle-size);background:var(--grey-circle-inner);border-width:8px;}
.mini-circle{width:var(--mini-circle-size);height:var(--mini-circle-size);background:var(--grey-circle-inner);font-size:10px;}
.circle.future,.mini-circle.future{opacity:0.45;filter:grayscale(0.4);}
.circle .day-label{font-size:16px;font-weight:600;color:var(--text);margin-top:6px;}
.circle .points{font-size:40px;font-weight:700;color:var(--text);}
.mini-circle .points{font-size:9px;font-weight:600;color:var(--text-muted);}
.circle.outer-green,.mini-circle.outer-green{border-color:var(--green);}
.circle.inner-green,.mini-circle.inner-green{background:var(--inner-green-bg);}
.circle.outer-green .day-label,.circle.inner-green .day-label{color:var(--text);}
.circle.outer-green .points,.circle.inner-green .points,.mini-circle.outer-green .points,.mini-circle.inner-green .points{color:#065f46;}
"""

def week_date_range_for(date_in_week: date):
    monday = date_in_week - timedelta(days=date_in_week.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday

def render_day_circle_html(day_date: date, today: date, points: int, week_total: int) -> str:
    classes = ["circle"]
    if day_date > today:
        classes.append("future")
    if (points >= 8) and (day_date <= today):
        classes.append("outer-green")
    if (week_total >= 40) and (day_date <= today):
        classes.append("inner-green")
    cls = " ".join(classes)
    label = calendar.day_name[day_date.weekday()][:3]
    return f"<div class='{cls}' style='display:flex;flex-direction:column;justify-content:center;align-items:center;'><div class='points'>{points}</div><div class='day-label'>{label}</div></div>"

def render_mini_circle_html(day_date: date, today: date, points: int, week_total: int) -> str:
    classes = ["mini-circle"]
    if day_date > today:
        classes.append("future")
    if (points >= 8) and (day_date <= today):
        classes.append("outer-green")
    if (week_total >= 40) and (day_date <= today):
        classes.append("inner-green")
    cls = " ".join(classes)
    return f"<div class='{cls}'><div class='points'>{points}</div></div>"

# ------------------ Streamlit App ------------------ #
st.set_page_config(page_title="Activity Tracker", layout="wide")
st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)

st.sidebar.markdown("## Navigation")
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

if st.sidebar.button("🏠 Home"):
    st.session_state.page = 'Home'
if st.sidebar.button("🗓️ Calendar"):
    st.session_state.page = 'Calendar'

page = st.session_state.page
today = date.today()

# ---------------- Caching Garmin Points ---------------- #
@st.cache_data(ttl=3600)
def get_points(start_date, end_date):
    return fetch_points_for_range(start_date, end_date)

# ------------------ Home Page ------------------ #
if page == "Home":
    monday, sunday = week_date_range_for(today)
    pts_map = get_points(monday, sunday)
    week_total = sum(pts_map.values())
    html = "<div class='app-container'><div class='week-row'>"
    for d in [monday + timedelta(days=i) for i in range(7)]:
        html += render_day_circle_html(d, today, pts_map.get(d, 0), week_total)
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)

# ------------------ Calendar Page ------------------ #
elif page == "Calendar":
    html = "<div class='app-container'><div class='calendar-container'>"
    current = today
    first_month = date(2025, 2, 1)

    while current >= first_month:
        month_days = calendar.monthcalendar(current.year, current.month)
        html += f"<div class='month-section'><h2>{calendar.month_name[current.month]} {current.year}</h2>"
        for week in month_days:
            html += "<div class='week-row-calendar'>"
            # Fetch points for the week
            week_start = date(current.year, current.month, week[0] or 1)
            week_end = date(current.year, current.month, week[-1] or 28)
            pts_map = get_points(week_start, week_end)

            for day in week:
                if day == 0:
                    html += "<div class='mini-circle future'></div>"
                else:
                    this_day = date(current.year, current.month, day)
                    pts = pts_map.get(this_day, 0)
                    # Calculate weekly total for inner-green logic
                    w_start, w_end = week_date_range_for(this_day)
                    week_total = sum(get_points(w_start, w_end).values())
                    html += render_mini_circle_html(this_day, today, pts, week_total)
            html += "</div>"
        html += "</div>"
        current = (current.replace(day=1) - timedelta(days=1)).replace(day=1)
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)
