from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from app.core.config import settings
from app.core.dependencies import get_db
from app.models.user import User
from app.services.attendance_service import find_best_match, mark_attendance_if_needed

router = APIRouter(tags=["attendance"])

@router.post("/attendance/verify")
async def verify_attendance(
    request: Request,
    image: UploadFile = File(...),
    device_id: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    face_service = request.app.state.face_service
    content = await image.read()

    try:
        query_embedding = await face_service.extract_embedding_from_bytes(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    best_row, best_score = await find_best_match(db, query_embedding)

    if not best_row or best_score < settings.face_match_threshold:
        return {
            "matched": False,
            "message": "Unknown face",
            "confidence": best_score,
        }

    user = await db.scalar(select(User).where(User.id == best_row.user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Matched user not available")

    created, log = await mark_attendance_if_needed(
        db=db,
        user_id=user.id,
        confidence=best_score,
        device_id=device_id,
    )

    return {
        "matched": True,
        "attendance_marked": created,
        "user": {
            "id": str(user.id),
            "person_code": user.person_code,
            "full_name": user.full_name,
        },
        "confidence": best_score,
    }