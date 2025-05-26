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


    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        scatter = alt.Chart(bike_df).mark_circle(color='brown', size=60).encode(
            x=alt.X('Speed', title='Speed (km/h)',
                    scale=alt.Scale(domain=[8, bike_df['Speed'].max() + 2])),
            y=alt.Y('Distance', title='Distance (Km)', scale=alt.Scale(
                domain=[0, bike_df['Distance'].max() + 5])),
            tooltip=['Speed', 'Distance',
                     'Average Heart Rate', 'Activity Date']
        ).properties(
            width=400,
            height=400
        ).interactive()

        avg_speed = bike_df['Speed'].mean()
        avg_distance = bike_df['Distance'].mean()
        avg_df = pd.DataFrame(
            {'Speed': [avg_speed], 'Distance': [avg_distance]})

        avg_point = alt.Chart(avg_df).mark_text(
            text='✖',  # Unicode "X" symbol
            fontSize=24,
            color='black'
        ).encode(
            x='Speed',
            y='Distance',
            tooltip=['Speed', 'Distance']
        ).properties(
            title='Average Speed and Distance',
            width=400,
            height=400
        ).interactive()

        chart = scatter + avg_point
        st.altair_chart(chart, use_container_width=True)

    with col2:
        hist = alt.Chart(bike_df).mark_bar().encode(
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
        total_activities = bike_df.shape[0]
        total_distance = bike_df['Distance'].sum()
        total_time = bike_df['Moving Time'].sum()
        total_elevation = bike_df['Elevation Gain'].sum()
        st.write(f"Total Activities: {total_activities}")
        st.write(f"Total Distance: {total_distance:.2f} km")
        st.write(f"Total Time: {total_time:.2f} hours")
        st.write(f"Total Elevation: {total_elevation:.2f} m")

        # Total paved and dirt distance with percentages
        total_paved_distance = bike_df['Paved Distance'].sum()
        total_dirt_distance = bike_df['Dirt Distance'].sum()
        total_distance = bike_df['Distance'].sum()
        paved_percentage = (total_paved_distance / total_distance) * 100
        dirt_percentage = (total_dirt_distance / total_distance) * 100
        st.write(
            f"Total Paved Distance: {total_paved_distance:.2f} km ({paved_percentage:.2f}%)")
        st.write(
            f"Total Dirt Distance: {total_dirt_distance:.2f} km ({dirt_percentage:.2f}%)")

    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        monthly_df = bike_df.groupby('YearMonth').agg({
            'Distance': 'sum',
            'Moving Time': 'sum'
        }).reset_index()

        monthly_df['YearMonth'] = monthly_df['YearMonth'].dt.to_timestamp()

        monthly_df['Cumulative Distance'] = monthly_df['Distance'].cumsum()
        monthly_df['Cumulative Time'] = monthly_df['Moving Time'].cumsum()

        area = alt.Chart(monthly_df).mark_area(
            color='brown',
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
        hist = alt.Chart(bike_df).mark_bar().encode(
            x=alt.X('Distance:Q', bin=alt.Bin(
                maxbins=20), title='Distance (Km)'),
            y=alt.Y('count()', title='Total Activities'),
            color=alt.Color('Distance:Q', bin=alt.Bin(maxbins=20),
                            scale=alt.Scale(scheme='browns'), title='Distance', legend=None)
        ).properties(
            title='Distance Distribution',
            width=400,
            height=400
        ).interactive()
        st.altair_chart(hist, use_container_width=True)

    with col3:
        # Top 3 longest rides and top 3 rides with most elevation
        top3_longest = bike_df.sort_values('Distance', ascending=False).head(3)
        top3_elevation = bike_df.sort_values(
            'Elevation Gain', ascending=False).head(3)

        st.markdown("### Top 3 Longest Rides")
        for idx, row in top3_longest.iterrows():
            st.write(
                f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Elevation Gain']:.0f} m elevation")

        st.markdown("### Top 3 Rides with Most Elevation")
        for idx, row in top3_elevation.iterrows():
            st.write(
                f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Elevation Gain']:.0f} m elevation")

    # Add week column
    bike_df['Week'] = bike_df['Activity Date'].dt.isocalendar().week
    bike_df['Year'] = bike_df['Activity Date'].dt.isocalendar().year
    bike_df['YearWeek'] = bike_df['Year'].astype(
        str) + '-W' + bike_df['Week'].astype(str)

    # Group by YearWeek and sum Distance
    weekly_df = bike_df.groupby(['YearWeek', 'Year', 'Week']).agg({
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
        color='brown',
        opacity=0.4
    ).encode(
        y=alt.Y('RollingMean:Q', title='Distance (km)')
    )

    line = base.mark_line(color='maroon').encode(
        y='RollingMean:Q'
    )

    scatter = base.mark_circle(color='maroon', opacity=0.2).encode(
        y='Distance:Q',
        tooltip=['Date:T', 'Distance:Q']
    )

    chart = (area + line + scatter).properties(
        title='Weekly Running Distance with Rolling Mean',
        width=500,
        height=400
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    st.dataframe(bike_df)

    # Number of km (and days/months/years) for column Activity Gear in bike_df

    gear_summary = bike_df.groupby('Activity Gear').agg(
        Total_Distance=('Distance', 'sum'),
        Total_Activities=('Activity Gear', 'count'),
        First_Use=('Activity Date', 'min'),
        Last_Use=('Activity Date', 'max')
    ).reset_index()

    gear_summary['Total_Distance'] = gear_summary['Total_Distance'].round(2)
    gear_summary['Duration'] = (
        gear_summary['Last_Use'] - gear_summary['First_Use']).dt.days

    st.markdown("### Activity Gear Summary")
    st.dataframe(gear_summary)


    # Gantt Diagram: Gear Usage by Year-Month
    if 'Activity Gear' in bike_df.columns:
        gantt_data = bike_df.groupby(['YearMonth', 'Activity Gear']).agg(
            Count=('Activity Gear', 'size'),
            Total_Distance=('Distance', 'sum')
        ).reset_index()
        gantt_data['YearMonth'] = gantt_data['YearMonth'].dt.to_timestamp()

        gantt_data['Cumulative Distance'] = gantt_data.groupby('Activity Gear')['Total_Distance'].cumsum()

        gantt_chart = alt.Chart(gantt_data).mark_rect().encode(
            x=alt.X('yearmonth(YearMonth):T', title='Year-Month', axis=alt.Axis(format='%b %Y'), 
                scale=alt.Scale(padding=0)),
            y=alt.Y('Activity Gear:N', title='Gear', scale=alt.Scale(padding=0)),
            color=alt.Color('Total_Distance:Q', scale=alt.Scale(scheme='greens'), title='Total Distance (km)'),
            tooltip=['yearmonth(YearMonth):T', 'Activity Gear:N', 'Total_Distance:Q', 'Cumulative Distance:Q']
        ).properties(
            width=800,
            height=300,
            title='Gear Usage by Year-Month (Square Style)'
        ).configure_view(
            stroke=None
        )

        st.altair_chart(gantt_chart, use_container_width=True)
    else:
        st.warning("Activity Gear data is not available in the dataset.")