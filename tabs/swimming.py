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



    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        scatter = alt.Chart(swim_df).mark_circle(size=60).encode(
            x=alt.X('Pace', title='Pace (min/km)', scale=alt.Scale(
                domain=[swim_df['Pace'].min()-0.5, swim_df['Pace'].max()+0.5])),
            y=alt.Y('Distance', title='Distance (Km)', scale=alt.Scale(
                domain=[0, swim_df['Distance'].max()+1])),
            color=alt.Color('Average Heart Rate:Q', scale=alt.Scale(
                scheme='blues'), legend=None),
            tooltip=['Pace', 'Distance', 'Average Heart Rate', 'Activity Date']
        ).properties(
            title='Pace vs Distance',
            width=400,
            height=400
        ).interactive()

        avg_pace = swim_df['Pace'].mean()
        avg_distance = swim_df['Distance'].mean()
        avg_df = pd.DataFrame({'Pace': [avg_pace], 'Distance': [avg_distance]})

        avg_point = alt.Chart(avg_df).mark_text(
            text='✖',
            fontSize=24,
            color='darkblue'
        ).encode(
            x='Pace',
            y='Distance',
            tooltip=['Pace', 'Distance']
        )

        chart = scatter + avg_point
        st.altair_chart(chart, use_container_width=True)

    with col2:
        hist = alt.Chart(swim_df).mark_bar().encode(
            x=alt.X('Average Heart Rate:Q', bin=alt.Bin(
                maxbins=20), title='Heart Rate'),
            y=alt.Y('count()', title='Total Activities'),
            color=alt.Color('Average Heart Rate:Q', bin=alt.Bin(maxbins=20),
                            scale=alt.Scale(scheme='reds'), title='Heart Rate', legend=None)
        ).properties(
            title='Heart Rate Distribution',
            width=400,
            height=400
        )

        st.altair_chart(hist, use_container_width=True)

    with col3:
        st.write("### Total Summary")
        total_activities = swim_df.shape[0]
        total_distance = swim_df['Distance'].sum()
        total_time = swim_df['Moving Time'].sum()
        st.write(f"Total Activities: {total_activities}")
        st.write(f"Total Distance: {total_distance:.2f} km")
        st.write(f"Total Time: {total_time:.2f} hours")

    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        monthly_df = swim_df.groupby('YearMonth').agg({
            'Distance': 'sum',
            'Moving Time': 'sum'
        }).reset_index()

        monthly_df['YearMonth'] = monthly_df['YearMonth'].dt.to_timestamp()

        monthly_df['Cumulative Distance'] = monthly_df['Distance'].cumsum()
        monthly_df['Cumulative Time'] = monthly_df['Moving Time'].cumsum()

        area = alt.Chart(monthly_df).mark_area(
            color='lightblue',
            interpolate='monotone'
        ).encode(
            x=alt.X('YearMonth:T', axis=alt.Axis(title='Month', tickCount=5)),
            y='Cumulative Time'
        ).properties(
            title='Cumulative Time',
            width=400,
            height=400
        ).interactive()
        st.altair_chart(area, use_container_width=True)

    with col2:
        # distance histogram
        hist = alt.Chart(swim_df).mark_bar().encode(
            x=alt.X('Distance:Q', bin=alt.Bin(
                maxbins=20), title='Distance (Km)'),
            y=alt.Y('count()', title='Total Activities'),
            color=alt.Color('Distance:Q', bin=alt.Bin(maxbins=20),
                            scale=alt.Scale(scheme='blues'), title='Distance', legend=None)
        ).properties(
            title='Distance Distribution',
            width=400,
            height=400
        ).interactive()
        top3_longest = swim_df.sort_values('Distance', ascending=False).head(3)
        top3_fastest = swim_df.sort_values('Pace').head(3)

        st.markdown("### Top 3 Longest Swims")
        for idx, row in top3_longest.iterrows():
            st.write(
                f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Pace']:.2f} min/100m")

        st.markdown("### Top 3 Fastest Swims")
        for idx, row in top3_fastest.iterrows():
            st.write(
                f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Pace']:.2f} min/100m")

    # Add week column
    swim_df['Week'] = swim_df['Activity Date'].dt.isocalendar().week
    swim_df['Year'] = swim_df['Activity Date'].dt.isocalendar().year
    swim_df['YearWeek'] = swim_df['Year'].astype(
        str) + '-W' + swim_df['Week'].astype(str)

    # Group by YearWeek and sum Distance
    weekly_df = swim_df.groupby(['YearWeek', 'Year', 'Week']).agg({
        'Distance': 'sum'}).reset_index()

    # Sort to ensure correct rolling
    weekly_df = weekly_df.sort_values(['Year', 'Week'])

    # Rolling mean (3-week window)
    weekly_df['RollingMean'] = weekly_df['Distance'].rolling(
        window=3, min_periods=1).mean()

    # For x-axis, convert Year and Week into a datetime
    weekly_df['Date'] = pd.to_datetime(weekly_df['Year'].astype(
        str) + weekly_df['Week'].astype(str) + '1', format='%G%V%u')

    # Altair chart
    base = alt.Chart(weekly_df).encode(
        x=alt.X('Date:T', title='Week'),
    )

    area = base.mark_area(
        color='skyblue',
        opacity=0.4
    ).encode(
        y=alt.Y('RollingMean:Q', title='Distance (km)')
    )

    line = base.mark_line(color='blue').encode(
        y='RollingMean:Q'
    )

    scatter = base.mark_circle(color='blue', opacity=0.2).encode(
        y='Distance:Q',
        tooltip=['Date:T', 'Distance:Q']
    )

    chart = (area + line + scatter).properties(
        title='Weekly Running Distance with Rolling Mean',
        width=500,
        height=400
    ).interactive()

    st.altair_chart(chart, use_container_width=True)