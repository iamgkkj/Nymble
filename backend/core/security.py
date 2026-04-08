import random
import secrets

from .names import ADJECTIVES, NOUNS

def generate_anonymous_name() -> str:
    """Generates a random anonymous name like 'Happy Squirrel'."""
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    return f"{adj} {noun}"

def generate_session_token() -> str:
    """Generates a unique hexadecimal token for user identity."""
    return secrets.token_hex(32)
