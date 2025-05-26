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





    st.write(run_df.head(10))
    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        scatter = alt.Chart(run_df).mark_circle(size=60).encode(
            x=alt.X('Pace', title='Pace (min/km)',
                    scale=alt.Scale(domain=[run_df['Pace'].min()-1, run_df['Pace'].max()+1])),
            y=alt.Y('Distance', title='Distance (Km)', scale=alt.Scale(
                domain=[0, run_df['Distance'].max()+1])),
            color=alt.Color('Average Heart Rate:Q', scale=alt.Scale(
                scheme='greens'), legend=None),
            tooltip=['Pace', 'Distance', 'Average Heart Rate', 'Activity Date']
        ).properties(
            title='Pace vs Distance',
            width=400,
            height=400
        ).interactive()

        avg_pace = run_df['Pace'].mean()
        avg_distance = run_df['Distance'].mean()
        avg_df = pd.DataFrame({'Pace': [avg_pace], 'Distance': [avg_distance]})

        avg_point = alt.Chart(avg_df).mark_text(
            text='✖',
            fontSize=24,
            color='darkgreen'
        ).encode(
            x='Pace',
            y='Distance',
            tooltip=['Pace', 'Distance']
        )

        chart = scatter + avg_point
        st.altair_chart(chart, use_container_width=True)

    with col2:
        hist = alt.Chart(run_df).mark_bar().encode(
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
        total_activities = run_df.shape[0]
        total_distance = run_df['Distance'].sum()
        total_time = run_df['Moving Time'].sum()
        total_elevation = run_df['Elevation Gain'].sum()
        st.write(f"Total Activities: {total_activities}")
        st.write(f"Total Distance: {total_distance:.2f} km")
        st.write(f"Total Time: {total_time:.2f} hours")
        st.write(f"Total Elevation: {total_elevation:.2f} m")

    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        # Prepare monthly data
        monthly_df = run_df.groupby('YearMonth').agg({
            'Distance': 'sum',
            'Moving Time': 'sum'
        }).reset_index()

        monthly_df['YearMonth'] = monthly_df['YearMonth'].dt.to_timestamp()

        # Generate a complete date range to include months with 0 values
        full_date_range = pd.date_range(
            start=monthly_df['YearMonth'].min(),
            end=monthly_df['YearMonth'].max(),
            freq='MS'
        )
        monthly_df = monthly_df.set_index('YearMonth').reindex(
            full_date_range).fillna(0).reset_index()
        monthly_df.rename(columns={'index': 'YearMonth'}, inplace=True)

        # Calculate cumulative distance and time
        monthly_df['Cumulative Distance'] = monthly_df['Distance'].cumsum()
        monthly_df['Cumulative Time'] = monthly_df['Moving Time'].cumsum()

        # Calculate rolling mean (3-month window)
        monthly_df['RollingMean Distance'] = monthly_df['Distance'].rolling(
            window=3, min_periods=1).mean()
        monthly_df['RollingMean Time'] = monthly_df['Moving Time'].rolling(
            window=3, min_periods=1).mean()

        # Option to toggle between cumulative and rolling mean
        view_option = st.radio(
            "View Option:", ["Cumulative", "Rolling Mean"], horizontal=True)

        if view_option == "Cumulative":
            area = alt.Chart(monthly_df).mark_area(
                color='green',
                interpolate='monotone'
            ).encode(
                x=alt.X('YearMonth:T', axis=alt.Axis(
                    title='Month', tickCount=5)),
                y='Cumulative Time'
            ).properties(
                title='Cumulative Time',
                width=400,
                height=400
            ).interactive()
        else:
            area = alt.Chart(monthly_df).mark_area(
                color='blue',
                interpolate='monotone'
            ).encode(
                x=alt.X('YearMonth:T', axis=alt.Axis(
                    title='Month', tickCount=5)),
                y='RollingMean Time'
            ).properties(
                title='Rolling Mean Time (3-Month Window)',
                width=400,
                height=400
            ).interactive()

        st.altair_chart(area, use_container_width=True)

    with col2:
        # distance histogram
        hist = alt.Chart(run_df).mark_bar().encode(
            x=alt.X('Distance:Q', bin=alt.Bin(
                maxbins=20), title='Distance (Km)'),
            y=alt.Y('count()', title='Total Activities'),
            color=alt.Color('Distance:Q', bin=alt.Bin(maxbins=20),
                            scale=alt.Scale(scheme='greens'), title='Distance', legend=None)
        ).properties(
            title='Distance Distribution',
            width=400,
            height=400
        ).interactive()
        st.altair_chart(hist, use_container_width=True)

    with col3:
        # Top 3 longest runs and top 3 fastest runs
        top3_longest = run_df.sort_values('Distance', ascending=False).head(3)
        top3_fastest = run_df.sort_values('Pace').head(3)

        st.markdown("### Top 3 Longest Runs")
        for idx, row in top3_longest.iterrows():
            st.write(
                f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Pace']} min/km")

        st.markdown("### Top 3 Fastest Runs")
        for idx, row in top3_fastest.iterrows():
            st.write(
                f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Pace']} min/km")

    # Add week column
    run_df['Week'] = run_df['Activity Date'].dt.isocalendar().week
    run_df['Year'] = run_df['Activity Date'].dt.isocalendar().year
    run_df['YearWeek'] = run_df['Year'].astype(
        str) + '-W' + run_df['Week'].astype(str)

    # Group by YearWeek and sum Distance
    weekly_df = run_df.groupby(['YearWeek', 'Year', 'Week']).agg({
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
        color='green',
        opacity=0.4
    ).encode(
        y=alt.Y('RollingMean:Q', title='Distance (km)')
    )

    line = base.mark_line(color='darkgreen').encode(
        y='RollingMean:Q'
    )

    scatter = base.mark_circle(color='darkgreen', opacity=0.2).encode(
        y='Distance:Q',
        tooltip=['Date:T', 'Distance:Q']
    )

    chart = (area + line + scatter).properties(
        title='Weekly Running Distance with Rolling Mean',
        width=500,
        height=400
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    # Number of km (and days/months/years) for column Activity Gear in run_df

    gear_summary = run_df.groupby('Activity Gear').agg(
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
    if 'Activity Gear' in run_df.columns:
        gantt_data = run_df.groupby(['YearMonth', 'Activity Gear']).agg(
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


    col1, col2 = st.columns([6, 6])

    distance_categories = {
        "1 Mile": 1.609,
        "5K": 5,
        "10K": 10,
        "Half Marathon": 21.0975,
        "Marathon": 42.195
    }
    margin_percentage = 0.075

    def riegel_predictor(distance, time, target_distance):
        return time * (target_distance / distance) ** 1.06

    with col1:
        st.markdown("### 🏁 Top Real Performances")
    with col2:
        st.markdown("### 🔮 Riegel Predictions from Top 5")

    for category_name, base_dist in distance_categories.items():
        margin = base_dist * margin_percentage
        lower_bound = base_dist - margin
        upper_bound = base_dist + margin

        filtered = run_df[(run_df['Distance'] >= lower_bound) & (run_df['Distance'] <= upper_bound)].copy()
        filtered.sort_values('Pace', inplace=True)
        top_5 = filtered.head(5)

        if top_5.empty:
            continue

        with col1:
            st.markdown(f"#### {category_name}")
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            for i, (_, row) in enumerate(top_5.iterrows()):
                emoji = medals[i] if i < len(medals) else ""
                st.write(
                    f"{emoji} **{row['Activity Date'].date()}** — {row['Distance']:.2f} km, "
                    f"{row['Pace']} min/km, {row['Moving Time']:.2f} min"
                )

        with col2:
            st.markdown(f"#### From {category_name}")
            prediction_ranges = {}
            for _, row in top_5.iterrows():
                time = row['Moving Time']
                dist = row['Distance']
                for target_name, target_dist in distance_categories.items():
                    if target_name == category_name:
                        continue
                    pred_time = riegel_predictor(dist, time, target_dist)
                    prediction_ranges.setdefault(target_name, []).append(pred_time)

            for target_name, preds in prediction_ranges.items():
                min_pred = min(preds)
                max_pred = max(preds)
                avg_pred = sum(preds) / len(preds)
                st.write(
                    f"→ **{target_name}**: {avg_pred:.2f} min  _(range: {min_pred:.2f}–{max_pred:.2f})_"
                )



    
    col1, col2 = st.columns([6, 6])

    with col1:
        scatter = alt.Chart(run_df).mark_circle(size=60).encode(
            x=alt.X('Distance', title='Distance (Km)', scale=alt.Scale(
                domain=[0, run_df['Distance'].max() + 5])),
            y=alt.Y('Elevation Gain', title='Elevation Gain (m)', scale=alt.Scale(
                domain=[0, run_df['Elevation Gain'].max() + 50])),
            color=alt.Color('Average Heart Rate:Q', scale=alt.Scale(
                scheme='viridis'), legend=None),
            tooltip=['Distance', 'Elevation Gain',
                     'Average Heart Rate', 'Activity Date']
        ).properties(
            title='Distance vs Elevation Gain',
            width=400,
            height=400
        ).interactive()

        st.altair_chart(scatter, use_container_width=True)

    with col2:
        hist = alt.Chart(run_df).mark_bar().encode(
            x=alt.X('Elevation Gain:Q', bin=alt.Bin(
                maxbins=20), title='Elevation Gain (m)'),
            y=alt.Y('count()', title='Total Activities'),
            color=alt.Color('Elevation Gain:Q', bin=alt.Bin(maxbins=20),
                            scale=alt.Scale(scheme='plasma'), title='Elevation Gain', legend=None)
        ).properties(
            title='Elevation Gain Distribution',
            width=400,
            height=400
        ).interactive()

        st.altair_chart(hist, use_container_width=True)
