from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api.routes import router as auth_router
from backend.api.boards import router as boards_router
from backend.api.posts import router as posts_router
from backend.api.chat import router as chat_router
from backend.core.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nymble API", description="Privacy-first, anonymous social interaction platform.")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded media
import os
os.makedirs("uploaded_media", exist_ok=True)
app.mount("/media", StaticFiles(directory="uploaded_media"), name="media")

app.include_router(auth_router, prefix="/api", tags=["Auth"])
app.include_router(boards_router, prefix="/api", tags=["Boards"])
app.include_router(posts_router, prefix="/api", tags=["Posts"])
app.include_router(chat_router, tags=["Chat"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Nymble Backend is running."}
