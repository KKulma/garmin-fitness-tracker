"""
Streamlit front-end for Activity Points tracker

This file implements the front-end UI you requested (Home + Calendar) and **gracefully handles
environments where the `streamlit` package is not available**.

Behavior:
- Home: 7 large circles (Mon-Sun) representing the current week
- Calendar: months from Feb 2025 through today; each day has a miniature activity circle

Coloring rules (as provided by you):
- For any day **after today**: the circle is greyed out (future)
- For any past or current day:
  - Display the day's activity points inside the circle
  - If day's points >= 8 -> outer rind (border) green
  - If the sum of points in the week >= 40 -> inner fill of ALL circles in that week is green

Important:
- This file contains a **mock data loader** (`mock_fetch_points_by_date`) which you should replace
  with your backend `fetch_points_by_date(start_date, end_date)` when you provide it.
- If `streamlit` is NOT installed, the script will generate a static HTML preview file
  `activity_preview.html` in the current working directory so you can inspect the UI.
  It will also run a couple of basic sanity tests on the mock loader.

To run the interactive Streamlit app (when you have streamlit installed):
    pip install streamlit
    streamlit run streamlit_activity_frontend.py

If streamlit is not available, simply run:
    python streamlit_activity_frontend.py
and the static preview will be generated.
"""

from datetime import date, timedelta
from typing import Dict, List, Tuple
import calendar
import os
import sys
import traceback

# Try to import streamlit; if not present, we'll fallback to generating a static HTML preview
try:
    import streamlit as st
    ST_AVAILABLE = True
except Exception:
    ST_AVAILABLE = False

# ------------------
# Shared CSS used by both Streamlit and static HTML
# ------------------
_CSS = r"""
:root{
  --circle-size: 140px;
  --mini-circle-size: 22px;
  --bg: #ffffff;
  --muted: #e9e9e9;
  --text: #111827;
  --green: #22c55e;
  --grey-circle-inner: #f3f4f6;
}

.app-container{
  padding: 18px 20px;
  font-family: 'Inter', Roboto, -apple-system, 'Segoe UI', 'Helvetica Neue', Arial;
}

.header{
  text-align: center;
  margin-bottom: 12px;
}

.week-grid{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  justify-items: center;
  align-items: center;
}

.circle{
  width: var(--circle-size);
  height: var(--circle-size);
  border-radius: 999px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  box-shadow: 0 1px 0 rgba(0,0,0,0.03);
  background: var(--grey-circle-inner);
  position: relative;
  border: 8px solid transparent;
}

.circle.future{
  opacity: 0.45;
  filter: grayscale(0.4);
}

.circle .day-label{
  font-size: 16px;
  color: var(--text);
}

.circle .points{
  font-size: 40px;
  font-weight: 700;
  margin-top: 6px;
  color: var(--text);
}

.circle.outer-green{
  border-color: var(--green);
}

.circle.inner-green{
  background: linear-gradient(180deg, rgba(34,197,94,0.14), rgba(34,197,94,0.06));
}

.calendar-month{
  margin-bottom: 18px;
}
.month-title{
  font-weight: 700;
  font-size: 18px;
  margin-bottom: 6px;
}
.month-grid{
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.mini-day{
  width: 100%;
  height: 36px;
  display:flex;
  justify-content:flex-start;
  align-items:center;
  padding-left: 6px;
}

.mini-circle{
  width: var(--mini-circle-size);
  height: var(--mini-circle-size);
  border-radius: 999px;
  background: var(--grey-circle-inner);
  display:inline-flex;
  justify-content:center;
  align-items:center;
  font-size: 12px;
}

.mini-circle.outer-green{ border: 2px solid var(--green); }
.mini-circle.inner-green{ background: var(--green); color: white; }
.mini-circle.future{ opacity: 0.35; filter: grayscale(0.4); }

.weekday-headers{ display:grid; grid-template-columns: repeat(7, 1fr); gap:8px; margin-bottom:6px;}
.weekday-headers div{ text-align:center; font-size:12px; color:#374151 }

"""

# ------------------
# Mock data loader (replace when backend is provided)
# ------------------

def mock_fetch_points_by_date(start_date: date, end_date: date) -> Dict[date, int]:
    """Return mock points mapping for demonstration.

    Produces a deterministic pattern for visualization and testing.
    """
    results: Dict[date, int] = {}
    d = start_date
    seed = 0
    while d <= end_date:
        weekday = d.weekday()  # Mon=0..Sun=6
        if weekday in (5, 6):
            pts = 9
        elif weekday == 0:
            pts = 6
        elif weekday == 2:
            pts = 8
        else:
            pts = 4
        pts = max(0, pts + ((d.day + seed) % 3) - 1)
        results[d] = int(pts)
        d = d + timedelta(days=1)
        seed += 1
    return results

# A thin wrapper you will replace with your real backend function in future
def fetch_points_by_date(start_date: date, end_date: date) -> Dict[date, int]:
    return mock_fetch_points_by_date(start_date, end_date)

