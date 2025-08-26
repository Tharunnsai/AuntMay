from typing import Dict, List
from uuid import UUID

from .schemas import HistoryItem, QuizRecord


# Simulated store just for Phase 1/2
HARDCODED_USER_ID = UUID("d290f1ee-6c54-4b01-90e6-d701748f0851")
HARDCODED_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
HARDCODED_QUIZ_ID = UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")

# In-memory stores
QUIZZES: Dict[UUID, QuizRecord] = {}
USER_HISTORY: Dict[UUID, List[HistoryItem]] = {}


