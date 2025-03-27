import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


st.set_page_config(
    page_title="Strava Training Dashboard",
    page_icon="🏃🚴🏊🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load data
activities_df = pd.read_csv(r'C:\Users\usuario\OneDrive\Escritorio\VS files\strava\activities.csv', encoding='latin-1', on_bad_lines='skip')

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

## DASHBOARD

# Sidebar Date Filter
st.sidebar.header("Filter by Date")
start_date = st.sidebar.date_input("From", activities_df['Activity Date'].min().date())
end_date = st.sidebar.date_input("To", activities_df['Activity Date'].max().date())

# Apply Date Filter
activities_df = activities_df[
    (activities_df['Activity Date'] >= pd.to_datetime("2022/08/03")) & 
    (activities_df['Activity Date'] <= pd.to_datetime(end_date))
]

# Filter datasets for individual sports (if needed later)
run_df = activities_df[activities_df['Activity Type'] == 'Run']
swim_df = activities_df[activities_df['Activity Type'] == 'Swim']
bike_df = activities_df[activities_df['Activity Type'] == 'Ride']


if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = "General"

# Navigation: Four clickable cards displayed as squares on the main page
# st.title('Strava Training Dashboard')

st.markdown(
    """
    <style>
    /* Target all Streamlit buttons */
    div.stButton > button {
        width: 200px;      /* Wider buttons */
        font-size: 2rem;   /* Bigger icon size */
        height: 100px;      /* Fixed height */
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


######################### GENERAL ##########################################
if selected_tab == 'General':
    # First row: Heatmap & Pie Chart
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
                alt.Tooltip("Activity Type:N"),
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




    # Create the small multiples area chart
    chart = alt.Chart(activities_df).mark_area().encode(
        x=alt.X('YearMonth:T', title='Month'),
        y=alt.Y('sum(Moving Time):Q', title='Total Time (hours)'),
        color=alt.Color('Activity Type:N', legend=None),
        row=alt.Row('Activity Type:N').sort(['Running', 'Cycling', 'Swimming'])  # Custom sorting
    ).properties(
        width=500,  # Adjust width of each small multiple
        height=80,  # Adjust height of each small multiple
        title="Monthly Strava Training (Small Multiples)"
    )

    # Display in Streamlit
    st.altair_chart(chart, use_container_width=True)




############################### RUNNING ##########################################

elif selected_tab == 'Running':
    col1, col2, col3 = st.columns([3, 3, 3])
    run_df = run_df.copy()
    run_df['Moving Time'] = run_df['Moving Time'] / 60
    run_df['Distance'] = run_df['Distance'] / 1000
    run_df['Pace'] = (run_df['Moving Time'] / (run_df['Distance'])).round(2)

    run_df.sort_values('Pace', inplace=True)
    run_df['Average Heart Rate'].fillna(run_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True)

    # Pace vs Distance Scatter
    with col1:
        scatter = alt.Chart(run_df).mark_circle(size=60).encode(
            x=alt.X('Pace', title='Pace (min/km)', scale=alt.Scale(domain=[3.5, 7.5])),
            y=alt.Y('Distance', title='Distance (Km)', scale=alt.Scale(domain=[0, run_df['Distance'].max()+1])),
            color=alt.Color('Average Heart Rate:Q', scale=alt.Scale(scheme='greens'), legend=None),
            tooltip=['Pace', 'Distance', 'Average Heart Rate', 'Activity Date']
        ).properties(
            width=700,
            height=500
        ).interactive()

        avg_pace = run_df['Pace'].mean()
        avg_distance = run_df['Distance'].mean()
        avg_df = pd.DataFrame({'Pace': [avg_pace], 'Distance': [avg_distance]})

        avg_point = alt.Chart(avg_df).mark_text(
        text='✖',  # Unicode "X" symbol
        fontSize=24,
        color='darkgreen'
        ).encode(
            x='Pace',
            y='Distance',
            tooltip=['Pace', 'Distance']
        )

        chart = scatter + avg_point
        st.altair_chart(chart, use_container_width=False)

    # Distance Histogram
    with col2:
        hist = alt.Chart(run_df).mark_bar(color='green').encode(
        x=alt.X('Distance:Q', bin=alt.Bin(maxbins=20), title='Distance (Km)'),
        y=alt.Y('count()', title='Total Activities')
        ).properties(
        title='Distance Distribution',
        width=700,
        height=500
        )

        st.altair_chart(hist, use_container_width=True)

    with col3:
        hist = alt.Chart(run_df).mark_bar().encode(
        x=alt.X('Average Heart Rate:Q', bin=alt.Bin(maxbins=20), title='Heart Rate'),
        y=alt.Y('count()', title='Total Activities'),
        color=alt.Color('Average Heart Rate:Q', bin=alt.Bin(maxbins=20),
                        scale=alt.Scale(scheme='reds'), title='Heart Rate', legend=None)
        ).properties(
        title='Heart Rate Distribution',
        width=700,
        height=500
        )

        st.altair_chart(hist, use_container_width=True)

    # Calculate overall summary statistics
    total_distance = run_df['Distance'].sum().round(2)
    total_time = run_df['Moving Time'].sum().round(2)
    total_activities = run_df.shape[0]
    avg_distance = run_df['Distance'].mean().round(2)
    avg_time = run_df['Moving Time'].mean().round(2)
    avg_pace = run_df['Pace'].mean().round(2)
    avg_hr = run_df['Average Heart Rate'].mean().round(2)

    # Define medal emojis for ranking
    medals = ['🥇', '🥈', '🥉']

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Running Summary")
        st.write(f"**Total Distance:** {total_distance} km")
        st.write(f"**Total Time:** {total_time} hours")
        st.write(f"**Total Activities:** {total_activities}")
        st.write(f"**Average Distance:** {avg_distance} km")
        st.write(f"**Average Time:** {avg_time} hours")
        st.write(f"**Average Pace:** {avg_pace} min/km")
        st.write(f"**Average Heart Rate:** {avg_hr} bpm")

    with col2:
        # Top 3 Longest Runs with medals
        st.markdown("### Top 3 Longest Runs")
        top_longest = run_df.nlargest(3, 'Distance').copy()
        top_longest.insert(0, 'Rank', medals)
        st.dataframe(top_longest[['Rank', 'Activity Date', 'Activity Name', 'Distance',  'Pace']])

    with col3:
        # Top 3 Fastest Runs (lowest pace values) with medals
        st.markdown("### Top 3 Fastest Runs")
        top_fastest = run_df.nsmallest(3, 'Pace').copy()
        top_fastest.insert(0, 'Rank', medals)
        st.dataframe(top_fastest[['Rank', 'Activity Date', 'Activity Name', 'Distance', 'Pace']])



############################### SWIMMING ##########################################

elif selected_tab == 'Swimming':
    col1, col2, col3 = st.columns([3, 3, 3])
    swim_df = swim_df.copy()
    
    swim_df['Moving Time'] = swim_df['Moving Time'] / 60  
    swim_df['Pace'] = (swim_df['Moving Time'] / (swim_df['Distance'] / 100)).round(2)
    
    swim_df.sort_values('Pace', inplace=True)
    swim_df['Average Heart Rate'].fillna(swim_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True)
    
    with col1:
        scatter = alt.Chart(swim_df).mark_circle(color='blue', size=60).encode(
        x=alt.X('Pace', title='Pace (min/100m)', scale=alt.Scale(domain=[1, 3])),
        y=alt.Y('Distance', title='Distance (m)', scale=alt.Scale(domain=[0, swim_df['Distance'].max() + 50])),
        tooltip=['Pace', 'Distance', 'Average Heart Rate', 'Activity Date']
        ).properties(
            width=700,
            height=500
        ).interactive()

    
        avg_pace = swim_df['Pace'].mean()
        avg_distance = swim_df['Distance'].mean()
        avg_df = pd.DataFrame({'Pace': [avg_pace], 'Distance': [avg_distance]})
    
        avg_point = alt.Chart(avg_df).mark_text(
            text='✖',  # Unicode "X" symbol
            fontSize=24,
            color='darkblue'
        ).encode(
            x='Pace',
            y='Distance',
            tooltip=['Pace', 'Distance']
        )
    
        chart = scatter + avg_point
        st.altair_chart(chart, use_container_width=False)
    
    with col2:
        hist = alt.Chart(swim_df).mark_bar(color='blue').encode(
            x=alt.X('Distance:Q', bin=alt.Bin(maxbins=20), title='Distance (m)'),
            y=alt.Y('count()', title='Total Activities')
        ).properties(
            title='Distance Distribution',
            width=700,
            height=500
        )
    
        st.altair_chart(hist, use_container_width=True)
    
    with col3:
        hist = alt.Chart(swim_df).mark_bar().encode(
            x=alt.X('Average Heart Rate:Q', bin=alt.Bin(maxbins=20), title='Heart Rate'),
            y=alt.Y('count()', title='Total Activities'),
            color=alt.Color('Average Heart Rate:Q', bin=alt.Bin(maxbins=20),
                             scale=alt.Scale(scheme='reds'), title='Heart Rate', legend=None)
        ).properties(
            title='Heart Rate Distribution',
            width=700,
            height=500
        )
    
        st.altair_chart(hist, use_container_width=True)

    
    # Calculate overall summary statistics
    total_distance = swim_df['Distance'].sum().round(2)
    total_time = swim_df['Moving Time'].sum().round(2)
    total_activities = swim_df.shape[0]
    avg_distance = swim_df['Distance'].mean().round(2)
    avg_time = swim_df['Moving Time'].mean().round(2)
    avg_pace = swim_df['Pace'].mean().round(2)
    avg_hr = swim_df['Average Heart Rate'].mean().round(2)

    # Define medal emojis for ranking
    medals = ['🥇', '🥈', '🥉']

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Running Summary")
        st.write(f"**Total Distance:** {total_distance} km")
        st.write(f"**Total Time:** {total_time} hours")
        st.write(f"**Total Activities:** {total_activities}")
        st.write(f"**Average Distance:** {avg_distance} km")
        st.write(f"**Average Time:** {avg_time} hours")
        st.write(f"**Average Pace:** {avg_pace} min/100m")
        st.write(f"**Average Heart Rate:** {avg_hr} bpm")

    with col2:
        # Top 3 Longest Runs with medals
        st.markdown("### Top 3 Longest Swims")
        top_longest = swim_df.nlargest(3, 'Distance').copy()
        top_longest.insert(0, 'Rank', medals)
        st.dataframe(top_longest[['Rank', 'Activity Date', 'Distance',  'Pace']])
    
    with col3:
        # Top 3 Fastest Runs (lowest pace values) with medals
        st.markdown("### Top 3 Fastest Swims")
        top_fastest = swim_df.nsmallest(3, 'Pace').copy()
        top_fastest.insert(0, 'Rank', medals)
        st.dataframe(top_fastest[['Rank', 'Activity Date', 'Distance', 'Pace']])

############################### CYCLING ##########################################

elif selected_tab == 'Cycling':
    col1, col2, col3 = st.columns([3, 3, 3])
    bike_df = bike_df.copy()
    
    bike_df['Distance'] = bike_df['Distance'] / 1000  
    bike_df['Moving Time'] = bike_df['Moving Time'] / 3600  
    
    # Calculate speed in km/h
    bike_df['Speed'] = (bike_df['Distance'] / bike_df['Moving Time']).round(2)
    
    bike_df.sort_values('Speed', inplace=True)
    bike_df['Average Heart Rate'].fillna(
        bike_df['Average Heart Rate'].rolling(5, min_periods=1).mean(), inplace=True
    )
    
    with col1:
        scatter = alt.Chart(bike_df).mark_circle(color='brown', size=60).encode(
            x=alt.X('Speed', title='Speed (km/h)', scale=alt.Scale(domain=[8, bike_df['Speed'].max() + 2])),
            y=alt.Y('Distance', title='Distance (Km)', scale=alt.Scale(domain=[0, bike_df['Distance'].max() + 5])),
            tooltip=['Speed', 'Distance', 'Average Heart Rate', 'Activity Date']
        ).properties(
            width=700,
            height=500
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
        )
    
        chart = scatter + avg_point
        st.altair_chart(chart, use_container_width=False)
    
    with col2:
        hist = alt.Chart(bike_df).mark_bar(color='brown').encode(
            x=alt.X('Distance:Q', bin=alt.Bin(maxbins=20), title='Distance (Km)'),
            y=alt.Y('count()', title='Total Activities')
        ).properties(
            title='Distance Distribution',
            width=700,
            height=500
        )
    
        st.altair_chart(hist, use_container_width=True)
    
    with col3:
        hist = alt.Chart(bike_df).mark_bar().encode(
            x=alt.X('Average Heart Rate:Q', bin=alt.Bin(maxbins=20), title='Heart Rate'),
            y=alt.Y('count()', title='Total Activities'),
            color=alt.Color(
                'Average Heart Rate:Q', 
                bin=alt.Bin(maxbins=20),
                scale=alt.Scale(scheme='reds'),
                title='Heart Rate',
                legend=None
            )
        ).properties(
            title='Heart Rate Distribution',
            width=700,
            height=500
        )
    
        st.altair_chart(hist, use_container_width=True)


    

    # Calculate overall summary statistics
    total_distance = bike_df['Distance'].sum().round(2)
    total_elevation = bike_df['Elevation Gain'].sum().round(2)
    total_time = bike_df['Moving Time'].sum().round(2)
    total_activities = bike_df.shape[0]
    avg_distance = bike_df['Distance'].mean().round(2)
    avg_time = bike_df['Moving Time'].mean().round(2)
    avg_speed = bike_df['Speed'].mean().round(2)
    avg_hr = bike_df['Average Heart Rate'].mean().round(2)
    avg_elevation = bike_df['Elevation Gain'].mean().round(2)

    # Define medal emojis for ranking
    medals = ['🥇', '🥈', '🥉']

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Cycling Summary")
        st.write(f"**Total Distance:** {total_distance} km")
        st.write(f"**Total Elev Gain:** {total_elevation} m")
        st.write(f"**Total Time:** {total_time} hours")
        st.write(f"**Total Activities:** {total_activities}")
        st.write(f"**Average Distance:** {avg_distance} km")
        st.write(f"**Average Time:** {avg_time} hours")
        st.write(f"**Average Speed:** {avg_speed} km/h")
        st.write(f"**Average Heart Rate:** {avg_hr} bpm")
        st.write(f"**Average Elev Gain:** {avg_elevation} m")

    with col2:
        st.markdown("### Top 3 Longest Rides")
        top_longest = bike_df.nlargest(3, 'Distance').copy()
        top_longest.insert(0, 'Rank', medals)
        st.dataframe(top_longest[['Rank', 'Activity Date', 'Distance', 'Speed']])
    with col3:
        st.markdown("### Top 3 Elevation")
        top_elevation = bike_df.nlargest(3, 'Elevation Gain').copy()
        top_elevation.insert(0, 'Rank', medals)
        st.dataframe(top_elevation[['Rank', 'Activity Date', 'Distance', 'Elevation Gain']])
    
    #distance vs elevation
    fig, ax = plt.subplots()
    sns.scatterplot(data=bike_df, x='Distance', y='Elevation Gain', ax=ax)
    st.pyplot(fig)

    #histogram of elevation
    fig, ax = plt.subplots()
    sns.histplot(bike_df['Elevation Gain'], kde=True, ax=ax)
    st.pyplot(fig)

    #histogram of 



    





###################### FUNCTIONS ##########################################
