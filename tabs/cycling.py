import streamlit as st
import pandas as pd
import altair as alt

def render(df):
    st.header("Cycling Analysis")
    bike_df = df[df['Activity Type'] == 'Ride'].copy()
    bike_df['Distance'] /= 1000
    bike_df['Moving Time'] /= 3600
    bike_df['Speed'] = (bike_df['Distance'] / bike_df['Moving Time']).round(2)
    bike_df['Elevation/km'] = (bike_df['Elevation Gain'] / bike_df['Distance']).round(2)
    bike_df['Dirt Distance'] = bike_df['Dirt Distance'].fillna(0) / 1000
    bike_df['Paved Distance'] = (bike_df['Distance'] - bike_df['Dirt Distance']).clip(lower=0)
    bike_df['Dirt Distance'] = bike_df['Dirt Distance'].clip(lower=0)
    bike_df['Average Heart Rate'].fillna(bike_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True)

    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        scatter = alt.Chart(bike_df).mark_circle(color='brown', size=60).encode(
            x=alt.X('Speed', title='Speed (km/h)'),
            y=alt.Y('Distance', title='Distance (Km)'),
            tooltip=['Speed', 'Distance', 'Average Heart Rate', 'Activity Date']
        ).properties(width=400, height=400).interactive()

        avg_df = pd.DataFrame({'Speed': [bike_df['Speed'].mean()], 'Distance': [bike_df['Distance'].mean()]})
        avg_point = alt.Chart(avg_df).mark_text(text='✖', fontSize=24, color='black').encode(
            x='Speed', y='Distance', tooltip=['Speed', 'Distance']
        )
        st.altair_chart(scatter + avg_point, use_container_width=True)

    with col2:
        hist = alt.Chart(bike_df).mark_bar().encode(
            x=alt.X('Average Heart Rate:Q', bin=alt.Bin(maxbins=20)),
            y=alt.Y('count()'),
            color=alt.Color('Average Heart Rate:Q', bin=alt.Bin(maxbins=20), scale=alt.Scale(scheme='reds'), legend=None)
        ).properties(title='Heart Rate Distribution', width=400, height=400)
        st.altair_chart(hist, use_container_width=True)

    with col3:
        st.write("### Total Summary")
        total_paved = bike_df['Paved Distance'].sum()
        total_dirt = bike_df['Dirt Distance'].sum()
        total_dist = bike_df['Distance'].sum()
        st.write(f"Total Activities: {bike_df.shape[0]}")
        st.write(f"Total Distance: {total_dist:.2f} km")
        st.write(f"Total Time: {bike_df['Moving Time'].sum():.2f} hours")
        st.write(f"Total Elevation: {bike_df['Elevation Gain'].sum():.2f} m")
        st.write(f"Paved: {total_paved:.2f} km ({(total_paved / total_dist) * 100:.1f}%)")
        st.write(f"Dirt: {total_dirt:.2f} km ({(total_dirt / total_dist) * 100:.1f}%)")