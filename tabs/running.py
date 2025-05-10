import streamlit as st
import pandas as pd
import altair as alt

def render(df):
    st.header("Running Analysis")
    run_df = df[df['Activity Type'] == 'Run'].copy()
    run_df['Moving Time'] /= 60
    run_df['Distance'] /= 1000
    run_df['Pace'] = (run_df['Moving Time'] / run_df['Distance']).round(2)
    run_df['Average Heart Rate'].fillna(run_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True)

    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        scatter = alt.Chart(run_df).mark_circle(size=60).encode(
            x=alt.X('Pace', title='Pace (min/km)'),
            y=alt.Y('Distance', title='Distance (Km)'),
            color=alt.Color('Average Heart Rate:Q', scale=alt.Scale(scheme='greens'), legend=None),
            tooltip=['Pace', 'Distance', 'Average Heart Rate', 'Activity Date']
        ).properties(title='Pace vs Distance', width=400, height=400).interactive()

        avg_df = pd.DataFrame({'Pace': [run_df['Pace'].mean()], 'Distance': [run_df['Distance'].mean()]})
        avg_point = alt.Chart(avg_df).mark_text(text='✖', fontSize=24, color='darkgreen').encode(
            x='Pace', y='Distance', tooltip=['Pace', 'Distance'])
        st.altair_chart(scatter + avg_point, use_container_width=True)

    with col2:
        hist = alt.Chart(run_df).mark_bar().encode(
            x=alt.X('Average Heart Rate:Q', bin=alt.Bin(maxbins=20)),
            y=alt.Y('count()'),
            color=alt.Color('Average Heart Rate:Q', bin=alt.Bin(maxbins=20), scale=alt.Scale(scheme='reds'), legend=None)
        ).properties(title='Heart Rate Distribution', width=400, height=400)
        st.altair_chart(hist, use_container_width=True)

    with col3:
        st.write("### Total Summary")
        st.write(f"Total Activities: {run_df.shape[0]}")
        st.write(f"Total Distance: {run_df['Distance'].sum():.2f} km")
        st.write(f"Total Time: {run_df['Moving Time'].sum():.2f} hours")
        st.write(f"Total Elevation: {run_df['Elevation Gain'].sum():.2f} m")
