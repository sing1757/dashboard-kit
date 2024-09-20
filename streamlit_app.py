import streamlit as st
import pandas as pd
from datetime import timedelta

# Set page config
st.set_page_config(page_title="Streamlit YouTube Channel Dashboard", layout="wide")

@st.cache_data
def get_data(_session):
    query = """
    SELECT * FROM MARKETING.RAW_YOUTUBE_ANALYTICS_STREAMLIT_YOUTUBE.YOUTUBE__VIDEO_REPORT
    """
    data = _session.sql(query).collect()
    return data

@st.cache_data
def load_and_aggregate_data():
    df = pd.DataFrame(get_data(session))
    df['DATE'] = pd.to_datetime(df['DATE_DAY'])
    df['NET_SUBSCRIBERS'] = df['SUBSCRIBERS_GAINED'] - df['SUBSCRIBERS_LOST']
    df['WATCH_HOURS'] = df['WATCH_TIME_MINUTES'] / 60
    return df

def aggregate_data(df, freq):
    df_agg = df.resample(freq, on='DATE').agg({
        'VIEWS': 'sum',
        'WATCH_HOURS': 'sum',
        'NET_SUBSCRIBERS': 'sum',
        'LIKES': 'sum',
        'COMMENTS': 'sum',
        'SHARES': 'sum',
        'AVERAGE_VIEW_DURATION_PERCENTAGE': 'mean'
    }).reset_index()
    return df_agg

def get_weekly_data(df):
    return aggregate_data(df, 'W-MON')

def get_monthly_data(df):
    return aggregate_data(df, 'M')

def get_quarterly_data(df):
    return aggregate_data(df, 'Q')

def load_pre_data():
    return pd.DataFrame({
        "DATE": pd.to_datetime(['2024-02-11 00:00:00']),
        "NET_SUBSCRIBERS": 12861,
        "VIEWS": 604780,
        "WATCH_HOURS": 24934.2,
        "LIKES": 9396
    })

def format_with_commas(number):
    return f"{number:,}"

def create_metric_chart(df, column, color, height=150):
    chart_df = df[["DATE", column]].set_index("DATE")
    return st.area_chart(chart_df, color=color, height=height)

def display_metric(col, title, value, df, column, color):
    with col:
        with st.container(border=True):
            st.metric(title, format_with_commas(value))
            create_metric_chart(df, column, color)

# Load data
df = load_and_aggregate_data()
df_pre = load_pre_data()

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
        ("Daily", "Weekly", "Monthly", "Quarterly", "Cumulative"),
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
elif time_frame == 'Cumulative':
    df_display = pd.concat([df_pre, df], ignore_index=True)
    for column in ['NET_SUBSCRIBERS', 'VIEWS', 'WATCH_HOURS', 'LIKES']:
        df_display[column] = df_display[column].cumsum()

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
    total_value = df[column].sum() + df_pre[column].iloc[0]
    display_metric(col, title, total_value, df_display, column, color)

# Selected Duration Metrics
st.caption("Selected Duration")

mask = (df_display['DATE'].dt.date >= start_date) & (df_display['DATE'].dt.date <= end_date)
df_filtered = df_display.loc[mask]

cols = st.columns(4)
for col, (title, column, color) in zip(cols, metrics):
    display_metric(col, title.split()[-1], df_filtered[column].sum(), df_filtered, column, color)

# DataFrame display
with st.expander('See DataFrame'):
    st.dataframe(df)
    st.dataframe(df_display)
