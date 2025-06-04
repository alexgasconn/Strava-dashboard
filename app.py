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
    if 'start_date' in df.columns:
        min_date = pd.to_datetime(df['start_date']).min().date()
        max_date = pd.to_datetime(df['start_date']).max().date()
        start, end = st.date_input(
            "Filter by date range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        if isinstance(start, pd.Timestamp): start = start.date()
        if isinstance(end, pd.Timestamp): end = end.date()
        mask = (pd.to_datetime(df['start_date']).dt.date >= start) & (pd.to_datetime(df['start_date']).dt.date <= end)
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