# ------------------
# Date helpers
# ------------------

def week_date_range_for(date_in_week: date) -> Tuple[date, date]:
    monday = date_in_week - timedelta(days=date_in_week.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def is_future(d: date, today: date) -> bool:
    return d > today


def months_since(start_year: int, start_month: int, end: date) -> List[Tuple[int, int]]:
    months: List[Tuple[int, int]] = []
    year = start_year
    month = start_month
    while (year < end.year) or (year == end.year and month <= end.month):
        months.append((year, month))
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months

# ------------------
# Rendering helpers for static HTML
# ------------------

def render_day_circle_html(day_date: date, today: date, points: int, week_total: int) -> str:
    classes = ["circle"]
    if is_future(day_date, today):
        classes.append("future")
    if (points >= 8) and (not is_future(day_date, today)):
        classes.append("outer-green")
    if (week_total >= 40) and (not is_future(day_date, today)):
        classes.append("inner-green")
    cls = " ".join(classes)
    day_label = calendar.day_name[day_date.weekday()][:3]
    return f"<div class='{cls}'><div class='day-label'>{day_label}</div><div class='points'>{points}</div></div>"


def render_mini_circle_html(day_date: date, today: date, points: int, week_total: int) -> str:
    classes = ["mini-circle"]
    if is_future(day_date, today):
        classes.append("future")
    if (points >= 8) and (not is_future(day_date, today)):
        classes.append("outer-green")
    if (week_total >= 40) and (not is_future(day_date, today)):
        classes.append("inner-green")
    cls = " ".join(classes)
    content = f"{points}" if not is_future(day_date, today) else ""
    return f"<div class='{cls}' title='{day_date.isoformat()} - {points} pts'>{content}</div>"

# ------------------
# Static HTML generation (fallback)
# ------------------

def generate_static_preview(output_path: str, cal_start: date, today: date, points_map: Dict[date, int]) -> None:
    """Create a single HTML file containing both Home and Calendar previews."""
    # Home
    monday, sunday = week_date_range_for(today)
    week_dates = [monday + timedelta(days=i) for i in range(7)]
    week_total = sum(points_map.get(d, 0) for d in week_dates)

    home_html = ""
    home_html += "<div class='app-container'>"
    home_html += "<div class='header'><h1>Home</h1></div>"
    home_html += "<div class='week-grid'>"
    for d in week_dates:
        pts = int(points_map.get(d, 0))
        home_html += render_day_circle_html(d, today, pts, week_total)
    home_html += "</div>"
    home_html += f"<div style='margin-top:12px'><b>This week total:</b> {week_total}</div>"
    home_html += "<div style='margin-top:10px'><b>Legend:</b><ul><li>Future days are greyed out</li><li>Day &ge; 8 points = outer green ring</li><li>Week &ge; 40 points = inner green fill on all days in the week</li></ul></div>"
    home_html += "</div>"

    # Calendar
    months = months_since(2025, 2, today)
    cal_html = ""
    cal_html += "<div class='app-container'>"
    cal_html += "<div class='header'><h1>Calendar</h1></div>"

    cal_html += "<div style='display:grid;grid-template-columns:repeat(2,1fr);gap:18px;'>"
    for (y, m) in months:
        cal_html += "<div class='calendar-month'>"
        cal_html += f"<div class='month-title'>{calendar.month_name[m]} {y}</div>"
        # weekday headers
        cal_html += "<div class='weekday-headers'>"
        for wd in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']:
            cal_html += f"<div>{wd}</div>"
        cal_html += "</div>"

        cal = calendar.Calendar(firstweekday=0)
        month_days = list(cal.itermonthdates(y, m))
        cal_html += "<div class='month-grid'>"
        # iterate weeks (chunks of 7)
        for w_start in range(0, len(month_days), 7):
            week = month_days[w_start:w_start+7]
            week_total = sum(points_map.get(d, 0) for d in week if d.month == m and d <= today)
            for d in week:
                if d.month != m:
                    cal_html += "<div class='mini-day'></div>"
                else:
                    pts = int(points_map.get(d, 0))
                    mini = render_mini_circle_html(d, today, pts, week_total)
                    cal_html += f"<div class='mini-day'>{mini}<div style='margin-left:6px;font-size:12px;color:#374151'>{d.day}</div></div>"
        cal_html += "</div>"  # end month-grid
        cal_html += "</div>"  # end calendar-month
    cal_html += "</div>"  # grid container
    cal_html += "</div>"  # app-container

    full_html = f"<!doctype html><html><head><meta charset='utf-8'><title>Activity Tracker Preview</title><style>{_CSS}</style></head><body style='background:var(--bg);'><div style='display:flex;gap:24px;align-items:flex-start;padding:18px;'>{home_html}<div style='width:24px'></div>{cal_html}</div></body></html>"

    with open(output_path, 'w', encoding='utf-8') as fh:
        fh.write(full_html)

# ------------------
# Basic tests / sanity checks
# ------------------

def run_basic_tests():
    print("Running basic tests on mock_fetch_points_by_date()...")
    s = date(2025, 2, 1)
    e = date(2025, 2, 10)
    m = mock_fetch_points_by_date(s, e)
    # test: correct number of days
    expected_len = (e - s).days + 1
    assert len(m) == expected_len, f"Expected {expected_len} days, got {len(m)}"
    # test: all values are ints >= 0
    for k, v in m.items():
        assert isinstance(k, date), "Keys must be date objects"
        assert isinstance(v, int) and v >= 0, "Points must be non-negative integers"
    print("Basic tests passed.")

# ------------------
# Entrypoint
# ------------------

def main():
    TODAY = date.today()
    CAL_START = date(2025, 2, 1)

    # Fetch points for entire calendar range (frontend expects this)
    points_map = fetch_points_by_date(CAL_START, TODAY)

    if ST_AVAILABLE:
        # Use Streamlit UI (same layout/behaviour as originally implemented)
        try:
            st.set_page_config(page_title="Activity Tracker", layout="wide")
            st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)

            PAGE = st.sidebar.radio("Page", ["Home", "Calendar"]) 

            def pts_for(d: date) -> int:
                return int(points_map.get(d, 0))

            if PAGE == "Home":
                st.markdown("<div class='app-container'>", unsafe_allow_html=True)
                st.markdown("<div class='header'><h1>Home</h1></div>", unsafe_allow_html=True)

                monday, sunday = week_date_range_for(TODAY)
                week_dates = [monday + timedelta(days=i) for i in range(7)]
                week_total = sum(pts_for(d) for d in week_dates)

                html = "<div class='week-grid'>"
                for d in week_dates:
                    points = pts_for(d)
                    # re-use static renderers for consistency
                    html += render_day_circle_html(d, TODAY, points, week_total)
                html += "</div></div>"
                st.markdown(html, unsafe_allow_html=True)

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.write("### This week total")
                    st.metric(label="Points (Mon-Sun)", value=str(week_total))
                with col2:
                    st.write("#### Legend")
                    st.write("- Future days are greyed out")
                    st.write("- If a day has >= 8 points, the circle gets an outer green ring")
                    st.write("- If the week total >= 40, all circles for that week have an inner green fill")

            else:  # Calendar page
                st.markdown("<div class='app-container'>", unsafe_allow_html=True)
                st.markdown("<div class='header'><h1>Calendar</h1></div>", unsafe_allow_html=True)

                months = months_since(2025, 2, TODAY)
                cols_per_row = 2
                for i in range(0, len(months), cols_per_row):
                    row_months = months[i:i+cols_per_row]
                    cols = st.columns(len(row_months))
                    for col, (y, m) in zip(cols, row_months):
                        with col:
                            st.markdown(f"<div class='calendar-month'>", unsafe_allow_html=True)
                            st.markdown(f"<div class='month-title'>{calendar.month_name[m]} {y}</div>", unsafe_allow_html=True)

                            hdrs = "<div class='weekday-headers'>"
                            for wd in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']:
                                hdrs += f"<div>{wd}</div>"
                            hdrs += "</div>"
                            st.markdown(hdrs, unsafe_allow_html=True)

                            cal = calendar.Calendar(firstweekday=0)
                            month_days = list(cal.itermonthdates(y, m))
                            grid_html = "<div class='month-grid'>"
                            for w_start in range(0, len(month_days), 7):
                                week = month_days[w_start:w_start+7]
                                week_total = sum(points_map.get(d, 0) for d in week if d.month == m and d <= TODAY)
                                for d in week:
                                    if d.month != m:
                                        grid_html += "<div class='mini-day'></div>"
                                    else:
                                        pts = int(points_map.get(d, 0))
                                        mini = render_mini_circle_html(d, TODAY, pts, week_total)
                                        grid_html += f"<div class='mini-day'>{mini}<div style='margin-left:6px;font-size:12px;color:#374151'>{d.day}</div></div>"
                            grid_html += "</div>"
                            st.markdown(grid_html, unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

        except Exception:
            st.error("An error occurred while rendering the Streamlit UI. See console for details.")
            traceback.print_exc()

    else:
        # Streamlit not available -> generate static HTML preview and run simple tests
        out = os.path.join(os.getcwd(), "activity_preview.html")
        generate_static_preview(out, CAL_START, TODAY, points_map)
        print("\n--- STREAMLIT NOT AVAILABLE ---\n")
        print("A static HTML preview was generated at:\n", out)
        print("Open that file in your browser to inspect the UI.\n")
        print("To run the interactive app, install streamlit and run: pip install streamlit && streamlit run streamlit_activity_frontend.py\n")
        try:
            run_basic_tests()
        except AssertionError as e:
            print("Self-test failed:", e)
        except Exception:
            print("Unexpected error during tests:")
            traceback.print_exc()


if __name__ == '__main__':
    main()
