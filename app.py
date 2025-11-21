import streamlit as st
from modules.home import render_home_page
from modules.calendar_page import render_calendar_page

# Page Config
st.set_page_config(
    page_title="Garmin Activity Fetcher",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("assets/style.css")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Calendar"])

# Page Routing
if page == "Home":
    render_home_page()
elif page == "Calendar":
    render_calendar_page()

# Footer / Debug info
st.sidebar.markdown("---")
st.sidebar.caption("v1.0.0 | Garmin Activity Fetcher")
