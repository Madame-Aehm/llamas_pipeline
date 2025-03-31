import streamlit as st  
import psycopg
import pandas as pd

st.title("City Weather App")

city = st.selectbox(
    "Select a city",
    ("Berlin", "London", "Sydney"),
)

st.write("You selected:", city)

def get_data(selected_city):
    dbconn = st.secrets["DBCONN"]
    conn = psycopg.connect(dbconn)
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM weather_data WHERE city = %s;
    ''', (selected_city,))
    data = cur.fetchall()
    data_df = pd.DataFrame(data, columns=["date", "city", "temp", "feels", "description"])
    return data_df
    
weather_data = get_data(city)
# print(weather_data)
st.dataframe(weather_data)