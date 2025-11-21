import streamlit as st
from modules.home import render_home_page
from modules.calendar_page import render_calendar_page
from modules import backend

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

# Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = backend.login()

if not st.session_state.logged_in:
    st.sidebar.title("Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if backend.login(email, password):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.sidebar.error("Login failed")
    
    st.title("Please Login")
    st.write("Enter your Garmin Connect credentials in the sidebar to continue.")
    st.stop()

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
if st.sidebar.button("Logout"):
    # In a real app, we might want to clear garth session too, but for now just session state
    st.session_state.logged_in = False
    st.rerun()
st.sidebar.caption("v1.0.0 | Garmin Activity Fetcher")
