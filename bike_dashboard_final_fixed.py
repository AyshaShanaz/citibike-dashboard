import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="NYC Citi Bike Dashboard",
    page_icon="🚴",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('202201-citibike-tripdata_1_sample.csv')
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 202201-citibike-tripdata_1_sample.csv is in the same directory.")
        return None

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", [
    "Intro", 
    "Daily Trends", 
    "Popular Stations", 
    "User Analysis",
    "Recommendations"
])

# Load data
df = load_data()

if df is not None:
    # Page: Intro
    if page == 'Intro':
        st.title('🚴 NYC Citi Bike Dashboard')
        st.markdown("""
        Welcome to the NYC Citi Bike Data Analysis Dashboard!
        
        This dashboard provides insights into bike sharing patterns using a sample of January 2022 data.
        
        **Dataset Overview:**
        """)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rides", f"{len(df):,}")
        with col2:
            st.metric("Unique Stations", f"{df['start_station_name'].nunique():,}")
        with col3:
            st.metric("Date Range", "January 2022")
        
        st.subheader("Data Preview")
        st.dataframe(df.head())
        
        st.subheader("Dataset Information")
        st.write(f"- **Shape:** {df.shape[0]} rows, {df.shape[1]} columns")
        st.write(f"- **Date Range:** {df['started_at'].min()} to {df['started_at'].max()}")

    # Page: Daily Trends
    elif page == 'Daily Trends':
        st.header('📈 Daily Ride Trends')
        
        # Prepare data
        df_temp = df.copy()
        df_temp['started_at'] = pd.to_datetime(df_temp['started_at'])
        df_temp['ended_at'] = pd.to_datetime(df_temp['ended_at'])
        df_temp['date'] = df_temp['started_at'].dt.date
        df_temp['ride_duration_min'] = (df_temp['ended_at'] - df_temp['started_at']).dt.total_seconds() / 60
        
        # Filter out extreme outliers
        df_filtered = df_temp[df_temp['ride_duration_min'].between(1, 120)]
        
        daily_stats = df_filtered.groupby('date').agg({
            'ride_id': 'count',
            'ride_duration_min': 'mean'
        }).reset_index()
        daily_stats.columns = ['date', 'daily_rides', 'avg_duration']
        
        st.subheader("Daily Ride Counts")
        st.line_chart(daily_stats.set_index('date')['daily_rides'])
        
        st.subheader("Average Daily Ride Duration (minutes)")
        st.line_chart(daily_stats.set_index('date')['avg_duration'])
        
        # Show summary stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Daily Rides", f"{daily_stats['daily_rides'].mean():.0f}")
            st.metric("Peak Day Rides", f"{daily_stats['daily_rides'].max():,}")
        with col2:
            st.metric("Average Ride Duration", f"{daily_stats['avg_duration'].mean():.1f} min")
            st.metric("Longest Avg Duration", f"{daily_stats['avg_duration'].max():.1f} min")

    # Page: Popular Stations
    elif page == 'Popular Stations':
        st.header('🚉 Most Popular Stations')
        
        # Top start stations
        top_start_stations = df['start_station_name'].value_counts().head(10)
        
        st.subheader("Top 10 Start Stations")
        st.bar_chart(top_start_stations)
        
        # Show as table too
        st.subheader("Station Details")
        station_df = pd.DataFrame({
            'Station Name': top_start_stations.index,
            'Number of Rides': top_start_stations.values
        })
        st.dataframe(station_df)
        
        # Top end stations
        st.subheader("Top 10 End Stations")
        top_end_stations = df['end_station_name'].value_counts().head(10)
        st.bar_chart(top_end_stations)

    # Page: User Analysis
    elif page == 'User Analysis':
        st.header('👥 User Analysis')
        
        # User type analysis
        st.subheader('User Type Distribution')
        user_type_counts = df['member_casual'].value_counts()
        
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(user_type_counts)
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
            st.bar_chart(bike_type_counts)
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
        df_filtered = df_temp[df_temp['ride_duration_min'].between(1, 60)]
        
        # Create histogram data properly for Streamlit
        hist_data = pd.cut(df_filtered['ride_duration_min'], bins=20).value_counts().sort_index()
        hist_df = hist_data.reset_index()
        hist_df.columns = ['Duration_Bin', 'Count']
        hist_df['Duration_Bin'] = hist_df['Duration_Bin'].astype(str)
        hist_df = hist_df.set_index('Duration_Bin')
        
        st.bar_chart(hist_df)
        
        avg_duration = df_filtered['ride_duration_min'].mean()
        median_duration = df_filtered['ride_duration_min'].median()
        st.write(f'Average ride duration: {avg_duration:.1f} minutes')
        st.write(f'Median ride duration: {median_duration:.1f} minutes')

    # Page: Recommendations
    elif page == 'Recommendations':
        st.header('💡 Recommendations')
        st.markdown("""
        Based on the analysis of the Citi Bike data sample, here are some recommendations for system improvements and further analysis:
        
        ### 🚀 Operational Improvements
        1. **Expand Capacity at Popular Stations:**
           - The most popular stations may need more docks and bikes, especially during peak hours.
        
        2. **Monitor Ride Duration Trends:**
           - Track changes in average ride duration to identify shifts in user behavior or potential issues.
        
        ### 📊 Business Strategy
        3. **Targeted Marketing for Casual Users:**
           - With members making up the majority of rides, consider campaigns to convert casual users to members.
        
        4. **Electric Bike Fleet Management:**
           - Electric bikes are a significant portion of rides. Ensure regular maintenance and consider expanding the electric fleet.
        
        ### 🗺️ Geographic Expansion
        5. **Network Expansion:**
           - Consider expanding the network in areas with high demand or underserved neighborhoods.
        
        ### 🔍 Further Analysis
        6. **Deep Dive Analysis:**
           - Analyze ride patterns by time of day, weather, and special events for deeper insights.
           - Study seasonal patterns across multiple months.
           - Investigate correlation between weather and ride duration/frequency.
        
        ---
        
        **Next Steps:**
        - Deploy this dashboard to Streamlit Cloud for easy sharing ✅
        - Continue to update the dashboard as new data becomes available
        - Solicit user feedback to improve the dashboard and data collection
        """)
        
        st.success("🎉 Dashboard successfully deployed! Share the link to showcase your analysis.")

else:
    st.error("Unable to load data. Please check that the CSV file is uploaded correctly.")
