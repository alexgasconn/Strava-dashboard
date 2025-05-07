import streamlit as st
import pandas as pd
import altair as alt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


st.set_page_config(
    page_title="Strava Triathlon Dashboard",
    page_icon="🏃🚴🏊🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            activities_df = pd.read_csv(
                uploaded_file, encoding='latin-1', on_bad_lines='skip')
            if activities_df.empty:
                st.error(
                    "The uploaded CSV file is empty. Please upload a valid file.")
                st.stop()  # Stop execution if the file is empty
        except Exception as e:
            st.error(f"An error occurred while reading the file: {e}")
            st.stop()  # Stop execution if there's an error reading the file
    else:
        st.warning("Please upload a CSV file to proceed.")
        st.stop()  # Stop execution if no file is uploaded

# FEATURE ENGINEERING
# Drop columns with all missing values
nan_cols = activities_df.columns[activities_df.isnull().all()]
activities_df.drop(nan_cols, axis=1, inplace=True)
activities_df = activities_df[activities_df['Activity Type'].isin(
    ['Ride', 'Run', 'Swim', 'Weight Training'])]

activities_df['Distance'] = activities_df['Distance.1']
activities_df.sort_values(by='Activity Date', inplace=True)

# Extract time-based features
activities_df['Activity Date'] = pd.to_datetime(activities_df['Activity Date'])
activities_df['Hour'] = activities_df['Activity Date'].dt.hour + 1
activities_df['Day'] = activities_df['Activity Date'].dt.day
activities_df['Week'] = activities_df['Activity Date'].dt.isocalendar().week
activities_df['Month'] = activities_df['Activity Date'].dt.month
activities_df['Year'] = activities_df['Activity Date'].dt.year
activities_df['YearMonth'] = activities_df['Activity Date'].dt.to_period('M')
activities_df["DayOfWeek"] = activities_df["Activity Date"].dt.dayofweek
activities_df['Quarter'] = activities_df['Activity Date'].dt.quarter
activities_df['IsWeekend'] = activities_df['Activity Date'].dt.dayofweek >= 5

# Rename some activity types
activities_df['Activity Type'] = activities_df['Activity Type'].replace(
    'Football (Soccer)', 'Football')
activities_df['Activity Type'] = activities_df['Activity Type'].replace(
    'Workout', 'Padel')


# Filter datasets for individual sports (if needed later)
run_df = activities_df[activities_df['Activity Type'] == 'Run']
swim_df = activities_df[activities_df['Activity Type'] == 'Swim']
bike_df = activities_df[activities_df['Activity Type'] == 'Ride']


if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = "General"


col1, col2 = st.columns([12, 3])
with col1:
    st.markdown(
        """
    <style>
    /* Target all Streamlit buttons */
    div.stButton > button {
        width: 200px;      /* Wider buttons */
        font-size: 2rem;   /* Bigger icon size */
        height: 50px;      /* Fixed height */
    }
    </style>
    """,
        unsafe_allow_html=True
    )

    cols_nav = st.columns(5)
    if cols_nav[0].button("🏃🚴🏊"):
        st.session_state.selected_tab = "General"
    if cols_nav[1].button("🏃"):
        st.session_state.selected_tab = "Running"
    if cols_nav[2].button("🏊"):
        st.session_state.selected_tab = "Swimming"
    if cols_nav[3].button("🚴"):
        st.session_state.selected_tab = "Cycling"
    if cols_nav[4].button("🕒⛅"):
        st.session_state.selected_tab = "Time & Weather"

    selected_tab = st.session_state.selected_tab

with col2:
    col_from, col_to = st.columns(2)

    with col_from:
        start_date = st.date_input(
            "From", activities_df['Activity Date'].min().date())

    with col_to:
        end_date = st.date_input(
            "To", activities_df['Activity Date'].max().date())

    activities_df = activities_df[
        (activities_df['Activity Date'] >= pd.to_datetime(start_date)) &
        (activities_df['Activity Date'] <= pd.to_datetime(end_date))
    ]


