from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Header, HTTPException, status
from backend.core.ws_manager import manager
from backend.core.database import SessionLocal, get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from backend.models.models import PrivateMessage, UserSession, BoardMessage, Board
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
                # Expecting payload: {"to": "username", "content": "..."}
                payload = json.loads(data)
                target_username = payload.get("to")
                content = payload.get("content")
                
                if target_username and content:
                    is_whisper = payload.get("is_whisper", False)
                    from backend.core.moderation import moderate_content
                    try:
                        content = moderate_content(content)
                    except ValueError:
                        await manager.send_personal_message({"error": "Content blocked by moderation"}, token)
                        continue
                        
                    db = SessionLocal()
                    # Resolve username to target token
                    target_user = db.query(UserSession).filter(UserSession.username == target_username).first()
                    if not target_user:
                        await manager.send_personal_message({"error": "User not found or offline"}, token)
                        db.close()
                        continue
                        
                    target_token = target_user.token
                        
                    # Save to DB
                    msg = PrivateMessage(
                        sender_token=token,
                        receiver_token=target_token,
                        content=content,
                        is_whisper=is_whisper
                    )
                    db.add(msg)
                    db.commit()
                    db.refresh(msg)
                    db.close()
                    
                    # Send to target if online
                    outgoing_msg = {
                        "from": username,
                        "content": content,
                        "is_whisper": is_whisper,
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

@router.get("/chats")
def get_inbox(x_session_token: str = Header(...), db: Session = Depends(get_db)):
    """Returns a list of usernames the current user has chatted with."""
    user = db.query(UserSession).filter(UserSession.token == x_session_token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    # Find all messages where this user was sender or receiver
    messages = db.query(PrivateMessage).filter(
        or_(
            PrivateMessage.sender_token == x_session_token,
            PrivateMessage.receiver_token == x_session_token
        )
    ).all()
    
    # Extract unique tokens they chatted with
    chat_partner_tokens = set()
    for m in messages:
        if m.sender_token != x_session_token:
            chat_partner_tokens.add(m.sender_token)
        if m.receiver_token != x_session_token:
            chat_partner_tokens.add(m.receiver_token)
            
    # Resolve tokens to usernames
    partners = db.query(UserSession).filter(UserSession.token.in_(list(chat_partner_tokens))).all()
    
    inbox = [{"username": p.username, "token": p.token} for p in partners]
    return inbox

@router.get("/chats/{username}")
def get_chat_history(username: str, x_session_token: str = Header(...), db: Session = Depends(get_db)):
    """Returns message history with a specific username."""
    user = db.query(UserSession).filter(UserSession.token == x_session_token).first()
    target_user = db.query(UserSession).filter(UserSession.username == username).first()
    
    if not user or not target_user:
        raise HTTPException(status_code=400, detail="Invalid user or target")
        
    messages = db.query(PrivateMessage).filter(
        or_(
            and_(PrivateMessage.sender_token == x_session_token, PrivateMessage.receiver_token == target_user.token),
            and_(PrivateMessage.sender_token == target_user.token, PrivateMessage.receiver_token == x_session_token)
        )
    ).order_by(PrivateMessage.created_at.asc()).all()
    
    history = []
    for m in messages:
        sender_name = user.username if m.sender_token == x_session_token else target_user.username
        history.append({
            "from": sender_name,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        })
    return history

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
                    is_whisper = payload.get("is_whisper", False)
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
                        content=content,
                        is_whisper=is_whisper
                    )
                    db.add(msg)
                    db.commit()
                    db.refresh(msg)
                    db.close()
                    
                    outgoing_msg = {
                        "from": username,
                        "content": content,
                        "is_whisper": is_whisper,
                        "timestamp": msg.created_at.isoformat()
                    }
                    await manager.broadcast_board(outgoing_msg, board_name)
                    
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect_board(board_name, websocket)
