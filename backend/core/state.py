from typing import Dict

# In-memory stores (to be replaced by Redis/DB later)
# challenge_id -> correct answer
CAPTCHA_STORE: Dict[str, str] = {}

# token -> username
SESSION_STORE: Dict[str, str] = {}