######################### GENERAL TAB #########################
if selected_tab == 'General':

    col1, col2 = st.columns([8, 6])
    with col1:
        time_view = st.radio("View by:", ["Month", "Week"], horizontal=True)
        if time_view == "Week":
            heatmap_data = activities_df.groupby(['Year', 'Week', 'Activity Type'])[
                'Moving Time'].count().reset_index()
            title = "Total Activities per Week"
            x_label = "Week"
        elif time_view == "Month":
            heatmap_data = activities_df.groupby(['Year', 'Month'])[
                'Moving Time'].count().reset_index()
            heatmap_data["Month"] = heatmap_data["Month"].astype(int)
            month_order = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                           7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            heatmap_data["Month"] = heatmap_data["Month"].map(month_order)
            month_categories = list(month_order.values())
            heatmap_data["Month"] = pd.Categorical(
                heatmap_data["Month"], categories=month_categories, ordered=True)
            title = "Total Activities per Month"
            x_label = "Month"
        if time_view == "Month":
            x_axis = alt.X("Month:O", title=x_label, sort=month_categories)
        else:
            x_axis = alt.X("Week:O", title=x_label)
        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x=x_axis,
            y=alt.Y("Year:O", title="Year"),
            color=alt.Color("Moving Time:Q", scale=alt.Scale(scheme="oran"
                                                             "ges"), legend=None),
            tooltip=[
                alt.Tooltip("Year:O"),
                alt.Tooltip(time_view + ":O"),
                alt.Tooltip("Moving Time:Q", title="Total Activities")
            ]
        ).properties(
            title=title,
            width=600,
            height=400
        )
        st.altair_chart(heatmap, use_container_width=True)

    with col2:
        # Prepare data
        activity_type_counts = activities_df['Activity Type'].value_counts(
        ).reset_index().head(4)
        activity_type_counts.columns = ['Activity Type', 'Count']
        # Create Altair Pie Chart
        pie_chart = alt.Chart(activity_type_counts).mark_arc(innerRadius=0).encode(
            theta=alt.Theta("Count:Q", title="Total Activities"),
            color=alt.Color("Activity Type:N", legend=None,
                            scale=alt.Scale(scheme="category10")),
            tooltip=[alt.Tooltip("Activity Type:N"), alt.Tooltip(
                "Count:Q", title="Total Activities")]
        ).properties(
            width=400,
            height=400,
            title="Activity Types Distribution"
        )
        st.altair_chart(pie_chart, use_container_width=True)

    # Second row: Summary Cards for Ride, Run, and Swim
    col_summary = st.columns(1)
    with col_summary[0]:
        sports = ['Ride', 'Run', 'Swim']
        filtered_df = activities_df[activities_df['Activity Type'].isin(
            sports)]
        aggregated_data = filtered_df.groupby('Activity Type').agg(
            Total_Distance=('Distance', 'sum'),
            Total_Time=('Moving Time', 'sum'),
            Count=('Activity Type', 'count'),
        ).reset_index()
        aggregated_data['Total_Distance'] = aggregated_data['Total_Distance'].round(
            0).astype(int) / 1000
        aggregated_data['Total_Hours'] = (
            aggregated_data['Total_Time'] / 3600).round(0).astype(int)
        summary_cols = st.columns(len(aggregated_data))
        for idx, row in aggregated_data.iterrows():
            with summary_cols[idx]:
                st.markdown(f"#### {row['Activity Type']}")
                st.write(f"**Total Distance:** {row['Total_Distance']} km")
                st.write(f"**Total Time:** {row['Total_Hours']} hours")
                st.write(f"**Total Activities:** {row['Count']}")

    # Layout: 4 filters in a row
    col1, col2, col3, col4 = st.columns([3, 3, 3, 3])

    with col1:
        activity_options = ['All'] + \
            sorted(activities_df['Activity Type'].unique())
        selected_activity = st.selectbox("Activity Type", activity_options)

    with col2:
        metric_option = st.radio("Metric", [
                                 "Moving Time", "Distance", "Activities"], horizontal=True, label_visibility="visible")

    with col3:
        time_level = st.radio("View", [
                              "Yearly (Monthly View)", "Monthly (Weekly View)"], horizontal=True, label_visibility="visible")

    # Apply activity filter
    if selected_activity != 'All':
        df_filtered = activities_df[activities_df['Activity Type']
                                    == selected_activity].copy()
    else:
        df_filtered = activities_df.copy()

    # Apply metric
    if metric_option == "Moving Time":
        df_filtered["Metric"] = df_filtered["Moving Time"] / \
            3600  # Convert to hours
        y_label = "Moving Time (hrs)"
    elif metric_option == "Distance":
        df_filtered["Metric"] = df_filtered["Distance"] / 1000  # Convert to km
        y_label = "Distance (km)"
    else:  # Activities
        df_filtered["Metric"] = 1  # Count activities
        y_label = "Number of Activities"

    with col4:
        if time_level == "Yearly (Monthly View)":
            year_options = sorted(df_filtered['Year'].unique(), reverse=True)
            selected_values = st.multiselect(
                "Year(s)", year_options, default=[year_options[0]])
        else:
            df_filtered['YearMonthStr'] = df_filtered['Activity Date'].dt.strftime(
                '%Y-%m')
            ym_options = sorted(
                df_filtered['YearMonthStr'].unique(), reverse=True)
            selected_values = st.multiselect(
                "Year-Month(s)", ym_options, default=[ym_options[0]])

    # Plot generation
    chart_data = pd.DataFrame()

    if time_level == "Yearly (Monthly View)":
        for year in selected_values:
            temp = df_filtered[df_filtered['Year'] == year].copy()
            monthly = temp.groupby('Month')['Metric'].sum().reset_index()
            monthly['Month'] = monthly['Month'].astype(int)
            monthly['MonthName'] = monthly['Month'].apply(lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][x - 1])
            monthly['Year'] = year
            monthly['CumulativeMetric'] = monthly['Metric'].cumsum()
            chart_data = pd.concat([chart_data, monthly])

        line = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('MonthName:N', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], title='Month'),
            y=alt.Y('CumulativeMetric:Q', title=f'Cumulative {y_label}'),
            color=alt.Color('Year:N'),
            tooltip=['Year:N', 'MonthName:N', alt.Tooltip(
                'CumulativeMetric:Q', title=f'Cumulative {y_label}')]
        )

        bars = alt.Chart(chart_data).mark_bar(opacity=0.8).encode(
            x=alt.X('MonthName:N', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], title='Month'),
            y=alt.Y('Metric:Q', title=f'{y_label}'),
            color=alt.Color('Year:N'),
            tooltip=['Year:N', 'MonthName:N', alt.Tooltip(
                'Metric:Q', title=f'{y_label}')]
        ).properties(
            width=40  # Ajusta el ancho de las barras para que sean colindantes
        )

        st.altair_chart((bars + line).properties(
            title=f'{y_label} by Month',
            width=600,
            height=400
        ), use_container_width=True)

    else:  # Monthly (Weekly View)
        for ym in selected_values:
            temp = df_filtered[df_filtered['YearMonthStr'] == ym].copy()
            temp['Day'] = temp['Activity Date'].dt.day
            daily = temp.groupby('Day')['Metric'].sum().reset_index()
            daily['YearMonth'] = ym
            daily['CumulativeMetric'] = daily['Metric'].cumsum()
            chart_data = pd.concat([chart_data, daily])

        line = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('Day:O', title='Day of Month', sort=list(range(1, 32))),
            y=alt.Y('CumulativeMetric:Q', title=f'Cumulative {y_label}'),
            color=alt.Color('YearMonth:N'),
            tooltip=['YearMonth:N', 'Day:O', alt.Tooltip(
                'CumulativeMetric:Q', title=f'Cumulative {y_label}')]
        )

        bars = alt.Chart(chart_data).mark_bar(opacity=0.8).encode(
            x=alt.X('Day:O', title='Day of Month', sort=list(range(1, 32))),
            y=alt.Y('Metric:Q', title=f'{y_label}'),
            color=alt.Color('YearMonth:N'),
            tooltip=['YearMonth:N', 'Day:O', alt.Tooltip(
                'Metric:Q', title=f'{y_label}')],
        ).properties(
            width=15  # Ajusta el ancho de las barras para que sean colindantes
        )

        st.altair_chart((bars + line).properties(
            title=f'{y_label} by Day',
            width=600,
            height=400
        ), use_container_width=True)


