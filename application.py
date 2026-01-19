import streamlit as st
import pandas as pd
import altair as alt
import os

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Bike Share Demand Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚴‍♀️ Bike Share Demand Analysis Dashboard")

# -----------------------------
# Load the CSV file (LOCAL FIX)
# -----------------------------
DATA_FILE = "train.csv"

if not os.path.exists(DATA_FILE):
    st.error(f"❌ File '{DATA_FILE}' not found. Please place it in the same folder as app.py.")
    st.stop()

train_df = pd.read_csv(DATA_FILE)

# -----------------------------
# Data Processing
# -----------------------------
train_df['datetime'] = pd.to_datetime(train_df['datetime'])

train_df['hour'] = train_df['datetime'].dt.hour
train_df['dayofweek'] = train_df['datetime'].dt.dayofweek
train_df['month'] = train_df['datetime'].dt.month
train_df['year'] = train_df['datetime'].dt.year

season_mapping = {
    1: 'Spring',
    2: 'Summer',
    3: 'Fall',
    4: 'Winter'
}

weather_mapping = {
    1: 'Clear',
    2: 'Misty',
    3: 'Light Snow/Rain',
    4: 'Heavy Snow/Rain'
}

train_df['season_name'] = train_df['season'].map(season_mapping)
train_df['weather_name'] = train_df['weather'].map(weather_mapping)

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("Dashboard Controls")

selected_season = st.sidebar.selectbox(
    "Select Season",
    ["All Seasons"] + list(season_mapping.values())
)

selected_weather = st.sidebar.selectbox(
    "Select Weather Condition",
    ["All Weather"] + list(weather_mapping.values())
)

include_holidays = st.sidebar.checkbox("Include Holidays", value=True)
include_workingdays = st.sidebar.checkbox("Include Working Days", value=True)

# -----------------------------
# Apply Filters
# -----------------------------
filtered_df = train_df.copy()

if selected_season != "All Seasons":
    filtered_df = filtered_df[filtered_df["season_name"] == selected_season]

if selected_weather != "All Weather":
    filtered_df = filtered_df[filtered_df["weather_name"] == selected_weather]

if not include_holidays:
    filtered_df = filtered_df[filtered_df["holiday"] == 0]

if not include_workingdays:
    filtered_df = filtered_df[filtered_df["workingday"] == 0]

# -----------------------------
# Visualizations
# -----------------------------
st.header("Visualizations")

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    # 1. Hourly Bike Rentals Over Time
    chart1 = alt.Chart(filtered_df).mark_line().encode(
        x=alt.X("datetime:T", title="Date and Time"),
        y=alt.Y("count:Q", title="Total Bike Rentals"),
        tooltip=["datetime:T", "count:Q"]
    ).properties(
        title="Hourly Bike Rentals Over Time"
    ).interactive()

    st.altair_chart(chart1, use_container_width=True)

    # 2. Average Rentals by Hour
    avg_hour = filtered_df.groupby("hour", as_index=False)["count"].mean()

    chart2 = alt.Chart(avg_hour).mark_bar().encode(
        x=alt.X("hour:O", title="Hour of Day"),
        y=alt.Y("count:Q", title="Average Bike Rentals"),
        tooltip=["hour:O", "count:Q"]
    ).properties(
        title="Average Bike Rentals by Hour of Day"
    )

    st.altair_chart(chart2, use_container_width=True)

    # 3. Average Rentals by Season
    season_order = list(season_mapping.values())
    avg_season = filtered_df.groupby("season_name", as_index=False)["count"].mean()
    avg_season["season_name"] = pd.Categorical(
        avg_season["season_name"],
        categories=season_order,
        ordered=True
    )

    chart3 = alt.Chart(avg_season).mark_bar().encode(
        x=alt.X("season_name:N", sort=season_order, title="Season"),
        y=alt.Y("count:Q", title="Average Bike Rentals"),
        tooltip=["season_name:N", "count:Q"]
    ).properties(
        title="Average Bike Rentals by Season"
    )

    st.altair_chart(chart3, use_container_width=True)

    # 4. Average Rentals by Weather
    weather_order = list(weather_mapping.values())
    avg_weather = filtered_df.groupby("weather_name", as_index=False)["count"].mean()
    avg_weather["weather_name"] = pd.Categorical(
        avg_weather["weather_name"],
        categories=weather_order,
        ordered=True
    )

    chart4 = alt.Chart(avg_weather).mark_bar().encode(
        x=alt.X("weather_name:N", sort=weather_order, title="Weather Condition"),
        y=alt.Y("count:Q", title="Average Bike Rentals"),
        tooltip=["weather_name:N", "count:Q"]
    ).properties(
        title="Average Bike Rentals by Weather Condition"
    )

    st.altair_chart(chart4, use_container_width=True)

    # 5. Rentals vs Temperature
    chart5 = alt.Chart(filtered_df).mark_point().encode(
        x=alt.X("temp:Q", title="Temperature (Celsius)"),
        y=alt.Y("count:Q", title="Total Bike Rentals"),
        tooltip=["temp:Q", "atemp:Q", "count:Q"]
    ).properties(
        title="Bike Rentals vs Temperature"
    ).interactive()

    st.altair_chart(chart5, use_container_width=True)
