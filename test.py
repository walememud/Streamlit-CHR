import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
import json

st.set_page_config(layout="wide")  # to use the entire page width

# Custom CSS to change the sidebar color
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #FFC72C; /* Blue color */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add logo under the sidebar
st.sidebar.image("images/etsu.png", use_column_width=True, caption="DEPARTMENT OF PUBLIC HEALTH")  # Display logo

# Title with custom styling and adjusted position
st.markdown(
    '''
    <style>
        .title {
            color: #00053E;
            text-align: center;
            margin-top: -80px;  /* Adjust this to move the title just above the navbar */
        }
    </style>
    <h1 class="title">UNITED STATES COUNTY HEALTH RANKING DASHBOARD</h1>
    ''',
    unsafe_allow_html=True
)

# Overview Section
st.subheader("Overview")
st.markdown(""" 
This website provides interactive charts of health indicators for the United States and its territories, sourced from the County Health Rankings (CHR) project by the University of Wisconsin's Population Health Institute. 
The CHR project tracks various health indicators for over 3,000 counties and independent cities across the U.S., with data available from 2010 onward.

Users can explore health data through dynamic percentile and time series charts, generated from County Health Rankings indicators for selected counties and states. 
The charts display counties and states as color-coded dots, allowing users to compare health indicators over time or across percentiles. Users can select specific indicators, years, counties, and states to generate tailored visualizations. 
Additionally, users can download these charts as PNG images for further analysis or local use.
""")

# Load dataset
min_year = 2010
max_year = date.today().year

