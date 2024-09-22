import streamlit as st
import pandas as pd
from datetime import timedelta

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
    }).reset_index()
    return df_agg

def get_weekly_data(df):
    return aggregate_data(df, 'W-MON')

def get_monthly_data(df):
    return aggregate_data(df, 'M')

def get_quarterly_data(df):
    df_monthly = df.resample('M', on='DATE').agg({
        'VIEWS': 'sum',
        'WATCH_HOURS': 'sum',
        'NET_SUBSCRIBERS': 'sum',
        'LIKES': 'sum',
        'COMMENTS': 'sum',
        'SHARES': 'sum',
    }).reset_index()
    
    df_monthly['QUARTER'] = df_monthly['DATE'].dt.to_period('Q')
    df_monthly['MONTH'] = df_monthly['DATE'].dt.strftime('%b')
    
    return df_monthly

def format_with_commas(number):
    return f"{number:,}"

def create_metric_chart(df, column, color, height=150, chart_type='area'):
    if chart_type == 'area':
        return st.area_chart(df, y=column, color=color, height=height)
    elif chart_type == 'bar':
        return st.bar_chart(df, y=column, color=color, height=height)

def display_metric(col, title, value, df, column, color):
    with col:
        with st.container(border=True):
            st.metric(title, format_with_commas(value))
            create_metric_chart(df, column, color)

def display_quarterly_chart(df, metric):
    st.subheader(f"Quarterly {metric} Chart")
    
    current_quarter = pd.Timestamp.now().to_period('Q')
    df_current = df[df['QUARTER'] == current_quarter]
    
    chart_data = df_current[['MONTH', metric]].set_index('MONTH')
    
    create_metric_chart(chart_data, metric, color='#1f77b4', height=300, chart_type='bar')
    
    st.write(f"Showing data for Q{current_quarter.quarter} {current_quarter.year}")
    st.write(f"Total {metric} for the quarter: {chart_data[metric].sum():,.0f}")
    
    if len(chart_data) < 3:
        st.write(f"Note: Only {len(chart_data)} month(s) of data available for the current quarter.")

# Load data
df = load_data()

# Set up the dashboard
st.title("🎈 Streamlit YouTube Channel Dashboard")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    max_date = df['DATE'].max().date()
    default_start_date = max_date - timedelta(days=27)
    default_end_date = max_date
    start_date = st.date_input("Start date", default_start_date, min_value=df['DATE'].min().date(), max_value=max_date)
    end_date = st.date_input("End date", default_end_date, min_value=df['DATE'].min().date(), max_value=max_date)
    time_frame = st.selectbox(
        "Select time frame",
        ("Daily", "Weekly", "Monthly", "Quarterly"),
    )

# Prepare data based on selected time frame
if time_frame == 'Daily':
    df_display = df
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
    display_metric(col, title, total_value, df_display, column, color)

# Selected Duration Metrics
st.caption("Selected Duration")
mask = (df_display['DATE'].dt.date >= start_date) & (df_display['DATE'].dt.date <= end_date)
df_filtered = df_display.loc[mask]

cols = st.columns(4)
for col, (title, column, color) in zip(cols, metrics):
    display_metric(col, title.split()[-1], df_filtered[column].sum(), df_filtered, column, color)

# Quarterly Chart (if Quarterly is selected)
if time_frame == 'Quarterly':
    metric_to_display = st.selectbox(
        "Select metric for quarterly chart",
        ("VIEWS", "WATCH_HOURS", "NET_SUBSCRIBERS", "LIKES", "COMMENTS", "SHARES")
    )
    display_quarterly_chart(df_display, metric_to_display)

# DataFrame display
with st.expander('See DataFrame'):
    st.dataframe(df)
    st.dataframe(df_display)
