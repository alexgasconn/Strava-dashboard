import pandas as pd

def preprocess_data(df):
    df.dropna(axis=1, how='all', inplace=True)
    df = df[df['Activity Type'].str.contains('Ride|Run|Swim|Weight Training', na=False)]
    df['Distance'] = df['Distance.1']
    df['Activity Date'] = pd.to_datetime(df['Activity Date'])

    df['Hour'] = df['Activity Date'].dt.hour + 1
    df['Day'] = df['Activity Date'].dt.day
    df['Week'] = df['Activity Date'].dt.isocalendar().week
    df['Month'] = df['Activity Date'].dt.month
    df['Year'] = df['Activity Date'].dt.year
    df['YearMonth'] = df['Activity Date'].dt.to_period('M')
    df['DayOfWeek'] = df['Activity Date'].dt.dayofweek
    df['Quarter'] = df['Activity Date'].dt.quarter
    df['IsWeekend'] = df['Activity Date'].dt.dayofweek >= 5

    df['Activity Type'] = df['Activity Type'].replace({
        'Football (Soccer)': 'Football',
        'Workout': 'Padel'
    })

    return df
