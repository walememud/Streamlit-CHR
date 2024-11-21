import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# Title
st.title("COUNTY HEALTH RANKING DASHBOARD 🏥")

# Overview Section
st.subheader("Overview")
st.markdown("""
Welcome to the County Health Ranking Dashboard! Here, you can explore health indicators across different counties for various years. 
Use this tool to gain insights into health outcomes, social and economic factors, and access to care at the county level.
Discover percentile rankings, trends over time, and comparisons between different counties.
""")

# Key Highlights (Example: Replace with actual logic from your data)
st.subheader("Key Highlights 📊")
st.write("""
- **Top 5 Healthiest Counties (2023):** County A, County B, County C, County D, County E
- **Top 5 Counties Needing Improvement (2023):** County X, County Y, County Z, County W, County V
""")

# Recent Trends
st.subheader("Recent Trends 📈")
years = [2010, 2012, 2014, 2016, 2018, 2020, 2022]
Washington_County = [70, 72, 75, 80, 76, 78, 65]
Unicoi_County = [60, 65, 63, 72, 69, 72, 70]
Sullivan_County = [55, 58, 62, 64, 66, 70, 73]

# Interactive Plotly line chart
fig_trends = go.Figure()
fig_trends.add_trace(go.Scatter(x=years, y=Washington_County, mode='lines+markers',
                                name="Washington County", line=dict(color='blue')))
fig_trends.add_trace(go.Scatter(x=years, y=Unicoi_County, mode='lines+markers',
                                name="Unicoi County", line=dict(color='green', dash='dash')))
fig_trends.add_trace(go.Scatter(x=years, y=Sullivan_County, mode='lines+markers',
                                name="Sullivan County", line=dict(color='red', dash='dot')))
fig_trends.update_layout(title="Adult Obesity Trends (2010 - 2022)",
                         xaxis_title="Year", yaxis_title="Index", height=400)
st.plotly_chart(fig_trends)

# Sidebar for year and county selection
st.sidebar.markdown("### Filters")
@st.cache_data
def load_data(file_path):
    """Loads data from a CSV file."""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"File {file_path} not found.")
        return pd.DataFrame()

min_year = 2010
max_year = date.today().year
selected_year = st.sidebar.selectbox("Release Year", range(min_year, max_year + 1))

filename = f"chr{selected_year}.csv"
df = load_data(filename)

if not df.empty and 'County' in df.columns:
    county_options = df['County'].unique()
    selected_counties = st.sidebar.multiselect("Select County(ies)", options=county_options, default=county_options[:1])

    attribute_options = df.columns[2:]  # Assuming attributes start from 3rd column
    selected_attributes = st.sidebar.multiselect("Select Attribute(s)", options=attribute_options)

    # Filtered Data
    df_filtered = df[df['County'].isin(selected_counties)]

    # Percentile Distribution Charts
    st.subheader("Percentile Distribution 📊")
    if selected_attributes:
        for attribute in selected_attributes:
            fig_percentile = go.Figure()
            attribute_values = df_filtered[attribute].dropna().values

            if len(attribute_values) > 0:
                percentiles = np.percentile(attribute_values, [0, 25, 50, 75, 100])

                for county in selected_counties:
                    county_value = df_filtered[df_filtered['County'] == county][attribute].iloc[0]
                    county_percentile = (np.sum(attribute_values < county_value) / len(attribute_values)) * 100

                    fig_percentile.add_trace(go.Scatter(x=[county_percentile], y=[county_value],
                                                        mode='markers', name=f"{county} (Value: {county_value:.2f})",
                                                        marker=dict(size=10)))

                fig_percentile.update_layout(
                    title=f"Percentile Distribution for {attribute}",
                    xaxis_title="Percentile", yaxis_title="Value",
                    xaxis=dict(tickmode='array', tickvals=[0, 25, 50, 75, 100], ticktext=['0', '25', '50', '75', '100'])
                )
                st.plotly_chart(fig_percentile)
            else:
                st.warning(f"No data available for {attribute}.")
    else:
        st.warning("Please select at least one attribute.")
else:
    st.warning("No data available for the selected year.")
