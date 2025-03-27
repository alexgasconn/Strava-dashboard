import streamlit as st
import pandas as pd
import altair as alt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


st.set_page_config(
    page_title="Strava Training Dashboard",
    page_icon="🏃🚴🏊🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Load data
# activities_df = pd.read_csv(r'C:\Users\usuario\OneDrive\Escritorio\VS files\strava\activities.csv', encoding='latin-1', on_bad_lines='skip')


uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    activities_df = pd.read_csv(uploaded_file, encoding='latin-1', on_bad_lines='skip')
    st.write(activities_df)



## FEATURE ENGINEERING
# Drop columns with all missing values
nan_cols = activities_df.columns[activities_df.isnull().all()]
activities_df.drop(nan_cols, axis=1, inplace=True)
activities_df = activities_df[activities_df['Activity Type'].isin(['Ride', 'Run', 'Swim', 'Weight Training'])]

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
activities_df['Activity Type'] = activities_df['Activity Type'].replace('Football (Soccer)', 'Football')
activities_df['Activity Type'] = activities_df['Activity Type'].replace('Workout', 'Padel')


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

    cols_nav = st.columns(4)
    if cols_nav[0].button("🏃🚴🏊"):
        st.session_state.selected_tab = "General"
    if cols_nav[1].button("🏃"):
        st.session_state.selected_tab = "Running"
    if cols_nav[2].button("🏊"):
        st.session_state.selected_tab = "Swimming"
    if cols_nav[3].button("🚴"):
        st.session_state.selected_tab = "Cycling"

    selected_tab = st.session_state.selected_tab

with col2:
    col_from, col_to = st.columns(2)

    with col_from:
        start_date = st.date_input("From", activities_df['Activity Date'].min().date())

    with col_to:
        end_date = st.date_input("To", activities_df['Activity Date'].max().date())

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
            heatmap_data = activities_df.groupby(['Year', 'Week', 'Activity Type'])['Moving Time'].count().reset_index()
            title = "Total Activities per Week"
            x_label = "Week"
        elif time_view == "Month":
            heatmap_data = activities_df.groupby(['Year', 'Month'])['Moving Time'].count().reset_index()
            heatmap_data["Month"] = heatmap_data["Month"].astype(int)
            month_order = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                           7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            heatmap_data["Month"] = heatmap_data["Month"].map(month_order)
            month_categories = list(month_order.values())
            heatmap_data["Month"] = pd.Categorical(heatmap_data["Month"], categories=month_categories, ordered=True)
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
        activity_type_counts = activities_df['Activity Type'].value_counts().reset_index().head(4)
        activity_type_counts.columns = ['Activity Type', 'Count']
        # Create Altair Pie Chart
        pie_chart = alt.Chart(activity_type_counts).mark_arc(innerRadius=0).encode(
            theta=alt.Theta("Count:Q", title="Total Activities"),
            color=alt.Color("Activity Type:N", legend=None, scale=alt.Scale(scheme="category10")),
            tooltip=[alt.Tooltip("Activity Type:N"), alt.Tooltip("Count:Q", title="Total Activities")]
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
        filtered_df = activities_df[activities_df['Activity Type'].isin(sports)]
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





    # Layout: 4 filters in a row
    col1, col2, col3, col4 = st.columns([3, 3, 3, 3])

    with col1:
        activity_options = ['All'] + sorted(activities_df['Activity Type'].unique())
        selected_activity = st.selectbox("Activity Type", activity_options)

    with col2:
        metric_option = st.radio("Metric", ["Moving Time", "Distance"], horizontal=True, label_visibility="visible")

    with col3:
        time_level = st.radio("View", ["Yearly (Monthly View)", "Monthly (Weekly View)"], horizontal=True, label_visibility="visible")

    # Apply activity filter
    if selected_activity != 'All':
        df_filtered = activities_df[activities_df['Activity Type'] == selected_activity].copy()
    else:
        df_filtered = activities_df.copy()

    # Apply metric
    if metric_option == "Moving Time":
        df_filtered["Metric"] = df_filtered["Moving Time"] / 3600  # Convert to hours
        y_label = "Cumulative Moving Time (hrs)"
    else:
        df_filtered["Metric"] = df_filtered["Distance"] / 1000  # Convert to km
        y_label = "Cumulative Distance (km)"

    with col4:
        if time_level == "Yearly (Monthly View)":
            year_options = sorted(df_filtered['Year'].unique(), reverse=True)
            selected_values = st.multiselect("Year(s)", year_options, default=[year_options[0]])
        else:
            df_filtered['YearMonthStr'] = df_filtered['Activity Date'].dt.strftime('%Y-%m')
            ym_options = sorted(df_filtered['YearMonthStr'].unique(), reverse=True)
            selected_values = st.multiselect("Year-Month(s)", ym_options, default=[ym_options[0]])

    # Plot generation
    chart_data = pd.DataFrame()

    if time_level == "Yearly (Monthly View)":
        for year in selected_values:
            temp = df_filtered[df_filtered['Year'] == year].copy()
            monthly = temp.groupby('Month')['Metric'].sum().cumsum().reset_index()
            monthly['Month'] = monthly['Month'].astype(int)
            monthly['MonthName'] = monthly['Month'].apply(lambda x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][x - 1])
            monthly['Year'] = year
            chart_data = pd.concat([chart_data, monthly])

        line = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('MonthName:N', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], title='Month'),
            y=alt.Y('Metric:Q', title=y_label),
            color=alt.Color('Year:N'),
            tooltip=['Year:N', 'MonthName:N', alt.Tooltip('Metric:Q', title=y_label)]
        ).properties(
            title=f'{y_label} by Month',
            width=600,
            height=400
        )
        st.altair_chart(line, use_container_width=True)

    else:  # Monthly (Daily View)
        for ym in selected_values:
            temp = df_filtered[df_filtered['YearMonthStr'] == ym].copy()
            temp['Day'] = temp['Activity Date'].dt.day
            daily = temp.groupby('Day')['Metric'].sum().cumsum().reset_index()
            daily['YearMonth'] = ym
            chart_data = pd.concat([chart_data, daily])

        line = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('Day:O', title='Day of Month', sort=list(range(1, 32))),
            y=alt.Y('Metric:Q', title=y_label),
            color=alt.Color('YearMonth:N'),
            tooltip=['YearMonth:N', 'Day:O', alt.Tooltip('Metric:Q', title=y_label)]
        ).properties(
            title=f'{y_label} by Day',
            width=600,
            height=400
        )
        st.altair_chart(line, use_container_width=True)