######################### RUNNING TAB #########################
elif selected_tab == 'Running':
    run_df = activities_df[activities_df['Activity Type'] == 'Run']
    run_df = run_df.copy()
    run_df['Moving Time'] = run_df['Moving Time'] / 60
    run_df['Distance'] = run_df['Distance'] / 1000
    run_df['Pace'] = (run_df['Moving Time'] / (run_df['Distance'])).round(2)
    st.write(run_df.head(10))

    run_df.sort_values('Pace', inplace=True)
    run_df['Average Heart Rate'].fillna(
        run_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True)

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

    # DISTANCE RECORDS
    st.markdown("### Distance Records")

    # Define distance categories and their margins
    distance_categories = {
        "1 Mile": 1.609,  # in km
        "5K": 5,
        "10K": 10,
        "Half Marathon": 21.0975,
        "Marathon": 42.195
    }
    margin_percentage = 0.075  # 7.5%

    # Create a container for each distance category
    for category, distance in distance_categories.items():
        margin = distance * margin_percentage
        lower_bound = distance - margin
        upper_bound = distance + margin

        # Filter runs within the margin
        filtered_runs = run_df[
            (run_df['Distance'] >= lower_bound) & (
                run_df['Distance'] <= upper_bound)
        ].copy()

        # Sort by pace (fastest first) and get the top 5
        filtered_runs.sort_values('Pace', inplace=True)
        top_5 = filtered_runs.head(5)

        # Display results
        st.markdown(f"#### {category}")
        if top_5.empty:
            st.write("No records found.")
        else:
            for idx, row in top_5.iterrows():
                st.write(
                    f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, "
                    f"{row['Pace']} min/km, {row['Moving Time']:.2f} min"
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

    # Weather conditions histogram
    if 'Weather Condition' in run_df.columns:
        weather_hist = alt.Chart(run_df).mark_bar().encode(
            x=alt.X('Weather Condition:N', title='Weather Condition'),
            y=alt.Y('count()', title='Total Activities'),
            color=alt.Color('Weather Condition:N', scale=alt.Scale(
                scheme='category20'), legend=None),
            tooltip=[alt.Tooltip('Weather Condition:N', title='Weather Condition'), alt.Tooltip(
                'count()', title='Total Activities')]
        ).properties(
            title='Weather Conditions Distribution',
            width=400,
            height=400
        )
        st.altair_chart(weather_hist, use_container_width=True)
    else:
        st.warning("Weather data is not available in the dataset.")

    # hours histogram
    if 'Hour' in run_df.columns:
        hour_hist = alt.Chart(run_df).mark_bar().encode(
            x=alt.X('Hour:O', title='Hour of Day'),
            y=alt.Y('count()', title='Total Activities'),
            color=alt.Color('Hour:O', scale=alt.Scale(
                scheme='category10'), legend=None),
            tooltip=[alt.Tooltip('Hour:O', title='Hour of Day'), alt.Tooltip(
                'count()', title='Total Activities')]
        ).properties(
            title='Activities by Hour of Day',
            width=400,
            height=400
        )
        st.altair_chart(hour_hist, use_container_width=True)


######################### SWIMMING TAB #########################
elif selected_tab == 'Swimming':
    swim_df = activities_df[activities_df['Activity Type'] == 'Swim']
    swim_df = swim_df.copy()

    swim_df['Moving Time'] = swim_df['Moving Time'] / 60
    swim_df['Distance'] = swim_df['Distance'] / 1000
    swim_df['Pace'] = (swim_df['Moving Time'] /
                       (swim_df['Distance'] * 10)).round(2)

    swim_df.sort_values('Pace', inplace=True)
    swim_df['Average Heart Rate'].fillna(
        swim_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True)

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


######################### CYCLING TAB #########################
elif selected_tab == 'Cycling':
    bike_df = activities_df[activities_df['Activity Type'] == 'Ride']
    bike_df = bike_df.copy()

    bike_df['Distance'] = bike_df['Distance'] / 1000
    bike_df['Moving Time'] = bike_df['Moving Time'] / 3600

    # Calculate speed in km/h
    bike_df['Speed'] = (bike_df['Distance'] / bike_df['Moving Time']).round(2)

    bike_df['Elevation/km'] = (bike_df['Elevation Gain'] /
                               bike_df['Distance']).round(2)

    bike_df['Dirt Distance'] = bike_df['Dirt Distance'].fillna(
        0)  # Fill NaN values with 0
    bike_df['Dirt Distance'] = bike_df['Dirt Distance'] / 1000  # Convert to km
    bike_df['Paved Distance'] = bike_df['Distance'] - bike_df['Dirt Distance']
    bike_df['Paved Distance'] = bike_df['Paved Distance'].clip(
        lower=0)  # Ensure no negative values
    bike_df['Dirt Distance'] = bike_df['Dirt Distance'].clip(
        lower=0)  # Ensure no negative values

    bike_df.sort_values('Speed', inplace=True)
    bike_df['Average Heart Rate'].fillna(
        bike_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True
    )

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


############################# TIME AND WEATHER TAB #########################
elif selected_tab == "Time & Weather":
    st.markdown("### Time and Weather Analysis 🕒⛅")
    st.info(
        "This section is still under construction, but already offers useful insights.")

    col1, col2, col3 = st.columns([4, 4, 4])
    with col1:
        if 'Hour' in activities_df.columns:
            avg_hour = int(activities_df['Hour'].mean())
            st.metric("Most Common Hour", f"{avg_hour}:00")
        if 'DayOfWeek' in activities_df.columns:
            dow_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            most_common_day = activities_df['DayOfWeek'].mode()[0]
            st.metric("Most Active Day", dow_map[most_common_day])
    with col2:
        if 'Weather Condition' in activities_df.columns:
            top_weather = activities_df['Weather Condition'].mode()[0]
            st.metric("Most Frequent Weather", top_weather)
    with col3:
        top_activity = activities_df['Activity Type'].mode()[0]
        st.metric("Top Activity", top_activity)

    st.markdown("---")

    # Distribution by Hour of Day
    col1, col2 = st.columns([6, 6])
    with col1:
        if 'Hour' in activities_df.columns:
            hour_chart = alt.Chart(activities_df).mark_bar().encode(
                x=alt.X('Hour:O', title='Hour of Day'),
                y=alt.Y('count()', title='Number of Activities'),
                color=alt.Color('Activity Type:N', legend=None),
                tooltip=['Hour:O', 'count()']
            ).properties(
                title='Activity Start Times',
                width=400,
                height=400
            ).interactive()
            st.altair_chart(hour_chart, use_container_width=True)
        else:
            st.warning("No hour data available.")

    with col2:
        # Day of Week distribution
        if 'DayOfWeek' in activities_df.columns:
            activities_df['DayOfWeekStr'] = activities_df['DayOfWeek'].map(
                lambda x: dow_map[x])
            dow_chart = alt.Chart(activities_df).mark_bar().encode(
                x=alt.X('DayOfWeekStr:N', title='Day of Week', sort=dow_map),
                y=alt.Y('count()', title='Number of Activities'),
                color=alt.Color('Activity Type:N', legend=None),
                tooltip=['DayOfWeekStr:N', 'count()']
            ).properties(
                title='Activity Frequency by Day',
                width=400,
                height=400
            ).interactive()
            st.altair_chart(dow_chart, use_container_width=True)

    # Heatmap: Month vs Weekday Number of Activities
    if 'Month' in activities_df.columns and 'DayOfWeek' in activities_df.columns:
        heatmap_data = activities_df.groupby(['Month', 'DayOfWeek']).size().reset_index(name='Count')
        heatmap_data['MonthStr'] = heatmap_data['Month'].map({
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        })
        dow_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        heatmap_data['DayOfWeekStr'] = heatmap_data['DayOfWeek'].map(lambda x: dow_map[x])
        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x=alt.X('MonthStr:N', title='Month', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
            y=alt.Y('DayOfWeekStr:N', title='Day of Week', sort=dow_map),
            color=alt.Color('Count:Q', scale=alt.Scale(scheme='greens'), title='Activity Count'),
            tooltip=['MonthStr', 'DayOfWeekStr', 'Count']
        ).properties(
            title='Heatmap: Month vs Weekday Number of Activities',
            width=600,
            height=400
        )
        st.altair_chart(heatmap, use_container_width=True)

        # Heatmap: Month vs Hour of Day
        if 'Month' in activities_df.columns and 'Hour' in activities_df.columns:
            heatmap_data = activities_df.groupby(['Month', 'Hour']).size().reset_index(name='Count')
            heatmap_data['MonthStr'] = heatmap_data['Month'].map({
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
            })
            heatmap = alt.Chart(heatmap_data).mark_rect().encode(
                x=alt.X('Hour:O', title='Hour of Day'),
                y=alt.Y('MonthStr:N', title='Month', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
                color=alt.Color('Count:Q', scale=alt.Scale(scheme='greens'), title='Activity Count'),
                tooltip=['MonthStr', 'Hour', 'Count']
            ).properties(
                title='Heatmap: Month vs Hour of Day',
                width=600,
                height=400
            )
            st.altair_chart(heatmap, use_container_width=True)

            # Favorite hour, day, month, and sport for the top 5 sports
            top_sports = activities_df['Activity Type'].value_counts().head(5).index.tolist()

            favorite_hour_day_month_sport = []
            for sport in top_sports:
                sport_df = activities_df[activities_df['Activity Type'] == sport]
                favorite_hour = sport_df['Hour'].mode()[0] if 'Hour' in sport_df.columns else None
                favorite_day = sport_df['DayOfWeek'].mode()[0] if 'DayOfWeek' in sport_df.columns else None
                favorite_month = sport_df['Month'].mode()[0] if 'Month' in sport_df.columns else None
                dow_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                             7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
                favorite_day_str = dow_map[favorite_day] if favorite_day is not None else None
                favorite_month_str = month_map[favorite_month] if favorite_month is not None else None
                favorite_hour_day_month_sport.append((sport, favorite_hour, favorite_day_str, favorite_month_str))

            st.markdown("### Favorite Hour, Day, and Month for Top 5 Sports")
            for sport, hour, day, month in favorite_hour_day_month_sport:
                st.write(f"**{sport}:** Favorite Hour: {hour}:00, Favorite Day: {day}, Favorite Month: {month}")
    
    # Additional Graphics for Weather and Time Sections

    # Hourly Activity Distribution by Weather Condition
    if 'Hour' in activities_df.columns and 'Weather Condition' in activities_df.columns:
        hourly_weather_data = activities_df.groupby(['Hour', 'Weather Condition']).size().reset_index(name='Count')
        hourly_weather_chart = alt.Chart(hourly_weather_data).mark_bar().encode(
            x=alt.X('Hour:O', title='Hour of Day'),
            y=alt.Y('Count:Q', title='Number of Activities'),
            color=alt.Color('Weather Condition:N', title='Weather Condition'),
            tooltip=['Hour:O', 'Weather Condition:N', 'Count:Q']
        ).properties(
            title='Hourly Activity Distribution by Weather Condition',
            width=600,
            height=400
        )
        st.altair_chart(hourly_weather_chart, use_container_width=True)

    # Monthly Average Temperature vs Activity Count
    if 'Month' in activities_df.columns and 'Weather Temperature' in activities_df.columns:
        monthly_activity_temp = activities_df.groupby('Month').agg(
            Activity_Count=('Activity Type', 'count'),
            Avg_Temperature=('Weather Temperature', 'mean')
        ).reset_index()
        monthly_activity_temp['MonthStr'] = monthly_activity_temp['Month'].map({
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        })

        activity_temp_chart = alt.Chart(monthly_activity_temp).mark_line(point=True).encode(
            x=alt.X('MonthStr:N', title='Month', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
            y=alt.Y('Activity_Count:Q', title='Activity Count'),
            color=alt.value('blue'),
            tooltip=['MonthStr', 'Activity_Count', 'Avg_Temperature']
        ).properties(
            title='Monthly Activity Count vs Average Temperature',
            width=600,
            height=400
        )

        temp_line = alt.Chart(monthly_activity_temp).mark_line(strokeDash=[5, 5], color='orange').encode(
            x=alt.X('MonthStr:N', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
            y=alt.Y('Avg_Temperature:Q', title='Average Temperature (°C)'),
            tooltip=['MonthStr', 'Avg_Temperature']
        )

        st.altair_chart(activity_temp_chart + temp_line, use_container_width=True)

    # Sunrise/Sunset Impact on Activities
    if 'Hour' in activities_df.columns and 'Weather Sunrise' in activities_df.columns:
        activities_df['Sunrise Impact'] = activities_df['Hour'] - pd.to_datetime(activities_df['Weather Sunrise']).dt.hour
        sunrise_impact_chart = alt.Chart(activities_df).mark_bar().encode(
            x=alt.X('Sunrise Impact:Q', bin=alt.Bin(maxbins=20), title='Hours from Sunrise'),
            y=alt.Y('count()', title='Number of Activities'),
            color=alt.Color('Activity Type:N', title='Activity Type'),
            tooltip=['Sunrise Impact:Q', 'count()']
        ).properties(
            title='Impact of Sunrise on Activity Start Times',
            width=600,
            height=400
        )
        st.altair_chart(sunrise_impact_chart, use_container_width=True)

    # Wind Speed vs Activity Count
    if 'Wind Speed' in activities_df.columns:
        wind_speed_data = activities_df.groupby(pd.cut(activities_df['Wind Speed'], bins=10)).size().reset_index(name='Count')
        wind_speed_data['Wind Speed Range'] = wind_speed_data['Wind Speed'].astype(str)
        wind_speed_chart = alt.Chart(wind_speed_data).mark_bar().encode(
            x=alt.X('Wind Speed Range:N', title='Wind Speed (km/h)'),
            y=alt.Y('Count:Q', title='Number of Activities'),
            color=alt.Color('Count:Q', scale=alt.Scale(scheme='blues'), legend=None),
            tooltip=['Wind Speed Range', 'Count']
        ).properties(
            title='Activity Count by Wind Speed',
            width=600,
            height=400
        )
        st.altair_chart(wind_speed_chart, use_container_width=True)
    # Advanced Weather Analysis: Temperature Impact on Performance
    if 'Weather Temperature' in activities_df.columns and 'Moving Time' in activities_df.columns:
        temp_performance_data = activities_df.groupby(pd.cut(activities_df['Weather Temperature'], bins=10)).agg(
            Avg_Moving_Time=('Moving Time', 'mean'),
            Avg_Distance=('Distance', 'mean')
        ).reset_index()
        temp_performance_data['Temperature Range'] = temp_performance_data['Weather Temperature'].astype(str)

        temp_performance_chart = alt.Chart(temp_performance_data).mark_bar().encode(
            x=alt.X('Temperature Range:N', title='Temperature Range (°C)'),
            y=alt.Y('Avg_Moving_Time:Q', title='Average Moving Time (s)'),
            color=alt.Color('Avg_Moving_Time:Q', scale=alt.Scale(scheme='reds'), legend=None),
            tooltip=['Temperature Range', 'Avg_Moving_Time', 'Avg_Distance']
        ).properties(
            title='Impact of Temperature on Moving Time',
            width=600,
            height=400
        )
        st.altair_chart(temp_performance_chart, use_container_width=True)
    if 'Weather Temperature' in activities_df.columns and 'Moving Time' in activities_df.columns:
        temp_performance_data = activities_df.groupby(pd.cut(activities_df['Weather Temperature'], bins=10)).agg(
            Avg_Moving_Time=('Moving Time', 'mean'),
            Avg_Distance=('Distance', 'mean')
        ).reset_index()
        temp_performance_data['Temperature Range'] = temp_performance_data['Weather Temperature'].astype(str)

        temp_performance_chart = alt.Chart(temp_performance_data).mark_bar().encode(
            x=alt.X('Temperature Range:N', title='Temperature Range (°C)'),
            y=alt.Y('Avg_Moving_Time:Q', title='Average Moving Time (s)'),
            color=alt.Color('Avg_Moving_Time:Q', scale=alt.Scale(scheme='reds'), legend=None),
            tooltip=['Temperature Range', 'Avg_Moving_Time', 'Avg_Distance']
        ).properties(
            title='Impact of Temperature on Moving Time',
            width=600,
            height=400
        )
        st.altair_chart(temp_performance_chart, use_container_width=True)

    # Correlation Matrix for Weather and Performance Metrics
    if {'Weather Temperature', 'Humidity', 'Wind Speed', 'Moving Time', 'Distance'}.issubset(activities_df.columns):
        correlation_data = activities_df[['Weather Temperature', 'Humidity', 'Wind Speed', 'Moving Time', 'Distance']].corr()
        correlation_chart = alt.Chart(correlation_data.reset_index().melt('index')).mark_rect().encode(
            x=alt.X('index:N', title='Metric'),
            y=alt.Y('variable:N', title='Metric'),
            color=alt.Color('value:Q', scale=alt.Scale(scheme='viridis'), title='Correlation'),
            tooltip=['index', 'variable', 'value']
        ).properties(
            title='Correlation Matrix: Weather and Performance Metrics',
            width=600,
            height=400
        )
        st.altair_chart(correlation_chart, use_container_width=True)


    # Weather Condition
    if 'Weather Condition' in activities_df.columns:
        col1, col2 = st.columns([6, 6])
        with col1:
            # Map weather condition codes to descriptive labels with emojis
            weather_map = {
                1: '☀️ Clear',
                2: '☁️ Cloudy',
                3: '⛅ Partly Cloudy',
                4: '🌧️ Rainy',
                5: '💨 Windy',
                6: '❄️ Snowy'
            }
            activities_df['Weather Condition'] = activities_df['Weather Condition'].map(
                weather_map)

            # Filter out NULL values
            weather_filtered_df = activities_df[activities_df['Weather Condition'].notnull(
            )]

            # Heatmap: Weather Condition by Month
            weather_filtered_df['MonthStr'] = weather_filtered_df['Month'].map({
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
            })
            weather_heatmap_data = weather_filtered_df.groupby(
                ['MonthStr', 'Weather Condition']).size().reset_index(name='Count')
            weather_heatmap = alt.Chart(weather_heatmap_data).mark_rect().encode(
                x=alt.X('MonthStr:N', title='Month', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
                y=alt.Y('Weather Condition:N', title='Weather Condition'),
                color=alt.Color('Count:Q', scale=alt.Scale(
                    scheme='reds'), title='Activity Count'),
                tooltip=['MonthStr', 'Weather Condition', 'Count']
            ).properties(
                title='Heatmap: Weather Condition by Month',
                width=600,
                height=400
            )
            st.altair_chart(weather_heatmap, use_container_width=True)
            weather_chart = alt.Chart(weather_filtered_df).mark_bar().encode(
                x=alt.X('Weather Condition:N', title='Weather'),
                y=alt.Y('count()', title='Number of Activities'),
                color=alt.Color('Weather Condition:N', legend=None),
                tooltip=['Weather Condition:N', 'count()']
            ).properties(
                title='Activities by Weather Condition 🌦️',
                width=400,
                height=400
            ).interactive()
            st.altair_chart(weather_chart, use_container_width=True)

    # Calculate monthly average temperature
    monthly_temp = activities_df.groupby('Month').agg(
        {'Weather Temperature': 'mean'}).reset_index()
    monthly_temp['MonthStr'] = monthly_temp['Month'].map({
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    })

    # Calculate monthly averages for temperature, humidity, and wind speed
    monthly_weather = activities_df.groupby('Month').agg({
        'Weather Temperature': 'mean',
        'Humidity': 'mean',
        'Wind Speed': 'mean'
    }).reset_index()

    monthly_weather['MonthStr'] = monthly_weather['Month'].map({
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    })

    # Create the base chart for temperature
    temp_chart = alt.Chart(monthly_weather).mark_bar(color='orange').encode(
        x=alt.X('MonthStr:N', title='Month', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        y=alt.Y('Weather Temperature:Q', title='Average Temperature (°C)'),
        tooltip=['MonthStr', 'Weather Temperature']
    )

    # Add a line for humidity as an area chart with low alpha
    humidity_chart = alt.Chart(monthly_weather).mark_area(color='blue', opacity=0.1).encode(
        x=alt.X('MonthStr:N', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        y=alt.Y('Humidity:Q', title='Humidity (%)'),
        tooltip=['MonthStr', 'Humidity']
    )

    # Add a line for wind speed
    wind_chart = alt.Chart(monthly_weather).mark_line(color='grey').encode(
        x=alt.X('MonthStr:N', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        y=alt.Y('Wind Speed:Q', title='Wind Speed (km/h)'),
        tooltip=['MonthStr', 'Wind Speed']
    )

    # Combine the charts
    combined_chart = alt.layer(temp_chart, humidity_chart, wind_chart).resolve_scale(
        y='independent'  # Allow independent y-axes for the metrics
    ).properties(
        title='Monthly Weather Metrics',
        width=600,
        height=400
    )

    st.altair_chart(combined_chart, use_container_width=True)
    # Heatmap Hour vs Day
    if 'Hour' in activities_df.columns and 'DayOfWeekStr' in activities_df.columns:
        heatmap_data = activities_df.groupby(
            ['DayOfWeekStr', 'Hour']).size().reset_index(name='Count')
        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x=alt.X('Hour:O', title='Hour'),
            y=alt.Y('DayOfWeekStr:N', title='Day of Week', sort=dow_map),
            color=alt.Color('Count:Q', scale=alt.Scale(
                scheme='blues'), title='Activity Count'),
            tooltip=['DayOfWeekStr', 'Hour', 'Count']
        ).properties(
            title='Heatmap: Hour vs Day of Week',
            width=600,
            height=400
        )
        st.altair_chart(heatmap, use_container_width=True)

    st.markdown("---")
    st.info("More advanced insights like temperature impact, sunrise time effects, and performance under rain will be added soon! 🚧")
