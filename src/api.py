import asyncio
import threading
import cv2
from run_pipeline import run_pipeline
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
from starlette.websockets import WebSocketDisconnect

events = []
latest_frame = [None]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # código de arranque (lo que antes iba en @app.on_event("startup"))
    thread = threading.Thread(target=iniciar_pipeline)
    thread.daemon = True
    thread.start()
    
    yield  # aquí la aplicación queda "corriendo"
    
    # código de cierre (se ejecutaría al parar el servidor)
    print("Cerrando aplicación...")

app = FastAPI(lifespan=lifespan)

def iniciar_pipeline():
    run_pipeline(video_source="test.mp4", events=events, latest_frame=latest_frame)

@app.get("/events")
def get_events():
    return {"events": events}

@app.get("/status")
def get_status():
    return {"status": "running", "total_events": len(events)}

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

