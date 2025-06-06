import streamlit as st
import pandas as pd
import altair as alt

def render(df):
    st.header("General Overview")

    col1, col2 = st.columns([8, 6])

    # Heatmap month/week per year
    with col1:
        time_view = st.radio("View by:", ["Month", "Week"], horizontal=True, key="time_view")
        if time_view == "Week":
            heatmap_data = df.groupby(['Year', 'Week', 'Activity Type'])['Moving Time'].count().reset_index()
            title = "Total Activities per Week"
            x_label = "Week"
            x_axis = alt.X("Week:O", title=x_label)
        else:
            heatmap_data = df.groupby(['Year', 'Month'])['Moving Time'].count().reset_index()
            month_order = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                           7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            heatmap_data['Month'] = heatmap_data['Month'].map(month_order)
            heatmap_data['Month'] = pd.Categorical(heatmap_data['Month'], categories=month_order.values(), ordered=True)
            title = "Total Activities per Month"
            x_axis = alt.X("Month:O", title="Month", sort=list(month_order.values()))

        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x=x_axis,
            y=alt.Y("Year:O", title="Year"),
            color=alt.Color("Moving Time:Q", scale=alt.Scale(scheme="oranges"), legend=None),
            tooltip=["Year:O", time_view + ":O", "Moving Time:Q"]
        ).properties(
            title=title,
            width=600,
            height=400
        )
        st.altair_chart(heatmap, use_container_width=True)



    # Pie chart for activity types
    with col2:
        activity_type_counts = df['Activity Type'].value_counts().reset_index().head(4)
        activity_type_counts.columns = ['Activity Type', 'Count']
        pie_chart = alt.Chart(activity_type_counts).mark_arc(innerRadius=0).encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("Activity Type:N", legend=None, scale=alt.Scale(scheme="category10")),
            tooltip=["Activity Type:N", "Count:Q"]
        ).properties(
            width=400,
            height=400,
            title="Activity Types Distribution"
        )
        st.altair_chart(pie_chart, use_container_width=True)



    # Summary of activities
    sports = ['Ride', 'Run', 'Swim', 'Weight Training']
    filtered_df = df[df['Activity Type'].isin(sports)]
    aggregated_data = filtered_df.groupby('Activity Type').agg(
        Total_Distance=('Distance', 'sum'),
        Total_Time=('Moving Time', 'sum'),
        Count=('Activity Type', 'count'),
    ).reset_index()
    aggregated_data['Total_Distance'] = aggregated_data['Total_Distance'].round(0).astype(int) / 1000
    aggregated_data['Total_Hours'] = (aggregated_data['Total_Time'] / 3600).round(0).astype(int)

    summary_cols = st.columns(len(aggregated_data))
    for idx, row in aggregated_data.iterrows():
        with summary_cols[idx]:
            st.markdown(f"#### {row['Activity Type']}")
            st.write(f"**Total Distance:** {row['Total_Distance']} km")
            st.write(f"**Total Time:** {row['Total_Hours']} hours")
            st.write(f"**Total Activities:** {row['Count']}")



    # Activity Transitions Heatmap
    st.subheader("Activity Transitions")

    mode = st.radio("Transition Mode", ["Chronological", "Same Day (No Repeats)"], horizontal=True)
    
    if mode == "Chronological":
        df_sorted = df.sort_values("Activity Date").reset_index(drop=True)
        df_sorted['Current'] = df_sorted['Activity Type']
        df_sorted['Next'] = df_sorted['Activity Type'].shift(-1)
        df_transitions = df_sorted[:-1]
    else:
        df_day = df.copy()
        df_day['Date'] = df_day['Activity Date'].dt.date
        df_day = df_day.sort_values(['Date', 'Activity Date'])
        df_day = df_day.drop_duplicates(subset=['Date', 'Activity Type'])
        df_day['Next'] = df_day.groupby('Date')['Activity Type'].shift(-1)
        df_day['Current'] = df_day['Activity Type']
        df_transitions = df_day.dropna(subset=['Next'])
    
    transition_counts = df_transitions.groupby(['Current', 'Next']).size().reset_index(name='Count')
    
    heatmap = alt.Chart(transition_counts).mark_rect().encode(
        x=alt.X('Next:N', title='Next Activity'),
        y=alt.Y('Current:N', title='Current Activity'),
        color=alt.Color('Count:Q', scale=alt.Scale(scheme='blues')),
        tooltip=['Current', 'Next', 'Count']
    ).properties(
        width=500,
        height=400,
        title="Activity Transition Heatmap"
    )
    
    st.altair_chart(heatmap, use_container_width=True)



    st.subheader("📅 Activities per Day: Distribution & Means")
    col1, col2 = st.columns(2)

    # Histogram: Number of days with X activities
    with col1:
        daily_counts = df.groupby(df['Activity Date'].dt.date).size().reset_index(name='Activity Count')
        hist = alt.Chart(daily_counts).mark_bar().encode(
            x=alt.X('Activity Count:O', title='Number of Activities in a Day'),
            y=alt.Y('count():Q', title='Number of Days'),
            tooltip=['Activity Count:O', alt.Tooltip('count():Q', title='Number of Days')]
        ).properties(
            width=350,
            height=300,
            title="Histogram: Activities per Day"
        )
        st.altair_chart(hist, use_container_width=True)

    # Mean activities per day by month and year
    with col2:
        df['Year'] = df['Activity Date'].dt.year
        df['Month'] = df['Activity Date'].dt.month
        daily_counts['Year'] = pd.to_datetime(daily_counts['Activity Date']).dt.year
        daily_counts['Month'] = pd.to_datetime(daily_counts['Activity Date']).dt.month

        mean_by_month = daily_counts.groupby(['Year', 'Month'])['Activity Count'].mean().reset_index()
        month_order = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                       7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        mean_by_month['MonthName'] = mean_by_month['Month'].map(month_order)
        mean_by_month['MonthName'] = pd.Categorical(mean_by_month['MonthName'], categories=month_order.values(), ordered=True)

        mean_chart = alt.Chart(mean_by_month).mark_line(point=True).encode(
            x=alt.X('MonthName:N', sort=list(month_order.values()), title='Month'),
            y=alt.Y('Activity Count:Q', title='Mean Activities per Day'),
            color=alt.Color('Year:N', title='Year'),
            tooltip=['Year:N', 'MonthName:N', alt.Tooltip('Activity Count:Q', title='Mean per Day')]
        ).properties(
            width=350,
            height=300,
            title="Mean Activities/Day by Month"
        )
        st.altair_chart(mean_chart, use_container_width=True)

    # Mean activities per day by week (optional, below the row)
    st.subheader("📊 Mean Activities per Day (by Week)")
    daily_counts['Week'] = pd.to_datetime(daily_counts['Activity Date']).dt.isocalendar().week
    mean_by_week = daily_counts.groupby(['Year', 'Week'])['Activity Count'].mean().reset_index()

    week_chart = alt.Chart(mean_by_week).mark_line(point=True).encode(
        x=alt.X('Week:O', title='Week'),
        y=alt.Y('Activity Count:Q', title='Mean Activities per Day'),
        color=alt.Color('Year:N', title='Year'),
        tooltip=['Year:N', 'Week:O', alt.Tooltip('Activity Count:Q', title='Mean per Day')]
    ).properties(
        width=700,
        height=300,
        title="Mean Activities per Day by Week and Year"
    )
    st.altair_chart(week_chart, use_container_width=True)





    
    # Layout: 4 filters in a row
    col1, col2, col3, col4 = st.columns([3, 3, 3, 3])

    with col1:
        activity_options = ['All'] + \
            sorted(df['Activity Type'].unique())
        selected_activity = st.selectbox("Activity Type", activity_options)

    with col2:
        metric_option = st.radio("Metric", [
                                 "Moving Time", "Distance", "Activities"], horizontal=True, label_visibility="visible")

    with col3:
        time_level = st.radio("View", [
                              "Yearly (Monthly View)", "Monthly (Weekly View)"], horizontal=True, label_visibility="visible")

    # Apply activity filter
    if selected_activity != 'All':
        df_filtered = df[df['Activity Type']
                                    == selected_activity].copy()
    else:
        df_filtered = df.copy()

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




    # For each activity calculate a relative effort, and then compute a fitness (CTL), FATIGUE (ATL), and FORM (TSB) score for each activity


    # 1. Calculate Relative Effort (TSS-like) for each activity
    # We'll use a simple formula: Relative Effort = (Moving Time in hours) * (Intensity Factor)
    # If Intensity Factor is not available, use a proxy (e.g., normalized speed or set to 1)
    df['Moving Time Hours'] = df['Moving Time'] / 3600
    if 'Intensity Factor' in df.columns:
        df['Relative Effort'] = df['Moving Time Hours'] * df['Intensity Factor']
    else:
        df['Relative Effort'] = df['Moving Time Hours']  # fallback

    # 2. Compute CTL (Chronic Training Load), ATL (Acute Training Load), and TSB (Training Stress Balance)
    # Use exponentially weighted moving averages (EWMAs)
    CTL_DAYS = 42  # typical CTL time constant
    ATL_DAYS = 7   # typical ATL time constant

    df = df.sort_values('Activity Date')
    df['CTL'] = df['Relative Effort'].ewm(span=CTL_DAYS, adjust=False).mean()
    df['ATL'] = df['Relative Effort'].ewm(span=ATL_DAYS, adjust=False).mean()
    df['TSB'] = df['CTL'] - df['ATL']

    # Optionally, display a chart
    st.subheader("Fitness (CTL), Fatigue (ATL), and Form (TSB) Over Time")
    chart = alt.Chart(df).mark_line().encode(
        x=alt.X('Activity Date:T', title='Date'),
        y=alt.Y('value:Q', title='Score'),
        color=alt.Color('variable:N', title='Metric'),
        tooltip=['Activity Date:T', 'variable:N', 'value:Q']
    ).transform_fold(
        ['CTL', 'ATL', 'TSB'],
        as_=['variable', 'value']
    ).properties(
        width=700,
        height=350
    )
    st.altair_chart(chart, use_container_width=True)
