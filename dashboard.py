import streamlit as st
import requests

def dashboard():
    st.title("Dashboard de Eventos")
    
    update_frame()
    update_events()
    
    st.subheader("Pregunta sobre la escena")
    chat_qa()
        
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
        
def chat_qa():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    question = st.chat_input("Escribe tu pregunta...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        response = requests.post("http://localhost:8000/ask", json={"text": question})
        if response.status_code == 200:
            answer = response.json()["answer"]
            st.session_state.messages.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.write(answer)
        
        
if __name__ == "__main__":
    dashboard()