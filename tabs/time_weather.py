import streamlit as st
import altair as alt
import pandas as pd

def render(df):
    st.header("Time & Weather Analysis")

    if 'Hour' in df.columns:
        st.metric("Most Common Hour", f"{int(df['Hour'].mean())}:00")
    if 'DayOfWeek' in df.columns:
        dow_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        st.metric("Most Active Day", dow_map[df['DayOfWeek'].mode()[0]])
    if 'Weather Condition' in df.columns:
        st.metric("Most Frequent Weather", df['Weather Condition'].mode()[0])

    col1, col2 = st.columns(2)

    with col1:
        if 'Hour' in df.columns:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('Hour:O', title='Hour of Day'),
                y=alt.Y('count()', title='Number of Activities'),
                color=alt.Color('Activity Type:N', legend=None)
            ).properties(title='Activity Start Times', width=400, height=400)
            st.altair_chart(chart, use_container_width=True)

    with col2:
        if 'DayOfWeek' in df.columns:
            day_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
            df['DayOfWeekStr'] = df['DayOfWeek'].map(day_map)

            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('DayOfWeekStr:N', title='Day of Week', sort=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']),
                y=alt.Y('count()', title='Number of Activities'),
                color=alt.Color('Activity Type:N', legend=None)
            ).properties(title='Activity Frequency by Day', width=400, height=400)
            st.altair_chart(chart, use_container_width=True)

    if 'Weather Condition' in df.columns:
        df['Weather Condition'] = df['Weather Condition'].map({
            1: '☀️ Clear', 2: '☁️ Cloudy', 3: '⛅ Partly Cloudy',
            4: '🌧️ Rainy', 5: '💨 Windy', 6: '❄️ Snowy'
        }).fillna('Unknown')
        weather_df = df[df['Weather Condition'].notnull()]
        chart = alt.Chart(weather_df).mark_bar().encode(
            x=alt.X('Weather Condition:N', title='Weather Condition'),
            y=alt.Y('count()', title='Number of Activities'),
            color=alt.Color('Weather Condition:N', legend=None)
        ).properties(title='Activities by Weather', width=600, height=400)
        st.altair_chart(chart, use_container_width=True)




    st.markdown("### Time and Weather Analysis 🕒⛅")
    st.info(
        "This section is still under construction, but already offers useful insights.")

    col1, col2, col3 = st.columns([4, 4, 4])
    with col1:
        if 'Hour' in df.columns:
            avg_hour = int(df['Hour'].mean())
            st.metric("Most Common Hour", f"{avg_hour}:00")
        if 'DayOfWeek' in df.columns:
            dow_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            most_common_day = df['DayOfWeek'].mode()[0]
            st.metric("Most Active Day", dow_map[most_common_day])
    with col2:
        if 'Weather Condition' in df.columns:
            top_weather = df['Weather Condition'].mode()[0]
            st.metric("Most Frequent Weather", top_weather)
    with col3:
        top_activity = df['Activity Type'].mode()[0]
        st.metric("Top Activity", top_activity)

    st.markdown("---")

    # Distribution by Hour of Day
    col1, col2 = st.columns([6, 6])
    with col1:
        if 'Hour' in df.columns:
            hour_chart = alt.Chart(df).mark_bar().encode(
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
        if 'DayOfWeek' in df.columns:
            df['DayOfWeekStr'] = df['DayOfWeek'].map(
                lambda x: dow_map[x])
            dow_chart = alt.Chart(df).mark_bar().encode(
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
    if 'Month' in df.columns and 'DayOfWeek' in df.columns:
        heatmap_data = df.groupby(['Month', 'DayOfWeek']).size().reset_index(name='Count')
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
        if 'Month' in df.columns and 'Hour' in df.columns:
            heatmap_data = df.groupby(['Month', 'Hour']).size().reset_index(name='Count')
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
            top_sports = df['Activity Type'].value_counts().head(5).index.tolist()

            favorite_hour_day_month_sport = []
            for sport in top_sports:
                sport_df = df[df['Activity Type'] == sport]
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
    if 'Hour' in df.columns and 'Weather Condition' in df.columns:
        hourly_weather_data = df.groupby(['Hour', 'Weather Condition']).size().reset_index(name='Count')
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
    if 'Month' in df.columns and 'Weather Temperature' in df.columns:
        monthly_activity_temp = df.groupby('Month').agg(
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
    if 'Hour' in df.columns and 'Weather Sunrise' in df.columns:
        df['Sunrise Impact'] = df['Hour'] - pd.to_datetime(df['Weather Sunrise']).dt.hour
        sunrise_impact_chart = alt.Chart(df).mark_bar().encode(
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
    if 'Wind Speed' in df.columns:
        wind_speed_data = df.groupby(pd.cut(df['Wind Speed'], bins=10)).size().reset_index(name='Count')
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
    if 'Weather Temperature' in df.columns and 'Moving Time' in df.columns:
        temp_performance_data = df.groupby(pd.cut(df['Weather Temperature'], bins=10)).agg(
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
    if 'Weather Temperature' in df.columns and 'Moving Time' in df.columns:
        temp_performance_data = df.groupby(pd.cut(df['Weather Temperature'], bins=10)).agg(
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
    if {'Weather Temperature', 'Humidity', 'Wind Speed', 'Moving Time', 'Distance'}.issubset(df.columns):
        correlation_data = df[['Weather Temperature', 'Humidity', 'Wind Speed', 'Moving Time', 'Distance']].corr()
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
    if 'Weather Condition' in df.columns:
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
            df['Weather Condition'] = df['Weather Condition'].map(
                weather_map)

            # Filter out NULL values
            weather_filtered_df = df[df['Weather Condition'].notnull(
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
    monthly_temp = df.groupby('Month').agg(
        {'Weather Temperature': 'mean'}).reset_index()
    monthly_temp['MonthStr'] = monthly_temp['Month'].map({
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    })

    # Calculate monthly averages for temperature, humidity, and wind speed
    monthly_weather = df.groupby('Month').agg({
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
    if 'Hour' in df.columns and 'DayOfWeekStr' in df.columns:
        heatmap_data = df.groupby(
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
