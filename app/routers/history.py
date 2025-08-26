from fastapi import APIRouter
from typing import List
from uuid import UUID

from ..schemas import HistoryItem
from ..store import HARDCODED_QUIZ_ID


router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history", response_model=List[HistoryItem])
async def get_history():
    return [
        HistoryItem(
            quizId=HARDCODED_QUIZ_ID,
            topic="The Roman Empire",
            dateTaken="2025-08-26T16:00:00Z",
            score=80,
        ),
        HistoryItem(
            quizId=UUID("e1a2c3b4-d5e6-f7a8-b9c0-d1e2f3a4b5c6"),
            topic="Quantum Mechanics",
            dateTaken="2025-08-25T11:30:00Z",
            score=90,
        ),
    ]


