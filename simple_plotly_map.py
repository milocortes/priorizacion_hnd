import plotly.express as px

# Sample data using ISO-3 country codes
data = {
    'Country_Code': ['USA', 'CAN', 'FRA', 'DEU', 'CHN', 'IND', 'BRA', 'AUS'],
    'Value': [85, 72, 65, 90, 88, 45, 60, 78],
    'Country_Name': ['United States', 'Canada', 'France', 'Germany', 'China', 'India', 'Brazil', 'Australia']
}
df = pd.DataFrame(data)

# Create the world map
fig = px.scatter_geo(
    df, 
    locations="Country_Code",       # Column containing ISO country codes
    color="Value",                  # Column determining the color scale
    hover_name="Country_Name",      # Column shown in bold at top of hover tooltip
    color_continuous_scale=px.colors.sequential.Plasma,
    title="Global Metrics World Map", 
    projection="natural earth", 
    size = "Value"
)

fig.update_layout(
    geo = dict(
        #showframe=False,
        showcoastlines=True,
        showcountries=True,

    )
)
fig.update_layout(height=600,width=800)

st.plotly_chart(fig, theme="streamlit", use_container_width=True)
