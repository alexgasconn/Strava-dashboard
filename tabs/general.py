import streamlit as st
import pandas as pd
import altair as alt

def render(df):
    st.header("General Overview")

    col1, col2 = st.columns([8, 6])
    with col1:
        time_view = st.radio("View by:", ["Month", "Week"], horizontal=True)
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

    sports = ['Ride', 'Run', 'Swim']
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
