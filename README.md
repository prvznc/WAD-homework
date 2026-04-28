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