# Custom CSS to style the "Filters" header with the gold color #FFC72C
st.markdown(
    """
    <style>
    /* Style the filters header */
    .gold-header {
        color: #00053E; /* Set text color to the specific gold shade */
        font-size: 24px; /* Optional: Adjust the font size */
        font-weight: bold; /* Optional: Make the text bold */
        text-align: center; /* Center align the header */
    }

    /* Set dropdown titles to gold (#FFC72C) */
    .sidebar .sidebar-content .stSelectbox label,
    .sidebar .sidebar-content .stMultiselect label {
        color: #00053E;  /* Gold color for all dropdown titles */
        font-size: 18px;  /* Optional: Adjust the font size */
        font-weight: bold; /* Optional: Make the text bold */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar filters
st.sidebar.markdown('<div class="gold-header">Filters</div>', unsafe_allow_html=True)

# Year selection with auto-selection of the most recent year
selected_year = st.sidebar.selectbox(
    "Select Year",
    options=list(range(max_year, min_year - 1, -1)),
    index=0
)

# Initialize filters if not already loaded from session or previous use
if 'selected_counties' not in st.session_state:
    st.session_state.selected_counties = []
if 'selected_attributes' not in st.session_state:
    st.session_state.selected_attributes = []

# Function to save filters to session state and to a JSON file
def save_filters_to_json():
    filters = {
        'selected_year': selected_year,
        'selected_counties': st.session_state.selected_counties,
        'selected_attributes': st.session_state.selected_attributes,
    }
    with open("filters.json", "w") as f:
        json.dump(filters, f)

# Load saved filters from JSON file
def load_saved_filters(file):
    try:
        filters = json.load(file)
        return filters
    except Exception as e:
        st.error(f"Error loading filters: {e}")
        return None

# Try loading saved filters if available
saved_filters = None
if 'uploaded_file' in st.session_state:
    uploaded_file = st.session_state.uploaded_file
    if uploaded_file is not None:
        saved_filters = load_saved_filters(uploaded_file)

# Sidebar - File upload option
uploaded_file = st.sidebar.file_uploader("Upload Saved Filters", type="json")

# If a file is uploaded, update session state with its contents
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file
    saved_filters = load_saved_filters(uploaded_file)
    if saved_filters:
        # Apply the loaded filters
        selected_year = saved_filters.get('selected_year', selected_year)
        st.session_state.selected_counties = saved_filters.get('selected_counties', [])
        st.session_state.selected_attributes = saved_filters.get('selected_attributes', [])

# Construct filename and load dataset
filename = f"chr{selected_year}.csv"
try:
    df = pd.read_csv(filename)
    st.write(f"Loaded data for year: {selected_year}")
except FileNotFoundError:
    st.error(f"Data file for year {selected_year} not found.")
    df = pd.DataFrame()

# Sidebar - Filter options
if not df.empty:
    # County selection
    if 'County' in df.columns:
        county_options = df['County'].unique()
        selected_counties = st.sidebar.multiselect(
            "Select County(ies)", 
            options=county_options, 
            default=st.session_state.selected_counties,  # Use saved counties if available
            help="Search and select one or more counties"
        )
        st.session_state.selected_counties = selected_counties

    # Attribute selection
    if len(df.columns) > 2:
        attribute_options = df.columns[2:]
        selected_attributes = st.sidebar.multiselect(
            "Select Attribute(s)",
            options=attribute_options,
            default=st.session_state.selected_attributes,  # Use saved attributes if available
            help="Search and select one or more attributes"
        )
        st.session_state.selected_attributes = selected_attributes

    # Save filters option
    save_filters_button = st.sidebar.button("Save Filters")
    if save_filters_button:
        save_filters_to_json()
        st.sidebar.success("Filters saved successfully!")

    # Option to download filters as JSON
    st.sidebar.download_button(
        label="Download Saved Filters",
        data=json.dumps({
            'selected_year': selected_year,
            'selected_counties': st.session_state.selected_counties,
            'selected_attributes': st.session_state.selected_attributes,
        }),
        file_name="filters.json",
        mime="application/json"
    )

# Proceed with chart generation as before (Percentile Chart / Time Series Chart)
# Chart rendering
chart_type = st.sidebar.selectbox("Select Chart Type", options=["Percentile Chart", "Line Chart"])

if chart_type == "Percentile Chart":
    if not st.session_state.selected_counties:
        st.warning("Please select at least one county.")
    elif not st.session_state.selected_attributes:
        st.warning("Please select at least one attribute.")
    else:
        for attribute in st.session_state.selected_attributes:
            fig = go.Figure()

            attribute_values = df[attribute].dropna().values

            if len(attribute_values) == 0:
                st.warning(f"No data available for the attribute: {attribute}")
                continue

            percentiles = np.percentile(attribute_values, [0, 25, 50, 75, 100])

            for county in st.session_state.selected_counties:
                county_value = df[df['County'] == county][attribute].values[0]
                county_percentile = (np.sum(attribute_values < county_value) / len(attribute_values)) * 100
                
                # Add scatter points dynamically with default color scheme
                fig.add_trace(go.Scatter(
                    x=[county_percentile],  # This is the x data
                    y=[county_value],  # This is the y data
                    mode="markers",
                    name=f"{county} (Value: {county_value:.3f})",
                    marker=dict(size=10),  # Dynamically assigns color
                    hovertemplate=(
                        f"County: {county}<br>"
                        f"Percentile: {county_percentile:.3f}<br>"  # Use the correct variable for percentile
                        f"Value: {county_value:.3f}<br><extra></extra>"
                    ),
                ))

            fig.update_layout(
                title=f"Percentile Distribution for {attribute}",
                title_x=0.5,  # Center the title horizontally
                title_xanchor="center",  # Ensure the title is anchored in the center
                title_font=dict(
                    size=24,  # Set the title font size (adjust as needed)
                    color="black",  # Optional: set the title color
                ),
                xaxis_title="Percentile",
                yaxis_title="Value",
                xaxis=dict(
                    range=[0, 100],  # Explicit
                ))
    # Assuming your years range and chart type selection are already set
elif chart_type == "Line Chart":
        if not selected_counties:
            st.warning("Please select at least one county.")
        elif len(selected_attributes) != 1:
            st.warning("Please select exactly one attribute for the line chart.")
        else:
            attribute = selected_attributes[0]
            years = list(range(min_year, max_year + 1))
            data = {county: [] for county in selected_counties}

            for year in years:
                try:
                    yearly_data = pd.read_csv(f"chr{year}.csv")
                    
                    # Check if the selected attribute exists in the dataset for this year
                    if attribute not in yearly_data.columns:
                        yearly_data[attribute] = np.nan  # Add the attribute with NaN values if it's missing
                        
                    for county in selected_counties:
                        if county in yearly_data['County'].values:
                            value = yearly_data.loc[yearly_data['County'] == county, attribute].values[0]
                            data[county].append(value)
                        else:
                            data[county].append(np.nan)  # Set NaN if county not found in the year
                except FileNotFoundError:
                    for county in selected_counties:
                        data[county].append(np.nan)  # Set NaN if file is not found

            fig = go.Figure()

            # Add traces for each county dynamically
            for county, values in data.items():
                fig.add_trace(go.Scatter(
                    x=years,
                    y=values,
                    mode='lines+markers',
                    name=county,
                    hovertemplate="Year: %{x}<br>Value: %{y}<br><extra></extra>"
                ))

            fig.update_layout(
                title=f"Trends Over Time for {attribute}",
                title_x=0.5,  # Center the title horizontally
                title_xanchor="center",  # Ensure the title is anchored in the center
                title_font=dict(
                    size=24,  # Set the title font size (adjust as needed)
                    color="black",  # Optional: set the title color
                ),
                xaxis_title="Year",
                yaxis_title=attribute,
                showlegend=True,
                template="plotly",
                xaxis=dict(
                    tickmode='array',  # Use a custom array for ticks
                    tickvals=years,    # Specify the years to show on the x-axis
                    ticktext=[str(year) for year in years],  # Show each year as a label
                ),
                width=1200,  # Set the width of the plot
                height=600,  # Set the height of the plot
            )


            st.plotly_chart(fig)

            # Provide the option to download the chart
            image_buf = save_chart_as_image(fig)
            st.download_button(
                label="Download Line Chart as Image",
                data=image_buf,
                file_name=f"{attribute}_line_chart.png",
                mime="image/png"
            )

