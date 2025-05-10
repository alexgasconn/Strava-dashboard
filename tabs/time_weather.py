import streamlit as st
import altair as alt
import pandas as pd

def render(df):
    st.header("Time & Weather Analysis")

    if 'Hour' in df.columns:
        st.metric("Most Common Hour", f"{int(df['Hour'].mean())}:00")
    if 'DayOfWeek' in df.columns:
        dow_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        st.metric("Most Active Day", dow_map[df['DayOfWeek'].mode()[0]])
    if 'Weather Condition' in df.columns:
        st.metric("Most Frequent Weather", df['Weather Condition'].mode()[0])

    col1, col2 = st.columns(2)

    with col1:
        if 'Hour' in df.columns:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('Hour:O', title='Hour of Day'),
                y=alt.Y('count()', title='Number of Activities'),
                color=alt.Color('Activity Type:N', legend=None)
            ).properties(title='Activity Start Times', width=400, height=400)
            st.altair_chart(chart, use_container_width=True)

    with col2:
        if 'DayOfWeek' in df.columns:
            df['DayOfWeekStr'] = df['DayOfWeek'].map(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('DayOfWeekStr:N', title='Day of Week', sort=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']),
                y=alt.Y('count()', title='Number of Activities'),
                color=alt.Color('Activity Type:N', legend=None)
            ).properties(title='Activity Frequency by Day', width=400, height=400)
            st.altair_chart(chart, use_container_width=True)

    if 'Weather Condition' in df.columns:
        df['Weather Condition'] = df['Weather Condition'].map({
            1: '☀️ Clear', 2: '☁️ Cloudy', 3: '⛅ Partly Cloudy',
            4: '🌧️ Rainy', 5: '💨 Windy', 6: '❄️ Snowy'
        }).fillna('Unknown')
        weather_df = df[df['Weather Condition'].notnull()]
        chart = alt.Chart(weather_df).mark_bar().encode(
            x=alt.X('Weather Condition:N', title='Weather Condition'),
            y=alt.Y('count()', title='Number of Activities'),
            color=alt.Color('Weather Condition:N', legend=None)
        ).properties(title='Activities by Weather', width=600, height=400)
        st.altair_chart(chart, use_container_width=True)