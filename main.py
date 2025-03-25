from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.database.database import engine, Base
from app.routers import users, auth, courses

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LMS API", description="Learning Management System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)

@app.get("/")
async def root():
    return {"message": "Welcome to LMS API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 