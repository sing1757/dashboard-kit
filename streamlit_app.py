import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Streamlit YouTube Channel Dashboard", layout="wide")

df = pd.read_csv("youtube_channel_data.csv")

st.title("🎈 Streamlit YouTube Channel Dashboard")

with st.sidebar:
    st.header("⚙️ Settings")
    start_date = st.date_input("Start date", df['DATE_DAY'].min())
    end_date = st.date_input("End date", df['DATE_DAY'].max())

    time_frame = st.selectbox(
        "Select time frame",
        ("Daily", "Cumulative"),
    )

