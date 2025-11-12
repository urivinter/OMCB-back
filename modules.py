from fastapi import WebSocket
import redis

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, offset: int, value: int):
        msg = encode(offset, value)
        for connection in self.active_connections:
            await connection.send_bytes(msg)

def decode(data: bytes) -> tuple[int, int]:
    """Decode 3-byte binary format to (offset, value)"""
    if len(data) != 3:
        raise ValueError(f"Error:   Expected 3 bytes, got {len(data)}")

    # Extract offset from 3 bytes (20 bits total)
    offset = data[0] | (data[1] << 8) | ((data[2] & 0x0F) << 16)

    # Extract value from high bit of third byte
    value = (data[2] >> 4) & 1

    return offset, value

def encode(offset: int, value: int) -> bytes:
    """Encode (offset, value) to 3-byte binary format"""
    data = bytearray(3)
    data[0] = offset & 0xff
    data[1] = (offset >> 8) & 0xff
    data[2] = ((offset >> 16) & 0xff) | (value << 4)
    return bytes(data)

def set_bit(offset: int, value: int):
    try:
        r = redis.Redis()
        pipe = r.bitfield('boxes')
        pipe.set('u1', offset, value)
        _ = pipe.execute()
        r.close()
    except Exception as e:
        print(e)

async def get_all():
    # Connect to Redis
    r = redis.Redis(decode_responses=False)
    res = r.get('boxes')
    r.close()
    return res
