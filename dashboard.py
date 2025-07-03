import pandas as pd
import streamlit as st
import plotly.express as px
import folium
import os
from folium import Map, PolyLine, Marker, Icon
from streamlit.components.v1 import html
# pyright: ignore[reportMissingImports]

# Load data
df = pd.read_csv(r'C:\Users\pooja\OneDrive\Pictures\Desktop\flight-forensics\crash_flight_simulated.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.dropna(subset=['latitude', 'longitude', 'altitude', 'speed'])
df = df.sort_values('timestamp')

# Anomaly detection function
def detect_anomalies(df):
    anomalies = []
    if df['vertical_speed'].min() < -4000:
        anomalies.append("Rapid Descent Detected")
    if df['altitude'].iloc[-1] < 100:
        anomalies.append("Potential Crash at Final Point")
    return anomalies

# Generate map.html
map_center = [df['latitude'].mean(), df['longitude'].mean()]
m = folium.Map(location=map_center, zoom_start=10)
flight_path = list(zip(df['latitude'], df['longitude']))
folium.PolyLine(flight_path, color="blue", weight=3).add_to(m)
crash_location = [df.iloc[-1]['latitude'], df.iloc[-1]['longitude']]
folium.Marker(crash_location, tooltip="Crash Site", icon=Icon(color="red")).add_to(m)

# Create the directory if it doesn't exist
os.makedirs("visualizations", exist_ok=True)

# Then save the map
m.save("visualizations/map.html")


# Streamlit UI
st.set_page_config(layout="wide")
st.title("\U0001F6E9 Flight Crash Forensics Visualizer")

# Line charts
st.subheader("Flight Telemetry")
st.line_chart(df.set_index('timestamp')[['altitude', 'speed', 'vertical_speed']])

# Load and show the map
st.subheader("Flight Path & Crash Site")
with open("visualizations/map.html", 'r', encoding='utf-8') as f:
    html(f.read(), height=600)

# Show anomalies
st.subheader("Detected Anomalies")
st.write(detect_anomalies(df))
# -----------------------------
# Section 5: Weather at Crash Site (Live Data)
# -----------------------------
st.subheader("🌦️ Weather at Crash Site")

# OpenWeatherMap API
API_KEY = st.secrets["OPENWEATHER_API_KEY"]  # Use secrets.toml in production
crash_lat = df.iloc[-1]['latitude']
crash_lon = df.iloc[-1]['longitude']

def get_weather(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "weather": data["weather"][0]["description"].title(),
            "temperature": data["main"]["temp"],
            "wind_speed": data["wind"]["speed"],
            "humidity": data["main"]["humidity"]
        }
    else:
        return None

weather_data = get_weather(crash_lat, crash_lon, API_KEY)

if weather_data:
    st.success("Live Weather Retrieved:")
    st.write(f"**Condition**: {weather_data['weather']}")
    st.write(f"**Temperature**: {weather_data['temperature']} °C")
    st.write(f"**Wind Speed**: {weather_data['wind_speed']} m/s")
    st.write(f"**Humidity**: {weather_data['humidity']}%")
else:
    st.error("Failed to fetch weather data.")
