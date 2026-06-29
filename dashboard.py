import streamlit as st
import requests

def dashboard():
    st.title("Dashboard de Eventos")

    if "phase" not in st.session_state:
        st.session_state.phase = "idle"
    
    if st.session_state.phase == "idle":
        st.subheader("Sube un video para iniciar el análisis")
        upload_file()

    elif st.session_state.phase == "processing":
        st.subheader("Procesando vídeo...")
        with st.spinner("Analizando..."):
            check_status()
        if st.button("Detener"):
            requests.post("http://localhost:8000/stop")
            st.session_state.phase = "finished"
            st.rerun()

    elif st.session_state.phase == "finished":
        st.subheader("Eventos detectados")
        show_results()
        st.subheader("Pregunta sobre la escena")
        chat_qa()

        if st.button("Volver"):
            requests.post("http://localhost:8000/clear_events")
            st.session_state.phase = "idle"
            st.rerun()  

def upload_file():
    uploaded_file = st.file_uploader("Sube un video", type=["mp4", "avi", "mov"])
    if uploaded_file is not None:
        if st.button("Iniciar"):
            st.write("Subiendo y procesando el video...")
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post("http://localhost:8000/upload_video", files=files)
            if response.status_code == 200:
                video_path = response.json()["video_path"]
                requests.post("http://localhost:8000/start", json={"path": video_path})
                st.session_state.phase = "processing"
                st.rerun()
            else:
                st.error("Error al subir el video.")       

@st.fragment(run_every=1)
def check_status():
    response = requests.get("http://localhost:8000/status")
    if response.status_code == 200:
        status = response.json()
        if status['status'] == "stopped":
            st.session_state.phase = "finished"
            st.rerun()

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

def show_results():
    response = requests.get("http://localhost:8000/events")
    if response.status_code == 200:
        events = response.json()["events"]
        st.write(f"Total de eventos: {len(events)}")
        for event in events:
            st.write(f"**{event['timestamp']}** — Riesgo: {event['risk_level']}")
            st.write(event['alert'])
            if event['frame_path']:
                st.image(event['frame_path'])
            st.divider()
        
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