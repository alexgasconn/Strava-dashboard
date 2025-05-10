import streamlit as st
import pandas as pd
from utils import preprocess_data
from tabs import general, running, swimming, cycling, time_weather

st.set_page_config(page_title="Strava Triathlon Dashboard", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file, encoding='latin-1', on_bad_lines='skip')
        df = preprocess_data(df)
    else:
        st.stop()

# Navigation
tabs = {
    "🏃🚴🏊 General": general,
    "🏃 Running": running,
    "🏊 Swimming": swimming,
    "🚴 Cycling": cycling,
    "🕒⛅ Time & Weather": time_weather,
}
selected = st.radio("Select Tab", list(tabs.keys()), horizontal=True)
tabs[selected].render(df)
