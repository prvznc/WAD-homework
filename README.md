# LLM Chat Application - Homework Project

Student: Perevoznic Valeria
Group: N4150c

# Instruction to run the app

1. git clone "repo"
2. cd "project"
3. copy (or cp for Linux) .env.example .env # change variables in the .env file
4. create virtual environment
5. pip install -r requirements.txt
6. docker compose up -d
7. alembic upgrade head
8. uvicorn app.main:app --reload

# Architecture

I have chosen frontend mode - SPA (Single Page Application), because it has one HTML file loaded once with no page reloads.

How the Authentification works (JWT + Refresh Tokens + Redis):

1. User logs in and backend issues these tokens:
    - access_token (JWT, 15 mins) that are sent in authorization header;
    - refresh_token (random UUID, 7 days) that are stored in Redis with TTL

2. API requests include:
    authorization: Bearer 'access_token'

3. If access_token expires (401 unauthorized):
    - frontend calls POST /api/auth/refresh?refresh_token=...;
    - backend validates token in Redis and issues new pair;
    - old token is deleted

4. After logout refresh_token is removed from Redis and frontend clears localStorage.