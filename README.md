# Nymble

Privacy-first, anonymous, low-pressure social interaction platform where users can communicate without identity pressure.

## Philosophy

- **No login system**: Entry is verified simply via CAPTCHA.
- **Anonymous but structured identity**: You are assigned a fun, ephemeral identity (like "Happy Squirrel").
- **Low-pressure UX**: No likes, no followers, no notifications spam.
- **Safety-first**: Keyword filtering and moderation.

## Architecture

- **Backend**: FastAPI (Python) for API and WebSockets.
- **Database**: SQLite (upgrade-ready for Postgres later).
- **Frontend**: Vanilla JS / Minimal UI (to be developed).

### Token System

The ONLY way to restore your session or access the platform is through a unique hex token generated for you after solving the CAPTCHA. This token is stored locally in your browser. There is no email, password, or third-party login.

### Moderation System

A rigorous backend filter evaluates all public interactions to maintain a safe environment, blocking or masking sensitive and abusive content.

## Setup Instructions

### Prerequisites
- Python 3.10+
- Virtualenv/Pip

### Linux / macOS
Run the setup script from the root directory:
```bash
./setup.sh
```

### Windows
Run the batch script:
```bat
setup.bat
```

## Screenshots

*(Placeholders for future screenshots)*
- Home Board
- Thread View
- Chat Interface
