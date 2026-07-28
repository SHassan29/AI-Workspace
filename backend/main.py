import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine


# ---------------------------------------------------------
# Environment variables
# ---------------------------------------------------------

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key) if openai_api_key else None


# ---------------------------------------------------------
# Database setup
# ---------------------------------------------------------

models.Base.metadata.create_all(bind=engine)


def get_db():
    """
    Creates a database session for each request and closes it afterwards.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="AI Workspace API",
    description="FastAPI backend for tasks and an AI software assistant.",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    completed: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    completed: bool | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)


# ---------------------------------------------------------
# Basic routes
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to the AI Workspace API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "ai_configured": client is not None,
    }


# ---------------------------------------------------------
# Task CRUD routes
# ---------------------------------------------------------

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()

    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id)
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@app.post("/tasks", status_code=201)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    new_task = models.Task(
        title=task_data.title,
        completed=task_data.completed,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id)
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    if task_data.title is not None:
        task.title = task_data.title

    if task_data.completed is not None:
        task.completed = task_data.completed

    db.commit()
    db.refresh(task)

    return task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id)
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully",
        "task_id": task_id,
    }


# ---------------------------------------------------------
# AI chat route
# ---------------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):
    if client is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "OpenAI API key is missing. "
                "Add OPENAI_API_KEY to your .env file."
            ),
        )

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=(
                "You are an AI software engineering assistant. "
                "Help users understand programming, React, FastAPI, "
                "databases, Docker, cloud computing and artificial "
                "intelligence. Give clear, accurate and beginner-friendly "
                "answers. When reviewing code, explain errors and provide "
                "a corrected example."
            ),
            input=request.message,
        )

        return {
            "reply": response.output_text,
        }

    except Exception as error:
        print(f"OpenAI API error: {error}")

        raise HTTPException(
            status_code=500,
            detail="The AI service could not generate a response.",
        )