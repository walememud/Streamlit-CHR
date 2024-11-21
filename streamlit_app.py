import streamlit as st

# Define pages as functions
def chart_page():
    import ma
    ma.app()

# Define page navigation
PAGES = {
    "Chart Page": chart_page,
}

# Add navigation to the sidebar
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

# Call the selected page function
page = PAGES[selection]
page()
