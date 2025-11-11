# main.py

from fastapi import FastAPI, Depends, HTTPException, responses, websockets

# For Cross-Origin Resource Sharing
from fastapi.middleware.cors import CORSMiddleware

import redis

# --- FastAPI Application Setup ---

app = FastAPI()

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

@app.get("/api/boxes/{offset}")
async def get_boxes(offset: str):
    # Connect to Redis
    r = redis.Redis(decode_responses=True)
    res = r.get('boxes')
    r.close()
    # return http response with `res` as raw bits
    return responses.Response(content=res, media_type="application/octet-stream")


@app.post("/api/boxes/{offset}")
async def flip_box(offset: str):
    try:
        r = redis.Redis(decode_responses=True)
        pipe = r.bitfield('boxes')
        pipe.incrby('u1', offset, 1)
        _ = pipe.execute()
        r.close()
    except Exception as e:
        print(e)
    return responses.Response()