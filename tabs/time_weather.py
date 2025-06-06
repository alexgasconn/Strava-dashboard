import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

def render(df):
    st.header("Time & Weather Analysis")

    # Define mappings
    dow_map = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    weather_map = {
        1: '☀️ Clear',
        2: '☁️ Cloudy',
        3: '⛅ Partly Cloudy',
        4: '🌧️ Rainy',
        5: '💨 Windy',
        6: '❄️ Snowy'
    }

    # --- Add Filters ---
    filter_cols = st.columns(2)
    with filter_cols[0]:
        day_filter = st.multiselect(
            "Filter by Day of Week",
            options=list(range(7)),
            format_func=lambda x: dow_map[x],
            default=list(range(7))
        )
    with filter_cols[1]:
        month_filter = st.multiselect(
            "Filter by Month",
            options=list(month_map.keys()),
            format_func=lambda x: month_map[x],
            default=list(month_map.keys())
        )

    # Apply filters
    if 'DayOfWeek' in df.columns:
        df = df[df['DayOfWeek'].isin(day_filter)]
    if 'Month' in df.columns:
        df = df[df['Month'].isin(month_filter)]

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if 'Hour' in df.columns:
            avg_hour = int(df['Hour'].mean())
            st.metric("Most Common Hour", f"{avg_hour}:00")
    with col2:
        if 'DayOfWeek' in df.columns:
            most_common_day = df['DayOfWeek'].mode()[0]
            st.metric("Most Active Day", dow_map[most_common_day])
    with col3:
        if 'Weather Condition' in df.columns:
            # Map weather codes to labels for metrics
            df['Weather Condition Label'] = df['Weather Condition'].map(weather_map).fillna('Unknown')
            top_weather = df['Weather Condition Label'].mode()[0]
            st.metric("Most Frequent Weather", top_weather)
    with col4:
        if 'Activity Type' in df.columns:
            top_activity = df['Activity Type'].mode()[0]
            st.metric("Top Activity", top_activity)

    st.markdown("---")

    # Hourly Activity Distribution
    col1, col2 = st.columns(2)
    with col1:
        if 'Hour' in df.columns:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('Hour:O', title='Hour of Day'),
                y=alt.Y('count()', title='Number of Activities'),
                color=alt.Color('Activity Type:N', legend=None),
                tooltip=['Hour:O', 'count()']
            ).properties(
                title='Activity Start Times',
                width=400,
                height=400
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("No hour data available.")

    with col2:
        if 'DayOfWeek' in df.columns:
            df['DayOfWeekStr'] = df['DayOfWeek'].map(lambda x: dow_map[x])
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
        heatmap_data['MonthStr'] = heatmap_data['Month'].map(month_map)
        heatmap_data['DayOfWeekStr'] = heatmap_data['DayOfWeek'].map(lambda x: dow_map[x])
        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x=alt.X('MonthStr:N', title='Month', sort=list(month_map.values())),
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
        heatmap_data['MonthStr'] = heatmap_data['Month'].map(month_map)
        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x=alt.X('Hour:O', title='Hour of Day'),
            y=alt.Y('MonthStr:N', title='Month', sort=list(month_map.values())),
            color=alt.Color('Count:Q', scale=alt.Scale(scheme='greens'), title='Activity Count'),
            tooltip=['MonthStr', 'Hour', 'Count']
        ).properties(
            title='Heatmap: Month vs Hour of Day',
            width=600,
            height=400
        )
        st.altair_chart(heatmap, use_container_width=True)

    # Favorite hour, day, month for top 5 sports
    if 'Activity Type' in df.columns:
        top_sports = df['Activity Type'].value_counts().head(5).index.tolist()
        st.markdown("### Favorite Hour, Day, and Month for Top 5 Sports")
        for sport in top_sports:
            sport_df = df[df['Activity Type'] == sport]
            favorite_hour = sport_df['Hour'].mode()[0] if 'Hour' in sport_df.columns and not sport_df['Hour'].empty else None
            favorite_day = sport_df['DayOfWeek'].mode()[0] if 'DayOfWeek' in sport_df.columns and not sport_df['DayOfWeek'].empty else None
            favorite_month = sport_df['Month'].mode()[0] if 'Month' in sport_df.columns and not sport_df['Month'].empty else None
            favorite_day_str = dow_map[favorite_day] if favorite_day is not None else None
            favorite_month_str = month_map[favorite_month] if favorite_month is not None else None
            st.write(f"**{sport}:** Favorite Hour: {favorite_hour}:00, Favorite Day: {favorite_day_str}, Favorite Month: {favorite_month_str}")

    # Hourly Activity Distribution by Weather Condition
    if 'Hour' in df.columns and 'Weather Condition' in df.columns:
        df['Weather Condition Label'] = df['Weather Condition'].map(weather_map).fillna('Unknown')
        hourly_weather_data = df.groupby(['Hour', 'Weather Condition Label']).size().reset_index(name='Count')
        hourly_weather_chart = alt.Chart(hourly_weather_data).mark_bar().encode(
            x=alt.X('Hour:O', title='Hour of Day'),
            y=alt.Y('Count:Q', title='Number of Activities'),
            color=alt.Color('Weather Condition Label:N', title='Weather Condition'),
            tooltip=['Hour:O', 'Weather Condition Label:N', 'Count:Q']
        ).properties(
            title='Hourly Activity Distribution by Weather Condition',
            width=600,
            height=400
        )
        st.altair_chart(hourly_weather_chart, use_container_width=True)

    # Monthly Activity Count vs Average Temperature
    if 'Month' in df.columns and 'Weather Temperature' in df.columns and 'Activity Type' in df.columns:
        monthly_activity_temp = df.groupby('Month').agg(
            Activity_Count=('Activity Type', 'count'),
            Avg_Temperature=('Weather Temperature', 'mean')
        ).reset_index()
        monthly_activity_temp['MonthStr'] = monthly_activity_temp['Month'].map(month_map)

        activity_temp_chart = alt.Chart(monthly_activity_temp).mark_line(point=True, color='blue').encode(
            x=alt.X('MonthStr:N', title='Month', sort=list(month_map.values())),
            y=alt.Y('Activity_Count:Q', title='Activity Count'),
            tooltip=['MonthStr', 'Activity_Count', 'Avg_Temperature']
        ).properties(
            title='Monthly Activity Count vs Average Temperature',
            width=600,
            height=400
        )

        temp_line = alt.Chart(monthly_activity_temp).mark_line(strokeDash=[5, 5], color='orange').encode(
            x=alt.X('MonthStr:N', sort=list(month_map.values())),
            y=alt.Y('Avg_Temperature:Q', title='Average Temperature (°C)'),
            tooltip=['MonthStr', 'Avg_Temperature']
        )

        st.altair_chart(activity_temp_chart + temp_line, use_container_width=True)

    # Sunrise Impact
    if 'Hour' in df.columns and 'Weather Sunrise' in df.columns:
        try:
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
        except Exception:
            pass

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

    # Temperature Impact on Performance
    if 'Weather Temperature' in df.columns and 'Moving Time' in df.columns and 'Distance' in df.columns:
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
        corr_melt = correlation_data.reset_index().melt('index')
        correlation_chart = alt.Chart(corr_melt).mark_rect().encode(
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

    # Weather Condition by Month Heatmap and Bar
    if 'Weather Condition' in df.columns and 'Month' in df.columns:
        df['Weather Condition Label'] = df['Weather Condition'].map(weather_map).fillna('Unknown')
        weather_filtered_df = df[df['Weather Condition Label'].notnull()]
        weather_filtered_df['MonthStr'] = weather_filtered_df['Month'].map(month_map)
        weather_heatmap_data = weather_filtered_df.groupby(
            ['MonthStr', 'Weather Condition Label']).size().reset_index(name='Count')
        weather_heatmap = alt.Chart(weather_heatmap_data).mark_rect().encode(
            x=alt.X('MonthStr:N', title='Month', sort=list(month_map.values())),
            y=alt.Y('Weather Condition Label:N', title='Weather Condition'),
            color=alt.Color('Count:Q', scale=alt.Scale(scheme='reds'), title='Activity Count'),
            tooltip=['MonthStr', 'Weather Condition Label', 'Count']
        ).properties(
            title='Heatmap: Weather Condition by Month',
            width=600,
            height=400
        )
        st.altair_chart(weather_heatmap, use_container_width=True)

        weather_chart = alt.Chart(weather_filtered_df).mark_bar().encode(
            x=alt.X('Weather Condition Label:N', title='Weather'),
            y=alt.Y('count()', title='Number of Activities'),
            color=alt.Color('Weather Condition Label:N', legend=None),
            tooltip=['Weather Condition Label:N', 'count()']
        ).properties(
            title='Activities by Weather Condition',
            width=400,
            height=400
        ).interactive()
        st.altair_chart(weather_chart, use_container_width=True)

    # Monthly Weather Metrics
    if {'Month', 'Weather Temperature', 'Humidity', 'Wind Speed'}.issubset(df.columns):
        monthly_weather = df.groupby('Month').agg({
            'Weather Temperature': 'mean',
            'Humidity': 'mean',
            'Wind Speed': 'mean'
        }).reset_index()
        monthly_weather['MonthStr'] = monthly_weather['Month'].map(month_map)

        temp_chart = alt.Chart(monthly_weather).mark_bar(color='orange').encode(
            x=alt.X('MonthStr:N', title='Month', sort=list(month_map.values())),
            y=alt.Y('Weather Temperature:Q', title='Average Temperature (°C)'),
            tooltip=['MonthStr', 'Weather Temperature']
        )

        humidity_chart = alt.Chart(monthly_weather).mark_area(color='blue', opacity=0.1).encode(
            x=alt.X('MonthStr:N', sort=list(month_map.values())),
            y=alt.Y('Humidity:Q', title='Humidity (%)'),
            tooltip=['MonthStr', 'Humidity']
        )

        wind_chart = alt.Chart(monthly_weather).mark_line(color='grey').encode(
            x=alt.X('MonthStr:N', sort=list(month_map.values())),
            y=alt.Y('Wind Speed:Q', title='Wind Speed (km/h)'),
            tooltip=['MonthStr', 'Wind Speed']
        )

        combined_chart = alt.layer(temp_chart, humidity_chart, wind_chart).resolve_scale(
            y='independent'
        ).properties(
            title='Monthly Weather Metrics',
            width=600,
            height=400
        )

        st.altair_chart(combined_chart, use_container_width=True)

    # Heatmap: Hour vs Day of Week
    if 'Hour' in df.columns and 'DayOfWeek' in df.columns:
        df['DayOfWeekStr'] = df['DayOfWeek'].map(lambda x: dow_map[x])
        heatmap_data = df.groupby(['DayOfWeekStr', 'Hour']).size().reset_index(name='Count')
        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x=alt.X('Hour:O', title='Hour'),
            y=alt.Y('DayOfWeekStr:N', title='Day of Week', sort=dow_map),
            color=alt.Color('Count:Q', scale=alt.Scale(scheme='blues'), title='Activity Count'),
            tooltip=['DayOfWeekStr', 'Hour', 'Count']
        ).properties(
            title='Heatmap: Hour vs Day of Week',
            width=600,
            height=400
        )
        st.altair_chart(heatmap, use_container_width=True)

    st.markdown("---")
    st.info("More advanced insights like temperature impact, sunrise time effects, and performance under rain will be added soon! 🚧")