######################### RUNNING TAB #########################
elif selected_tab == 'Running':
    run_df = activities_df[activities_df['Activity Type'] == 'Run']
    run_df = run_df.copy()
    run_df['Moving Time'] = run_df['Moving Time'] / 60
    run_df['Distance'] = run_df['Distance'] / 1000
    run_df['Pace'] = (run_df['Moving Time'] / (run_df['Distance'])).round(2)

    run_df.sort_values('Pace', inplace=True)
    run_df['Average Heart Rate'].fillna(run_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True)
    
    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        scatter = alt.Chart(run_df).mark_circle(size=60).encode(
            x=alt.X('Pace', title='Pace (min/km)', scale=alt.Scale(domain=[run_df['Pace'].min()-1, run_df['Pace'].max()+1])),
            y=alt.Y('Distance', title='Distance (Km)', scale=alt.Scale(domain=[0, run_df['Distance'].max()+1])),
            color=alt.Color('Average Heart Rate:Q', scale=alt.Scale(scheme='greens'), legend=None),
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
        x=alt.X('Average Heart Rate:Q', bin=alt.Bin(maxbins=20), title='Heart Rate'),
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
        monthly_df = run_df.groupby('YearMonth').agg({
            'Distance': 'sum',
            'Moving Time': 'sum'
        }).reset_index()

        monthly_df['YearMonth'] = monthly_df['YearMonth'].dt.to_timestamp()

        monthly_df['Cumulative Distance'] = monthly_df['Distance'].cumsum()
        monthly_df['Cumulative Time'] = monthly_df['Moving Time'].cumsum()

        area = alt.Chart(monthly_df).mark_area(
            color='green',
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
        #distance histogram
        hist = alt.Chart(run_df).mark_bar().encode(
            x=alt.X('Distance:Q', bin=alt.Bin(maxbins=20), title='Distance (Km)'),
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
            st.write(f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Pace']} min/km")
        
        st.markdown("### Top 3 Fastest Runs")
        for idx, row in top3_fastest.iterrows():
            st.write(f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Pace']} min/km")




    
    # Add week column
    run_df['Week'] = run_df['Activity Date'].dt.isocalendar().week
    run_df['Year'] = run_df['Activity Date'].dt.isocalendar().year
    run_df['YearWeek'] = run_df['Year'].astype(str) + '-W' + run_df['Week'].astype(str)

    # Group by YearWeek and sum Distance
    weekly_df = run_df.groupby(['YearWeek', 'Year', 'Week']).agg({'Distance': 'sum'}).reset_index()

    # Sort to ensure correct rolling
    weekly_df = weekly_df.sort_values(['Year', 'Week'])

    # Rolling mean (3-week window)
    weekly_df['RollingMean'] = weekly_df['Distance'].rolling(window=3, min_periods=1).mean()

    # For x-axis, convert Year and Week into a datetime
    weekly_df['Date'] = pd.to_datetime(weekly_df['Year'].astype(str) + weekly_df['Week'].astype(str) + '1', format='%G%V%u')

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


######################### SWIMMING TAB #########################
elif selected_tab == 'Swimming':
    swim_df = activities_df[activities_df['Activity Type'] == 'Swim']
    swim_df = swim_df.copy()
    
    swim_df['Moving Time'] = swim_df['Moving Time'] / 60
    swim_df['Distance'] = swim_df['Distance'] / 1000
    swim_df['Pace'] = (swim_df['Moving Time'] / (swim_df['Distance'] *10)).round(2)

    swim_df.sort_values('Pace', inplace=True)
    swim_df['Average Heart Rate'].fillna(swim_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True)
    
    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        scatter = alt.Chart(swim_df).mark_circle(size=60).encode(
            x=alt.X('Pace', title='Pace (min/km)', scale=alt.Scale(domain=[swim_df['Pace'].min()-0.5, swim_df['Pace'].max()+0.5])),
            y=alt.Y('Distance', title='Distance (Km)', scale=alt.Scale(domain=[0, swim_df['Distance'].max()+1])),
            color=alt.Color('Average Heart Rate:Q', scale=alt.Scale(scheme='blues'), legend=None),
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
        x=alt.X('Average Heart Rate:Q', bin=alt.Bin(maxbins=20), title='Heart Rate'),
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
        #distance histogram
        hist = alt.Chart(swim_df).mark_bar().encode(
            x=alt.X('Distance:Q', bin=alt.Bin(maxbins=20), title='Distance (Km)'),
            y=alt.Y('count()', title='Total Activities'),
            color=alt.Color('Distance:Q', bin=alt.Bin(maxbins=20),
                            scale=alt.Scale(scheme='blues'), title='Distance', legend=None)
        ).properties(
            title='Distance Distribution',
            width=400,
            height=400
        ).interactive()
        st.altair_chart(hist, use_container_width=True)

    with col3:
        # Top 3 longest swims and top 3 fastest swims
        top3_longest = swim_df.sort_values('Distance', ascending=False).head(3)
        top3_fastest = swim_df.sort_values('Pace').head(3)
        
        st.markdown("### Top 3 Longest Swims")
        for idx, row in top3_longest.iterrows():
            st.write(f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Pace']:.2f} min/100m")
        
        st.markdown("### Top 3 Fastest Swims")
        for idx, row in top3_fastest.iterrows():
            st.write(f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Pace']:.2f} min/100m")




    
    # Add week column
    swim_df['Week'] = swim_df['Activity Date'].dt.isocalendar().week
    swim_df['Year'] = swim_df['Activity Date'].dt.isocalendar().year
    swim_df['YearWeek'] = swim_df['Year'].astype(str) + '-W' + swim_df['Week'].astype(str)

    # Group by YearWeek and sum Distance
    weekly_df = swim_df.groupby(['YearWeek', 'Year', 'Week']).agg({'Distance': 'sum'}).reset_index()

    # Sort to ensure correct rolling
    weekly_df = weekly_df.sort_values(['Year', 'Week'])

    # Rolling mean (3-week window)
    weekly_df['RollingMean'] = weekly_df['Distance'].rolling(window=3, min_periods=1).mean()

    # For x-axis, convert Year and Week into a datetime
    weekly_df['Date'] = pd.to_datetime(weekly_df['Year'].astype(str) + weekly_df['Week'].astype(str) + '1', format='%G%V%u')

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
    
    bike_df.sort_values('Speed', inplace=True)
    bike_df['Average Heart Rate'].fillna(
        bike_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True
    )
    
    
    col1, col2, col3 = st.columns([6, 6, 3])
    with col1:
        scatter = alt.Chart(bike_df).mark_circle(color='brown', size=60).encode(
            x=alt.X('Speed', title='Speed (km/h)', scale=alt.Scale(domain=[8, bike_df['Speed'].max() + 2])),
            y=alt.Y('Distance', title='Distance (Km)', scale=alt.Scale(domain=[0, bike_df['Distance'].max() + 5])),
            tooltip=['Speed', 'Distance', 'Average Heart Rate', 'Activity Date']
        ).properties(
            width=400,
            height=400
        ).interactive()
        
        avg_speed = bike_df['Speed'].mean()
        avg_distance = bike_df['Distance'].mean()
        avg_df = pd.DataFrame({'Speed': [avg_speed], 'Distance': [avg_distance]})
    
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
        x=alt.X('Average Heart Rate:Q', bin=alt.Bin(maxbins=20), title='Heart Rate'),
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
        #distance histogram
        hist = alt.Chart(bike_df).mark_bar().encode(
            x=alt.X('Distance:Q', bin=alt.Bin(maxbins=20), title='Distance (Km)'),
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
        top3_elevation = bike_df.sort_values('Elevation Gain', ascending=False).head(3)
        
        st.markdown("### Top 3 Longest Rides")
        for idx, row in top3_longest.iterrows():
            st.write(f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Elevation Gain']:.0f} m elevation")
        
        st.markdown("### Top 3 Rides with Most Elevation")
        for idx, row in top3_elevation.iterrows():
            st.write(f"**{row['Activity Date'].date()}** - {row['Distance']:.2f} km, {row['Elevation Gain']:.0f} m elevation")




    
    # Add week column
    bike_df['Week'] = bike_df['Activity Date'].dt.isocalendar().week
    bike_df['Year'] = bike_df['Activity Date'].dt.isocalendar().year
    bike_df['YearWeek'] = bike_df['Year'].astype(str) + '-W' + bike_df['Week'].astype(str)

    # Group by YearWeek and sum Distance
    weekly_df = bike_df.groupby(['YearWeek', 'Year', 'Week']).agg({'Distance': 'sum'}).reset_index()

    # Sort to ensure correct rolling
    weekly_df = weekly_df.sort_values(['Year', 'Week'])

    # Rolling mean (3-week window)
    weekly_df['RollingMean'] = weekly_df['Distance'].rolling(window=3, min_periods=1).mean()

    # For x-axis, convert Year and Week into a datetime
    weekly_df['Date'] = pd.to_datetime(weekly_df['Year'].astype(str) + weekly_df['Week'].astype(str) + '1', format='%G%V%u')

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






