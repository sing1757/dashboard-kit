import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Streamlit YouTube Channel Dashboard", layout="wide")

def load_data():
    data = pd.read_csv("youtube_channel_data.csv")
    data['DATE'] = pd.to_datetime(data['DATE'])
    data['NET_SUBSCRIBERS'] = data['SUBSCRIBERS_GAINED'] - data['SUBSCRIBERS_LOST']
    return data

df = load_data()

st.title("🎈 Streamlit YouTube Channel Dashboard")

logo_icon = "images/streamlit-mark-color.png"
logo_image = "images/streamlit-logo-primary-colormark-lighttext.png"
st.logo(icon_image=logo_icon, image=logo_image)

with st.sidebar:
    st.header("⚙️ Settings")
    start_date = st.date_input("Start date", df['DATE'].min())
    end_date = st.date_input("End date", df['DATE'].max())

    time_frame = st.selectbox(
        "Select time frame",
        ("Daily", "Cumulative"),
    )

with st.expander("See DataFrame"):
    st.dataframe(df)
