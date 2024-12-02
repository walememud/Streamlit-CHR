import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
import io
import json

st.set_page_config(layout="wide")  #to use the entire page width

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


# Ensure Kaleido is installed and available for image export
try:
    import kaleido
except ImportError:
    st.error("Kaleido is not installed. Please install it using 'pip install kaleido'.")

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
This website generates annotated percentile charts of health indicators for the United States and its territories. Data for these charts 
has been compiled by the [County Health Rankings (CHR) project](https://www.countyhealthrankings.org/health-data/methodology-and-sources/data-documentation), a service of the University of Wisconsin's Population Health Institute.
The CHR project maintains data on its website on various health indicators for each of the U.S's 3000+ counties and independent cities, dating to 2010
            
This site provides interactive charts based on County Health Rankings (CHR) indicators for user-selected counties and states. Users can select a specific 
indicator and year to generate the charts. Counties and states are displayed as color-coded dots on the charts. Two chart types are available: Percentile 
Chart and Time Series Chart. Additionally, users can download the charts in PNG format for local use.
            
This website allows users to save their filter selections and reuse them for future sessions. Once a specific county, state, indicator is chosen, 
users can save their filter settings, making it easy to quickly revisit the same charts without needing to reapply the filters each time. This feature 
enhances the user experience, ensuring that previously selected data views are readily accessible for ongoing analysis.
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

 #Function to reset multiselect state
def reset_multiselect(key):
    """
    Helper function to reset multiselect state and force re-render
    
    Args:
        key (str): Unique key for the multiselect component
    """
    if key in st.session_state:
        del st.session_state[key]

# Initialize session state variables if not already set
if 'selected_counties' not in st.session_state:
    st.session_state.selected_counties = []
if 'selected_attributes' not in st.session_state:
    st.session_state.selected_attributes = []


# Sidebar filters
st.sidebar.markdown('<div class="gold-header">Filters</div>', unsafe_allow_html=True)

# Year selection with auto-selection of the most recent year
selected_year = st.sidebar.selectbox(
    "Select Year",
    options=list(range(max_year, min_year - 1, -1)),
    index=0
)


# Function to save filters to session state and to a JSON file
def save_filters_to_json():
    filters = {
        'selected_counties': st.session_state.selected_counties,
        'selected_attributes': st.session_state.selected_attributes,
    }
    with open("filters.json", "w") as f:
        json.dump(filters, f)

# Sidebar - File upload option
uploaded_file = st.sidebar.file_uploader("Upload Saved Filters", type="json")

# Function to load the saved filters from the uploaded JSON file
def load_saved_filters(file):
    try:
        filters = json.load(file)
        return filters
    except Exception as e:
        st.error(f"Error loading filters: {e}")
        return None

# If a file is uploaded, update session state with the filter contents
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file
    saved_filters = load_saved_filters(uploaded_file)
    if saved_filters:
        # Apply the loaded filters to session state
        st.session_state.selected_counties = saved_filters.get('selected_counties', [])
        st.session_state.selected_attributes = saved_filters.get('selected_attributes', [])


# Add "Created by Muiz Memud" at the bottom of the the page
st.sidebar.markdown(
    """
    <div style="position: fixed; bottom: 0; width: 100%; text-align: center; font-size: 14px; color: #00053E;">
        <p>Developed by <b>Muiz Memud</b></p>
    </div>
    """,
    unsafe_allow_html=True
)

# Construct filename and load dataset
filename = f"chr{selected_year}.csv"
try:
    df = pd.read_csv(filename)
    st.write(f"Loaded data for year: {selected_year}")
except FileNotFoundError:
    st.error(f"Data file for year {selected_year} not found.")
    df = pd.DataFrame()

# Ensure the dataset has data before proceeding
if not df.empty:
    # Chart type selection
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Percentile Chart", "Line Chart"])

    # County selection
    if 'County' in df.columns:
        county_options = df['County'].unique()
        selected_counties = st.sidebar.multiselect(
            "Select County(ies)", 
            options=county_options, 
            default=st.session_state.selected_counties,     # Use saved counties if available
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

            # Combined save and download filters option
    download_filters_button = st.sidebar.download_button(
        label="Download Filters",
        data=json.dumps({
            'selected_year': selected_year,
            'selected_counties': st.session_state.selected_counties,
            'selected_attributes': st.session_state.selected_attributes,
        }),
        file_name="filters.json",
        mime="application/json",
        on_click=save_filters_to_json  # Call the save function when the button is clicked
    )

    # Function to save chart as an image
    def save_chart_as_image(fig):
        # Create an in-memory buffer to save the figure
        buf = io.BytesIO()
        fig.update_layout(template="plotly")  # Use default template for consistency
        fig.write_image(buf, format="png", engine="kaleido")
        buf.seek(0)
        return buf

    # Chart rendering
    if chart_type == "Percentile Chart":
        if not selected_counties:
            st.warning("Please select at least one county.")
        elif not selected_attributes:
            st.warning("Please select at least one attribute.")
        else:
            for attribute in selected_attributes:
                fig = go.Figure()

                attribute_values = df[attribute].dropna().values

                if len(attribute_values) == 0:
                    st.warning(f"No data available for the attribute: {attribute}")
                    continue

                percentiles = np.percentile(attribute_values, [0, 25, 50, 75, 100])

                for county in selected_counties:
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
                        range=[0, 100],  # Explicitly set the range of the x-axis to cover 0-100
                        tickvals=[0, 25, 50, 75, 100],  # Ensure these tick values appear on the axis
                        ticktext=["0", "25", "50", "75", "100"]  # Customize the tick labels (optional)
                    ),
                    showlegend=True,
                    template="plotly",  # Use Plotly's default color scheme
                )

                st.plotly_chart(fig)

                # Provide the option to download the chart
                image_buf = save_chart_as_image(fig)
                st.download_button(
                    label="Download Percentile Chart as Image",
                    data=image_buf,
                    file_name=f"{attribute}_percentile_chart.png",
                    mime="image/png"
                )

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