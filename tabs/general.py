import streamlit as st
import altair as alt
import pandas as pd

def render(df):
    st.subheader("General Overview")
    st.write("You can now modularize all the logic from the general section here.")
    # Paste code from your general tab here


    col1, col2 = st.columns([8, 6])
    with col1:
        time_view = st.radio("View by:", ["Month", "Week"], horizontal=True)
        if time_view == "Week":
            heatmap_data = df.groupby(['Year', 'Week', 'Activity Type'])[
                'Moving Time'].count().reset_index()
            title = "Total Activities per Week"
            x_label = "Week"
        elif time_view == "Month":
            heatmap_data = df.groupby(['Year', 'Month'])[
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

