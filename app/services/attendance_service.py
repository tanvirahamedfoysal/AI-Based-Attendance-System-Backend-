from datetime import date
import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.face_embedding import FaceEmbedding
from app.models.attendance_log import AttendanceLog


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


async def find_best_match(db: AsyncSession, query_embedding: np.ndarray):
    result = await db.execute(select(FaceEmbedding))
    rows = result.scalars().all()

    if not rows:
        return None, 0.0

    best_row = None
    best_score = -1.0

    for row in rows:
        stored = np.array(row.embedding, dtype=np.float32)
        score = cosine_similarity(query_embedding, stored)
        if score > best_score:
            best_score = score
            best_row = row

    return best_row, best_score


async def mark_attendance_if_needed(
    db: AsyncSession,
    user_id,
    confidence: float,
    device_id: str | None = None,
):
    today = date.today()

    existing = await db.scalar(
        select(AttendanceLog).where(
            AttendanceLog.user_id == user_id,
            AttendanceLog.attendance_date == today,
        )
    )
    if existing:
        return False, existing

    log = AttendanceLog(
        user_id=user_id,
        confidence=confidence,
        attendance_date=today,
        device_id=device_id,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return True, log