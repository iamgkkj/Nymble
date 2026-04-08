# Project Context: Nymble

## Current Strategy & Roadmap

We are following a phased approach to build out the core features without over-engineering.

### Phase 1: Basic setup, CAPTCHA, Identity (Completed)
- [x] Backend setup with FastAPI
- [x] CAPTCHA system mock/validation
- [x] Anonymous identity generation

### Phase 2: Board system + post feed (Completed)
- [x] Create board definitions and initial database schema
- [x] Board retrieval endpoints
- [x] Create post and get posts endpoints with auth
### Phase 3: Image posting + replies (Completed)
- [x] Configure backend static file serving
- [x] Support image uploads for posts
- [x] Add threads and replies functionality
### Phase 4: Token-based session restore (Completed)
- [x] Create SQLite-backed Session model (`UserSession`)
- [x] Persist identities across server restarts
- [x] Integrate session header validation in all secure endpoints
### Phase 5: Real-time private chat (Completed)
- [x] Create WebSocket connection manager for live message routing
- [x] Create persistent PrivateMessage DB model
- [x] Build isolated 1-to-1 token-based WebSocket channels
### Phase 6: Board chatrooms (Completed)
- [x] Extend WebSocket connection manager for public rooms
- [x] Create persistent BoardMessage DB model
- [x] Build board-specific WebSocket lobby endpoint
### Phase 7: Content moderation (Completed)
- [x] Create centralized backend keyword filtering
- [x] Detect banned terminologies to completely block request payloads
- [x] Mask standard sensitive words dynamically in text payloads
### Phase 8: Whisper mode (Completed)
- [x] Add `is_whisper` flag to `Post`, `Reply`, `PrivateMessage`, and `BoardMessage`
- [x] Integrate flag in all JSON schemas and WebSocket handlers
### Phase 9: UI polish + theme toggle (Pending)
### Phase 10: Documentation + scripts (Pending)

## Completed Features
*(None yet)*

## Known Issues / Notes
- Just started project initialization.
- Need to keep code modular and readable.
