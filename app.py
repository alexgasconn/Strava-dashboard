import streamlit as st
import pandas as pd
from utils import preprocess_data
from tabs import general, running, swimming, cycling, time_weather

st.set_page_config(page_title="Strava Triathlon Dashboard", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    use_example = st.checkbox("Use example file")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file, encoding='latin-1', on_bad_lines='skip')
    elif use_example:
        df = pd.read_csv("activities.csv", encoding='latin-1', on_bad_lines='skip')
    else:
        st.stop()

    df = preprocess_data(df)

    # Date filter
    if 'Activity Date' in df.columns:
        df['Activity Date'] = pd.to_datetime(df['Activity Date'], errors='coerce')
        df = df.dropna(subset=['Activity Date'])
    
        min_date = df['Activity Date'].min().date()
        max_date = df['Activity Date'].max().date()
    
        default_start = max(pd.to_datetime("2020-01-01").date(), min_date)  # evita que esté fuera de rango
        default_end = max_date
    
        start_date = st.date_input("Start date", min_value=min_date, max_value=max_date, value=default_start)
        end_date = st.date_input("End date", min_value=min_date, max_value=max_date, value=default_end)

    
        if start_date > end_date:
            st.warning("Start date must be before end date")
            st.stop()
    
        mask = (df['Activity Date'].dt.date >= start_date) & (df['Activity Date'].dt.date <= end_date)
        df = df.loc[mask]



# Tab navigation
tabs = {
    "🏃🚴🏊 General": general,
    "🏃 Running": running,
    "🏊 Swimming": swimming,
    "🚴 Cycling": cycling,
    "🕒⛅ Time & Weather": time_weather,
}

tab_labels = list(tabs.keys())
tab_objects = st.tabs(tab_labels)

for tab_obj, tab_label in zip(tab_objects, tab_labels):
    with tab_obj:
        tabs[tab_label].render(df)