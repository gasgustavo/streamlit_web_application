import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
    'Motor_Vehicle_Collisions_-_Crashes_small.csv'
)

st.title('Motor Vehicle Collisions in New York city')
st.markdown("This application is a Streamlit dashboard that can be used"
"to analize motor vehicle collisions in NYC")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(
        DATA_URL,
        nrows=nrows,
        parse_dates={"date/time": ["CRASH_DATE", "CRASH_TIME"]}
    )
    data.dropna(subset=["LATITUDE", "LONGITUDE"], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    return data

n_rows = st.sidebar.slider(
    label="Number of rows of data to open",
    min_value=0,
    max_value=1000000,
    value=100000,
    step=1000
)

data = load_data(n_rows)
original_data = data.copy()

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons in vehicles collisions", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

st.header("How many collisions occur during a given time?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data["date/time"].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time','latitude','longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0,1000],
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour+1) % 24))
filtered_data = data[
    (data['date/time'].dt.hour >= hour) &
    (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(
    filtered_data['date/time'].dt.minute, bins=60,range=(0,60)
)[0]
chart_data = pd.DataFrame({'minute': range(60), "crashes":hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

number_of_ranking_itens = 5
st.header("Top {} dangerous streets bt affected type".format(number_of_ranking_itens))
select = st.selectbox("Affected type of people", ["Pedestrians", "Cyclists", "Motorists"])
column_name = "injured_{}".format(select.lower())
st.write(
        original_data
            .query("{} >= 1".format(column_name))[["on_street_name", column_name]]
            .sort_values(by=column_name, ascending=False)
            .dropna(how="any")
            .iloc[:number_of_ranking_itens]
    )

if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)
