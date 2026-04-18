import cv2
import numpy as np
from insightface.app import FaceAnalysis


class FaceService:
    def __init__(self) -> None:
        self.app = FaceAnalysis(name="buffalo_l")
        self.app.prepare(ctx_id=0)

    @staticmethod
    def normalize(vec: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return vec / norm

    async def extract_embedding_from_bytes(self, image_bytes: bytes) -> np.ndarray:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image")

        faces = self.app.get(img)
        if len(faces) == 0:
            raise ValueError("No face detected")
        if len(faces) > 1:
            raise ValueError("Multiple faces detected")

        embedding = np.array(faces[0].embedding, dtype=np.float32)
        return self.normalize(embedding)

    async def average_embeddings(self, embeddings: list[np.ndarray]) -> np.ndarray:
        avg = np.mean(np.stack(embeddings), axis=0)
        return self.normalize(avg)