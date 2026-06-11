import asyncio
import threading
from run_pipeline import run_pipeline
from fastapi import FastAPI

app = FastAPI()
events = []

def iniciar_pipeline():
    run_pipeline(video_source="test.mp4", events=events)

@app.get("/events")
def get_events():
    return {"events": events}

@app.get("/status")
def get_status():
    return {"status": "running", "total_events": len(events)}

@app.websocket("/stream")
async def stream_events(websocket):
    await websocket.accept()
    while True:
        # enviar datos al cliente
        await websocket.send_text("frame")
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup():
    thread = threading.Thread(target=iniciar_pipeline)
    thread.daemon = True  # se cierra cuando cierra el programa principal
    thread.start()