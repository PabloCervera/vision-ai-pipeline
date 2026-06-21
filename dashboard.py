import streamlit as st
import requests
import time

def dashboard():
    st.title("Dashboard de Eventos")
    
    update_frame()
    update_events()
        
@st.fragment(run_every=0.1)
def update_frame():
    response = requests.get("http://localhost:8000/latest_frame")
    if response.status_code == 200:
        st.image(response.content, channels="BGR")
        
@st.fragment(run_every=1)
def update_events():
    response = requests.get("http://localhost:8000/events")
    if response.status_code == 200:
        events = response.json()
        st.write(f"Total de eventos: {len(events['events'])}")
        for event in events['events']:
            st.write(event)
        
if __name__ == "__main__":
    dashboard()