from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.user import User
from app.models.face_embedding import FaceEmbedding

router = APIRouter(tags=["users"])

@router.post("/users/register")
async def register_user(
    request: Request,
    person_code: str = Form(...),
    full_name: str = Form(...),
    images: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    if len(images) != 5:
        raise HTTPException(status_code=400, detail="Exactly 5 images are required")

    existing = await db.scalar(select(User).where(User.person_code == person_code))
    if existing:
        raise HTTPException(status_code=409, detail="person_code already exists")

    face_service = request.app.state.face_service

    embeddings = []
    for image in images:
        content = await image.read()
        try:
            emb = await face_service.extract_embedding_from_bytes(content)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"{image.filename}: {str(e)}")
        embeddings.append(emb)

    avg_embedding = await face_service.average_embeddings(embeddings)

    user = User(
        person_code=person_code,
        full_name=full_name,
    )
    db.add(user)
    await db.flush()

    face_embedding = FaceEmbedding(
        user_id=user.id,
        embedding=avg_embedding.tolist(),
    )
    db.add(face_embedding)

    await db.commit()
    await db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": str(user.id),
        "person_code": user.person_code,
        "full_name": user.full_name,
    }