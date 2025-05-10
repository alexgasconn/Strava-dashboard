import streamlit as st
import pandas as pd
import altair as alt

def render(df):
    st.header("Swimming Analysis")
    swim_df = df[df['Activity Type'] == 'Swim'].copy()
    swim_df['Moving Time'] /= 60
    swim_df['Distance'] /= 1000
    swim_df['Pace'] = (swim_df['Moving Time'] / (swim_df['Distance'] * 10)).round(2)
    swim_df['Average Heart Rate'].fillna(swim_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True)

    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        scatter = alt.Chart(swim_df).mark_circle(size=60).encode(
            x=alt.X('Pace', title='Pace (min/100m)'),
            y=alt.Y('Distance', title='Distance (Km)'),
            color=alt.Color('Average Heart Rate:Q', scale=alt.Scale(scheme='blues'), legend=None),
            tooltip=['Pace', 'Distance', 'Average Heart Rate', 'Activity Date']
        ).properties(title='Pace vs Distance', width=400, height=400).interactive()

        avg_df = pd.DataFrame({'Pace': [swim_df['Pace'].mean()], 'Distance': [swim_df['Distance'].mean()]})
        avg_point = alt.Chart(avg_df).mark_text(text='✖', fontSize=24, color='darkblue').encode(
            x='Pace', y='Distance', tooltip=['Pace', 'Distance'])
        st.altair_chart(scatter + avg_point, use_container_width=True)

    with col2:
        hist = alt.Chart(swim_df).mark_bar().encode(
            x=alt.X('Average Heart Rate:Q', bin=alt.Bin(maxbins=20)),
            y=alt.Y('count()'),
            color=alt.Color('Average Heart Rate:Q', bin=alt.Bin(maxbins=20), scale=alt.Scale(scheme='reds'), legend=None)
        ).properties(title='Heart Rate Distribution', width=400, height=400)
        st.altair_chart(hist, use_container_width=True)

    with col3:
        st.write("### Total Summary")
        st.write(f"Total Activities: {swim_df.shape[0]}")
        st.write(f"Total Distance: {swim_df['Distance'].sum():.2f} km")
        st.write(f"Total Time: {swim_df['Moving Time'].sum():.2f} hours")