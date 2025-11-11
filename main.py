# main.py
from starlette.websockets import WebSocketDisconnect
from fastapi import FastAPI, Depends, HTTPException, responses, WebSocket

from fastapi.middleware.cors import CORSMiddleware

import redis
from moduls import ConnectionManager

# --- FastAPI Application Setup ---

app = FastAPI()
manager = ConnectionManager()
# This allows frontend to communicate with backend
origins = [
    "http://localhost:8000",
    "http://localhost:5173",
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
    try:
        # Connect to Redis
        r = redis.Redis(decode_responses=False)
        res = r.get('boxes')
        r.close()
        # return http response with res as string
        print(f'Sending boxes: {res}, type: {type(res)}')
        return responses.PlainTextResponse(res)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


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
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        manager.disconnect(websocket)

async def set_bit(offset: str, value: str):
    try:
        r = redis.Redis()
        pipe = r.bitfield('boxes')
        pipe.set('u1', offset, int(value))
        _ = pipe.execute()
        r.close()
    except Exception as e:
        print(e)
