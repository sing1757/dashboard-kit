import streamlit as st
import pandas as pd
from datetime import timedelta, datetime

# Set page config
st.set_page_config(page_title="Streamlit YouTube Channel Dashboard", layout="wide")

@st.cache_data
def load_data():
    data = pd.read_csv("youtube_channel_data.csv")
    data['DATE'] = pd.to_datetime(data['DATE'])
    data['NET_SUBSCRIBERS'] = data['SUBSCRIBERS_GAINED'] - data['SUBSCRIBERS_LOST']
    return data

def aggregate_data(df, freq):
    df_agg = df.resample(freq, on='DATE').agg({
        'VIEWS': 'sum',
        'WATCH_HOURS': 'sum',
        'NET_SUBSCRIBERS': 'sum',
        'LIKES': 'sum',
        'COMMENTS': 'sum',
        'SHARES': 'sum',
    })
    return df_agg

def get_weekly_data(df):
    return aggregate_data(df, 'W-MON')

def get_monthly_data(df):
    return aggregate_data(df, 'M')

def get_quarterly_data(df):
    df_quarterly = aggregate_data(df, 'Q')
    df_quarterly.index = df_quarterly.index.to_period('Q')
    return df_quarterly

def format_with_commas(number):
    return f"{number:,}"

def create_metric_chart(df, column, color, height=200, time_frame='Daily'):
    chart_data = df[[column]].copy()
    if time_frame == 'Quarterly':
        chart_data.index = chart_data.index.astype(str)
    st.bar_chart(chart_data, y=column, color=color, height=height)

def is_period_complete(date, freq):
    today = datetime.now()
    if freq == 'D':
        return date.date() < today.date()
    elif freq == 'W':
        return date + timedelta(days=6) < today
    elif freq == 'M':
        next_month = date.replace(day=28) + timedelta(days=4)
        return next_month.replace(day=1) <= today
    elif freq == 'Q':
        current_quarter = pd.Period(today, freq='Q')
        return pd.Period(date, freq='Q') < current_quarter

def display_metric(col, title, value, df, column, color, time_frame):
    with col:
        with st.container(border=True):
            st.metric(title, format_with_commas(value))
            create_metric_chart(df, column, color, time_frame=time_frame)
            
            last_period = df.index[-1]
            freq = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M', 'Quarterly': 'Q'}[time_frame]
            if not is_period_complete(last_period, freq):
                st.caption(f"Note: The last {time_frame.lower()[:-2] if time_frame != 'Daily' else 'day'} is incomplete.")

# Load data
df = load_data()

# Set up the dashboard
st.title("🎈 Streamlit YouTube Channel Dashboard")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    max_date = df['DATE'].max().date()
    default_start_date = max_date - timedelta(days=365)  # Show a year by default
    default_end_date = max_date
    start_date = st.date_input("Start date", default_start_date, min_value=df['DATE'].min().date(), max_value=max_date)
    end_date = st.date_input("End date", default_end_date, min_value=df['DATE'].min().date(), max_value=max_date)
    time_frame = st.selectbox(
        "Select time frame",
        ("Daily", "Weekly", "Monthly", "Quarterly"),
    )

# Prepare data based on selected time frame
if time_frame == 'Daily':
    df_display = df.set_index('DATE')
elif time_frame == 'Weekly':
    df_display = get_weekly_data(df)
elif time_frame == 'Monthly':
    df_display = get_monthly_data(df)
elif time_frame == 'Quarterly':
    df_display = get_quarterly_data(df)

# Key Metrics
st.subheader("Key Metrics")
st.caption("All-Time Statistics")
metrics = [
    ("Total Subscribers", "NET_SUBSCRIBERS", '#29b5e8'),
    ("Total Views", "VIEWS", '#FF9F36'),
    ("Total Watch Hours", "WATCH_HOURS", '#D45B90'),
    ("Total Likes", "LIKES", '#7D44CF')
]

cols = st.columns(4)
for col, (title, column, color) in zip(cols, metrics):
    total_value = df[column].sum()
    display_metric(col, title, total_value, df_display, column, color, time_frame)

# Selected Duration Metrics
st.caption("Selected Duration")
if time_frame == 'Quarterly':
    start_quarter = pd.Period(start_date, freq='Q')
    end_quarter = pd.Period(end_date, freq='Q')
    mask = (df_display.index >= start_quarter) & (df_display.index <= end_quarter)
else:
    mask = (df_display.index >= pd.Timestamp(start_date)) & (df_display.index <= pd.Timestamp(end_date))
df_filtered = df_display.loc[mask]

cols = st.columns(4)
for col, (title, column, color) in zip(cols, metrics):
    display_metric(col, title.split()[-1], df_filtered[column].sum(), df_filtered, column, color, time_frame)

# DataFrame display
with st.expander('See DataFrame'):
    st.dataframe(df)
    st.dataframe(df_display)
