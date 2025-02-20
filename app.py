import os
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import LinearRegression

# File paths
city_file_path = "AIR POLLUTION IN KIGALI FROM 2020 TO 2024.xlsx"
rural_file_path = "AIR POLLUTION IN RURAL FROM 2020 TO 2024.xlsx"

# Function to load and preprocess data
@st.cache_data
def load_and_preprocess(file_path):
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return None
    
    all_sheets = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
    data_frames = []
    
    for sheet_name, df in all_sheets.items():
        if 'Site' in df.columns and 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            data_frames.append(df)

    return pd.concat(data_frames, ignore_index=True) if data_frames else None

# Load datasets
city_data = load_and_preprocess(city_file_path)
rural_data = load_and_preprocess(rural_file_path)

if city_data is not None and rural_data is not None:
    all_data = pd.concat([city_data, rural_data], ignore_index=True)
else:
    st.stop()

# Extract unique site names
unique_sites = sorted(all_data['Site'].dropna().unique().tolist())

# Define pollutant thresholds
pollutant_thresholds = {
    'SO2': 40,
    'CO': 4,
    'PM10': 45,
    'NO2': 25,
    'O3': 100,
    'PM2.5': 15
}

# Function to filter data by year
def filter_data_by_year(year):
    return all_data[all_data['Date'].dt.year == year]

# Function to provide health advice
def provide_health_advice(pollutant, value):
    threshold = pollutant_thresholds.get(pollutant, 0)
    if value > threshold:
        return f"⚠️ WARNING: {pollutant} levels are HIGH ({value:.2f} µg/m³). Limit outdoor activities and wear a mask."
    return f"✅ {pollutant} levels are safe ({value:.2f} µg/m³). No major health risks."

# Function to check pollution data
def check_pollution_data(site, pollutant, year):
    filtered_data = filter_data_by_year(year)
    filtered_data = filtered_data[filtered_data['Site'] == site]
    
    if not filtered_data.empty:
        value = filtered_data[pollutant].mean()
        advice = provide_health_advice(pollutant, value)
        return f"📌 **Average {pollutant} level in {year}:** {value:.2f} µg/m³\n\n{advice}"
    return f"⚠️ No data found for {site} in {year}."

# Function to plot pollutant levels
def plot_pollutant_levels(site, pollutant, year):
    filtered_data = filter_data_by_year(year)
    filtered_data = filtered_data[filtered_data['Site'] == site]
    
    if filtered_data.empty:
        st.warning("⚠️ No data available for this site in the selected year.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(filtered_data['Date'], filtered_data[pollutant], label=pollutant, marker='o')
    plt.axhline(y=pollutant_thresholds[pollutant], color='r', linestyle='--', label='Threshold')
    plt.xlabel("Date")
    plt.ylabel(f"{pollutant} (µg/m³)")
    plt.title(f"{pollutant} Levels in {site} ({year})")
    plt.legend()
    plt.grid()
    st.pyplot(plt)

# Function to predict future pollution levels
def predict_pollutant_level(site, pollutant, year):
    filtered_data = filter_data_by_year(year)
    filtered_data = filtered_data[filtered_data['Site'] == site]
    
    if filtered_data.empty:
        return f"⚠️ No data available for {site} in {year}."

    filtered_data['Days'] = (filtered_data['Date'] - filtered_data['Date'].min()).dt.days
    X = filtered_data[['Days']]
    y = filtered_data[pollutant]

    model = LinearRegression()
    model.fit(X, y)

    future_days = (datetime(year, 12, 31) - filtered_data['Date'].min()).days
    predicted_value = model.predict(np.array([[future_days]]))[0]
    advice = provide_health_advice(pollutant, predicted_value)

    return f"🔮 **Predicted {pollutant} level for {year}:** {predicted_value:.2f} µg/m³\n\n{advice}"

# Streamlit UI
st.title("🌍 Air Pollution Monitoring System")

# Sidebar Inputs
st.sidebar.header("🔎 Select Parameters")
selected_site = st.sidebar.selectbox("Select Site", unique_sites)
selected_pollutant = st.sidebar.selectbox("Select Pollutant", list(pollutant_thresholds.keys()))
selected_year = st.sidebar.selectbox("Select Year", ["2020", "2021", "2022", "2023"], index=0)

# Check Pollution Data
st.subheader("📌 Pollution Data Summary")
if st.sidebar.button("Check Data"):
    result = check_pollution_data(selected_site, selected_pollutant, int(selected_year))
    st.info(result)

# Plot Pollution Data
st.subheader("📈 Pollutant Level Trend")
if st.sidebar.button("Generate Plot"):
    plot_pollutant_levels(selected_site, selected_pollutant, int(selected_year))

# Predict Future Pollution Levels
st.subheader("🔮 Future Pollution Prediction")
if st.sidebar.button("Predict Future Levels"):
    prediction_result = predict_pollutant_level(selected_site, selected_pollutant, int(selected_year))
    st.success(prediction_result)

# Run Streamlit
if __name__ == "__main__":
    st.write("Use the sidebar to interact with the app.")
