import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal, Base, engine
from backend.models.models import Board, Post

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

boards = ["anime", "academics", "technology", "movies", "games", "exams", "placements", "travel", "hostel", "dayscholar"]

dummy_content = [
    "Just finished watching the latest episode, that animation was insane!",
    "Does anyone have the notes for the last lecture?",
    "I can't believe they broke API compatibility again...",
    "What's everyone playing this weekend?",
    "Need roommates for next semester, DM me.",
    "This new framework is actually pretty fast.",
    "Can't decide between these two offers. Thoughts?",
    "Any good food places around campus open late?",
    "The exam was totally unfair, half the questions weren't in the syllabus.",
    "Finally booked my tickets for the trip!"
]

whisper_content = [
    "I might actually fail this class...",
    "To be honest, I think the new policy is a terrible idea.",
    "I have no idea what I'm doing in my project.",
    "I feel like everyone else is getting placements except me."
]

author_names = ["Happy Squirrel", "Sleepy Panda", "Fast Fox", "Brave Bear", "Smart Owl"]

for board_name in boards:
    board = db.query(Board).filter(Board.name == board_name).first()
    if not board:
        board = Board(name=board_name, description=f"Discussion for {board_name}")
        db.add(board)
        db.commit()
    
    # Add 2-3 standard posts
    for _ in range(random.randint(2, 3)):
        post = Post(
            board_name=board_name,
            author_name=random.choice(author_names),
            content=random.choice(dummy_content),
            is_whisper=False
        )
        db.add(post)
    
    # Add 1 whisper post
    post = Post(
        board_name=board_name,
        author_name=random.choice(author_names),
        content=random.choice(whisper_content),
        is_whisper=True
    )
    db.add(post)

db.commit()
db.close()
print("Seeding complete!")
