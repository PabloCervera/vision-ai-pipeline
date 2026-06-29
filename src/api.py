import asyncio
import os
import threading
import cv2
import shutil
from run_pipeline import run_pipeline
from database.event_store import EventStore
from qa_chain import QAChain
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import Response
from contextlib import asynccontextmanager
from starlette.websockets import WebSocketDisconnect
from pydantic import BaseModel

class Question(BaseModel):
    text: str

class VideoPath(BaseModel):
    path: str

event_store = EventStore()
qa_chain = QAChain()
latest_frame = [None]

stop_event = threading.Event()
pipeline_thread = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    stop_event.set()  # para el pipeline si está corriendo al cerrar la API
    print("Cerrando aplicación...")

app = FastAPI(lifespan=lifespan)

app = FastAPI()

def iniciar_pipeline(video_source):
    global pipeline_thread, stop_event
    stop_event.clear()  # resetea el evento por si venía de una parada anterior
    pipeline_thread = threading.Thread(
        target=run_pipeline,
        kwargs={"video_source": video_source, "events": event_store, "latest_frame": latest_frame, "stop_event": stop_event}
    )
    pipeline_thread.daemon = True
    pipeline_thread.start()

@app.get("/events")
def get_events():
    return {"events": event_store.get_all_events()}

@app.get("/status")
def get_status():
    is_running = pipeline_thread is not None and pipeline_thread.is_alive()
    return {
        "status": "running" if is_running else "stopped",
        "total_events": len(event_store.get_all_events())
    }

@app.get("/latest_frame")
def get_latest_frame():
    if latest_frame[0] is None:
        return Response(status_code=204)  
    _, buffer = cv2.imencode(".jpg", latest_frame[0])
    return Response(content=buffer.tobytes(), media_type="image/jpeg")

@app.websocket("/stream")
async def stream_events(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if latest_frame[0] is not None:
                _, buffer = cv2.imencode(".jpg", latest_frame[0])
                await websocket.send_bytes(buffer.tobytes())
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        print("Cliente desconectado del stream")

@app.post("/ask")
def ask_question(question: Question):
    events = event_store.get_recent_events(limit=20)
    answer = qa_chain.ask(question.text, events)
    return {"answer": answer}

@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    video_path = f"data/uploads/{file.filename}"
    os.makedirs("data/uploads", exist_ok=True)
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"video_path": video_path}

@app.post("/start")
def start_pipeline(video: VideoPath):
    iniciar_pipeline(video_source=video.path)
    return {"status": "started"}

@app.post("/stop")
def stop_pipeline():
    stop_event.set()
    return {"status": "stopped"}

@app.post("/clear_events")
def clear_events():
    event_store.clear_events()
    return {"status": "cleared"}