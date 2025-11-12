# OMCB Backend

This directory contains the Python-based backend for the OMCB project. It is built with FastAPI and uses Redis for data storage and WebSockets for real-time communication with the frontend.

## Prerequisites

Before you begin, ensure you have the following installed on your local machine:
- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (a fast Python package installer and resolver)
- Git

## Local Development Setup

The following steps will guide you through setting up and running the backend server.

### 1. Clone the Repository

First, clone the repository to your local machine and navigate into the backend directory.

```bash
git clone https://github.com/urivinter/OMCB-back
cd omcb-back
```

### 2. Set Up the Environment and Dependencies

This project uses `uv` to handle both the virtual environment and package installation.

```bash
# Sync dependencies and create virtual environment
uv sync
```

### 3. Prepare the Database

1.  **Start Redis**: Make sure your local Redis server is running. You can typically start it by running `redis-server` in your terminal.

2.  **Initialize Bitfield**: The application requires a Redis bitfield named `boxes` to be initialized. This command creates a bitfield large enough for 200,000 "boxes". **This only needs to be done once.**

    ```bash
    redis-cli BITFIELD boxes SET u1 199999 0
    ```

### 4. Run the Application Server

With the virtual environment activated and Redis running, start the backend server using Uvicorn:

```bash
uv run uvicorn main:app --reload
```

The backend will now be running at `http://localhost:8000` and is configured to accept connections from a frontend at `http://localhost:5173`.
