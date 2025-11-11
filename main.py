# main.py

from fastapi import FastAPI, Depends, HTTPException, responses, WebSocket

from fastapi.middleware.cors import CORSMiddleware

import redis
import json
from moduls import ConnectionManager

# --- FastAPI Application Setup ---

app = FastAPI()
manager = ConnectionManager()
# This allows frontend to communicate with backend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- API Endpoints ---

# Hello world
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/boxes/")
async def get_boxes():
    # Connect to Redis
    r = redis.Redis(decode_responses=True)
    res = r.get('boxes')
    r.close()
    # return http response with `res` as raw bits
    return responses.Response(content=res, media_type="application/octet-stream")

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            offset, value = data['offset'], data['value']
            print(data)
            await set_bit(offset, value)
            await manager.broadcast(offset, value)
    finally:
        manager.disconnect(websocket)

async def set_bit(offset: str, value: str):
    try:
        r = redis.Redis(decode_responses=True)
        pipe = r.bitfield('boxes')
        pipe.set('u1', offset, int(value))
        _ = pipe.execute()
        r.close()
    except Exception as e:
        print(e)