# API Server

A FastAPI-based backend service with user authentication, file uploads, and image management using ImageKit.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **User Authentication** - JWT-based authentication with fastapi-users
- **File Uploads** - Image and video upload support with ImageKit integration
- **Async Database** - SQLAlchemy with async SQLite support
- **Streamlit Frontend** - Interactive web interface for testing

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Uvicorn
- **Authentication**: fastapi-users with JWT
- **Database**: SQLite with async support (aiosqlite)
- **File Storage**: ImageKit
- **Frontend**: Streamlit
- **Package Manager**: uv


## Running the Application

Start the API Server
uv run .\main.py

The server will start on `http://0.0.0.0:8000`

Access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Run the Streamlit Frontend
uv run streamlit run .\frontend.py #In a separate terminal
The Streamlit app will open at `http://localhost:8501`
