from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.core.ws_manager import manager
from backend.core.database import SessionLocal
from backend.models.models import PrivateMessage, UserSession
import json

router = APIRouter()

@router.websocket("/ws/chat/{token}")
async def websocket_chat(websocket: WebSocket, token: str):
    # Verify token exists in DB to prevent arbitrary connections
    db = SessionLocal()
    user = db.query(UserSession).filter(UserSession.token == token).first()
    if not user:
        db.close()
        await websocket.close(code=1008)
        return
        
    username = user.username
    db.close()

    await manager.connect(token, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                # Expecting payload: {"to": "receiver_token", "content": "..."}
                payload = json.loads(data)
                target_token = payload.get("to")
                content = payload.get("content")
                
                if target_token and content:
                    from backend.core.moderation import moderate_content
                    try:
                        content = moderate_content(content)
                    except ValueError:
                        await manager.send_personal_message({"error": "Content blocked by moderation"}, token)
                        continue
                        
                    # Save to DB
                    db = SessionLocal()
                    msg = PrivateMessage(
                        sender_token=token,
                        receiver_token=target_token,
                        content=content
                    )
                    db.add(msg)
                    db.commit()
                    db.refresh(msg)
                    db.close()
                    
                    # Send to target if online
                    outgoing_msg = {
                        "from": username,
                        "from_token": token,
                        "content": content,
                        "timestamp": msg.created_at.isoformat()
                    }
                    await manager.send_personal_message(outgoing_msg, target_token)
                    
                    # Echo back to sender to confirm delivery
                    await manager.send_personal_message({
                        "status": "sent",
                        "to": target_token,
                        "content": content
                    }, token)
                    
            except json.JSONDecodeError:
                pass # Ignore malformed messages
                
    except WebSocketDisconnect:
        manager.disconnect(token, websocket)

from backend.models.models import BoardMessage, Board

@router.websocket("/ws/boards/{board_name}/{token}")
async def websocket_board_chat(websocket: WebSocket, board_name: str, token: str):
    db = SessionLocal()
    
    # Verify token
    user = db.query(UserSession).filter(UserSession.token == token).first()
    if not user:
        db.close()
        await websocket.close(code=1008)
        return
        
    # Verify board exists
    board = db.query(Board).filter(Board.name == board_name).first()
    if not board:
        db.close()
        await websocket.close(code=1008)
        return

    username = user.username
    db.close()

    await manager.connect_board(board_name, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                content = payload.get("content")
                
                if content:
                    from backend.core.moderation import moderate_content
                    try:
                        content = moderate_content(content)
                    except ValueError:
                        # For websockets we could send an error back or drop the message
                        await manager.send_personal_message({"error": "Content blocked by moderation"}, token)
                        continue
                        
                    db = SessionLocal()
                    msg = BoardMessage(
                        board_name=board_name,
                        sender_token=token,
                        author_name=username,
                        content=content
                    )
                    db.add(msg)
                    db.commit()
                    db.refresh(msg)
                    db.close()
                    
                    outgoing_msg = {
                        "from": username,
                        "content": content,
                        "timestamp": msg.created_at.isoformat()
                    }
                    await manager.broadcast_board(outgoing_msg, board_name)
                    
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect_board(board_name, websocket)
