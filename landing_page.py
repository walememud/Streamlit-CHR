import streamlit as st
from landing_page import app as landing_page
from ma import app as chart_page

# Sidebar Navigation
st.sidebar.title("Navigation")
pages = {
    "Landing Page": landing_page,
    "Chart Page": chart_page,
}
selected_page = st.sidebar.radio("Go to", list(pages.keys()))

# Render the selected page
pages[selected_page]()
