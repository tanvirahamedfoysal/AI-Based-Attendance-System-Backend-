from fastapi import FastAPI

from app.api.routes import health, users, attendance
from app.services.face_service import FaceService

app = FastAPI(title="Face Attendance API")

@app.on_event("startup")
async def startup_event():
    app.state.face_service = FaceService()

app.include_router(health.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1")