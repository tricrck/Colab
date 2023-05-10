import streamlit as st
import requests
import datetime

# Define a function to retrieve a random fact about the current date
def get_random_fact(month, day):
    url = f"http://numbersapi.com/{month}/{day}/date"
    response = requests.get(url)
    return response.text

# Define a function to retrieve the weather details for Nairobi, Kenya
def get_weather():
    url = "https://wttr.in/Nairobi?format=%C\n%t\n"
    response = requests.get(url)
    return response.text

# Get the current date
today = datetime.date.today()
month = today.month
day = today.day

# Retrieve a random fact about the current date
fact = get_random_fact(month, day)

# Retrieve the weather details for Nairobi, Kenya
weather = get_weather()

# Set the page title and icon
st.set_page_config(page_title="Fun Facts & Weather", page_icon=":partly_sunny:")

# Add a custom CSS style
st.markdown(
    """
    <style>
    .stApp {
        background-color: #939BA3;
        color: #333333;
        font-family: 'Helvetica', sans-serif;
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add a title and subtitle
st.title("Fun Facts & Weather")
st.markdown("Displaying a random fact about today's date and the weather details for Nairobi, Kenya")

# Add a divider
st.markdown("---")

# Add a widget to display the fact and weather details
col1, col2 = st.beta_columns(2)
with col1:
    st.write(f"**Fun Fact about {today}:**")
    st.write(fact)

with col2:
    st.write(f"**Weather in Nairobi, Kenya:**")
    st.write(weather)
