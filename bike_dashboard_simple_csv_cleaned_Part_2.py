import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load the sampled data
@st.cache_data
def load_data():
    df = pd.read_csv('202201-citibike-tripdata_1_sample.csv')
    return df

df = load_data()

# Sidebar for navigation
page = st.sidebar.selectbox(
    'Select a page:',
    [
        'Intro',
        'Dual-axis Line Chart',
        'Most Popular Stations',
        'Kepler.gl Map',
        'Additional Insights',
        'Recommendations'
    ]
)

# Page: Intro
if page == 'Intro':
    st.title('NYC Citi Bike Dashboard')
    st.markdown("""
    Welcome to the New York Citi Bike Dashboard! This dashboard provides insights into bike usage patterns, station popularity, and more, using a sample of Citi Bike trip data.
    
    Use the sidebar to navigate through the different analyses and visualizations.
    """)
    st.image('https://upload.wikimedia.org/wikipedia/commons/6/6d/Citi_Bike_logo.png', width=200)
    st.caption('Image source: Wikipedia')
    st.write('Here is a preview of the data:')
    st.dataframe(df.head())

# Page: Dual-axis Line Chart
if page == 'Dual-axis Line Chart':
    st.header('Daily Rides and Average Duration')
    st.markdown("""
    This chart shows the number of Citi Bike rides per day (left axis) and the average ride duration in minutes (right axis).
    Use this to spot trends in demand and trip length.
    """)
    import plotly.graph_objects as go
    daily_stats = df.copy()
    daily_stats['started_at'] = pd.to_datetime(daily_stats['started_at'])
    daily_stats['ended_at'] = pd.to_datetime(daily_stats['ended_at'])
    daily_stats['ride_duration_min'] = (daily_stats['ended_at'] - daily_stats['started_at']).dt.total_seconds() / 60
    daily_stats['date'] = daily_stats['started_at'].dt.date
    daily_stats = daily_stats.groupby('date').agg({
        'ride_id': 'count',
        'ride_duration_min': 'mean'
    }).rename(columns={'ride_id': 'num_rides', 'ride_duration_min': 'avg_duration_min'})
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_stats.index, y=daily_stats['num_rides'], name='Number of Rides', yaxis='y1'))
    fig.add_trace(go.Scatter(x=daily_stats.index, y=daily_stats['avg_duration_min'], name='Avg Duration (min)', yaxis='y2'))
    fig.update_layout(
        xaxis=dict(title='Date'),
        yaxis=dict(title='Number of Rides', side='left'),
        yaxis2=dict(title='Avg Duration (min)', overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    **Interpretation:**
    - Peaks in the blue line indicate days with high demand.
    - The orange line shows how long rides lasted on average.
    - Look for patterns, such as weekends or weather events, that might affect both metrics.
    """)

# Page: Most Popular Stations
if page == 'Most Popular Stations':
    st.header('Most Popular Start Stations')
    st.markdown("""
    This bar chart shows the top 10 most popular Citi Bike start stations based on the number of rides.
    These stations likely have high foot traffic and good accessibility.
    """)
    import plotly.express as px
    station_counts = df['start_station_name'].value_counts().head(10)
    fig = px.bar(
        x=station_counts.values,
        y=station_counts.index,
        orientation='h',
        labels={'x': 'Number of Rides', 'y': 'Station Name'},
        title='Top 10 Most Popular Start Stations'
    )
    fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    **Key Insights:**
    - These stations are likely in high-traffic areas like business districts or tourist spots.
    - Consider these locations for bike redistribution and maintenance priorities.
    - Popular stations may need more docking capacity during peak hours.
    """)
    st.subheader('Station Usage Statistics')
    st.dataframe(station_counts.reset_index().rename(columns={'index': 'Station Name', 'start_station_name': 'Number of Rides'}))

# Page: Kepler.gl Map
if page == 'Kepler.gl Map':
    st.header('Bike Station Locations Map')
    st.markdown("""
    This map shows the geographic distribution of Citi Bike start stations.
    Each point represents a station, with size indicating popularity.
    """)
    import plotly.express as px
    # Get unique start stations with their coordinates and ride counts
    station_data = df.groupby(['start_station_name', 'start_lat', 'start_lng']).size().reset_index(name='ride_count')
    station_data = station_data.dropna(subset=['start_lat', 'start_lng'])
    
    fig = px.scatter_mapbox(
        station_data,
        lat='start_lat',
        lon='start_lng',
        size='ride_count',
        hover_name='start_station_name',
        hover_data={'ride_count': True, 'start_lat': False, 'start_lng': False},
        mapbox_style='open-street-map',
        zoom=11,
        height=600,
        title='NYC Citi Bike Station Locations'
    )
    fig.update_layout(margin={'r': 0, 't': 50, 'l': 0, 'b': 0})
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    **Map Features:**
    - Larger circles indicate stations with more rides
    - Hover over points to see station names and ride counts
    - The map shows the concentration of stations in Manhattan and Brooklyn
    """)

# Page: Additional Insights
if page == 'Additional Insights':
    st.header('Additional Insights')
    
    # User type analysis
    st.subheader('User Type Distribution')
    user_type_counts = df['member_casual'].value_counts()
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = px.pie(
            values=user_type_counts.values,
            names=user_type_counts.index,
            title='Member vs Casual Users'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.metric('Total Members', f'{user_type_counts.get("member", 0):,}')
        st.metric('Total Casual Users', f'{user_type_counts.get("casual", 0):,}')
        member_pct = (user_type_counts.get("member", 0) / user_type_counts.sum()) * 100
        st.metric('Member Percentage', f'{member_pct:.1f}%')
    
    # Bike type analysis
    st.subheader('Bike Type Distribution')
    bike_type_counts = df['rideable_type'].value_counts()
    col3, col4 = st.columns(2)
    
    with col3:
        fig_bar = px.bar(
            x=bike_type_counts.index,
            y=bike_type_counts.values,
            title='Classic vs Electric Bikes',
            labels={'x': 'Bike Type', 'y': 'Number of Rides'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col4:
        st.metric('Classic Bike Rides', f'{bike_type_counts.get("classic_bike", 0):,}')
        st.metric('Electric Bike Rides', f'{bike_type_counts.get("electric_bike", 0):,}')
        electric_pct = (bike_type_counts.get("electric_bike", 0) / bike_type_counts.sum()) * 100
        st.metric('Electric Bike %', f'{electric_pct:.1f}%')
    
    # Ride duration analysis
    st.subheader('Ride Duration Analysis')
    df_temp = df.copy()
    df_temp['started_at'] = pd.to_datetime(df_temp['started_at'])
    df_temp['ended_at'] = pd.to_datetime(df_temp['ended_at'])
    df_temp['ride_duration_min'] = (df_temp['ended_at'] - df_temp['started_at']).dt.total_seconds() / 60
    # Filter out extreme outliers for better visualization
    df_filtered = df_temp[df_temp['ride_duration_min'].between(1, 60)]
    
    fig_hist = px.histogram(
        df_filtered,
        x='ride_duration_min',
        nbins=30,
        title='Distribution of Ride Durations (1-60 minutes)',
        labels={'x': 'Ride Duration (minutes)', 'y': 'Number of Rides'}
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    
    avg_duration = df_filtered['ride_duration_min'].mean()
    median_duration = df_filtered['ride_duration_min'].median()
    st.write(f'Average ride duration: {avg_duration:.1f} minutes')
    st.write(f'Median ride duration: {median_duration:.1f} minutes')

# Page: Recommendations
if page == 'Recommendations':
    st.header('Recommendations')
    st.markdown("""
    Based on the analysis of the Citi Bike data sample, here are some recommendations for system improvements and further analysis:
    
    1. **Expand Capacity at Popular Stations:**
       - The most popular stations (e.g., W 21 St & 6 Ave, E 17 St & Broadway) may need more docks and bikes, especially during peak hours.
    2. **Monitor Ride Duration Trends:**
       - Track changes in average ride duration to identify shifts in user behavior or potential issues (e.g., traffic, weather).
    3. **Targeted Marketing for Casual Users:**
       - With members making up the majority of rides, consider campaigns to convert casual users to members.
    4. **Electric Bike Maintenance:**
       - Electric bikes are a significant portion of rides. Ensure regular maintenance and consider expanding the electric fleet.
    5. **Geographic Expansion:**
       - Consider expanding the network in areas with high demand or underserved neighborhoods.
    6. **Further Analysis:**
       - Analyze ride patterns by time of day, weather, and special events for deeper insights.
    
    ---
    
    **Next Steps:**
    - Deploy this dashboard to Streamlit Cloud for easy sharing.
    - Continue to update the dashboard as new data becomes available.
    - Solicit user feedback to improve the dashboard and data collection.
    """)
    st.image('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80', caption='Citi Bike in NYC (Unsplash)', use_column_width=True)
