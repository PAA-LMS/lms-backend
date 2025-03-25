# LMS Backend

This is the backend for the Learning Management System built with FastAPI.

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Mac/Linux:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
uvicorn main:app --reload
```

The server will start at http://localhost:8000

## API Documentation

Once the server is running, you can access:
- API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc 