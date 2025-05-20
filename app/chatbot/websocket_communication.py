from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime, timezone
import json
from uuid import uuid4
from .agent import handle_user_query

app = FastAPI()

MESSAGE_SENDER_SERVER = "server"
MESSAGE_SENDER_USER = "user"

# Define constants for message types
MESSAGE_TYPE_REQUEST = "request"
MESSAGE_TYPE_USER_MESSAGE = "user_message"
MESSAGE_TYPE_RESPONSE = "response"
MESSAGE_TYPE_ERROR = "error"
MESSAGE_TYPE_INIT = "init"

class WebSocketMessage(BaseModel):
    type: str
    timestamp: str
    session_id: str
    payload: dict
    sender: str

class WebSocketResponse(BaseModel):
    type: str
    timestamp: str
    session_id: str
    payload: dict
    sender: str

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid4())
    init_message = WebSocketResponse(
        type=MESSAGE_TYPE_INIT,
        timestamp=datetime.now(timezone.utc).isoformat() + 'Z',
        session_id=session_id,
        payload={},
        sender=MESSAGE_SENDER_SERVER
    )
    await websocket.send_text(json.dumps(init_message.model_dump()))
    print(f"send init message to client {init_message.model_dump()}")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            print(f"receive data from client {message}")
            response = process_message(message)
            await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        print("Client disconnected")

# Process incoming messages
def process_message(data: dict) -> dict:
    if data.get('session_id') is None:
        data['session_id'] = str(uuid4())
    message = WebSocketMessage(**data)
    if message.type == MESSAGE_TYPE_USER_MESSAGE:
        print(f"process_message message: {message}")
        print(f"process_message message.payload: {message.payload}")
        user_query = message.payload.get('text')
        response_text = handle_user_query(user_query)
        response = WebSocketResponse(
            type=MESSAGE_TYPE_RESPONSE,
            timestamp=datetime.now(timezone.utc).isoformat() + 'Z',
            session_id=message.session_id,
            payload={
                'response': response_text,
                'metadata': {
                    'intent': 'query_response',
                    'source': 'vector_db'
                }
            },
            sender=MESSAGE_SENDER_SERVER
        )
    elif message.type == MESSAGE_TYPE_ERROR:
        response = WebSocketResponse(
            type=MESSAGE_TYPE_ERROR,
            timestamp=datetime.now(timezone.utc).isoformat() + 'Z',
            session_id=message.session_id,
            payload={
                'error': 'An error occurred while processing the message.'
            },
            sender=MESSAGE_SENDER_SERVER
        )
    else:
        response = WebSocketResponse(
            type=MESSAGE_TYPE_ERROR,
            timestamp=datetime.now(timezone.utc).isoformat() + 'Z',
            session_id=message.session_id,
            payload={
                'error': 'Unknown message type.'
            },
            sender=MESSAGE_SENDER_SERVER
        )
    return response.model_dump()

# Start the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 