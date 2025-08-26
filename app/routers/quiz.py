from uuid import UUID
from fastapi import APIRouter, HTTPException
from typing import List

from ..schemas import (
    GenerateQuizRequest,
    GenerateQuizResponse,
    QuizDetailResponse,
    SubmitQuizRequest,
    SubmitQuizResponse,
    QuestionResult,
    QuizQuestion,
)
from ..store import HARDCODED_QUIZ_ID


router = APIRouter(prefix="/api/quiz", tags=["quiz"])


# Phase 1 static dataset
HARDCODED_QUESTIONS: List[QuizQuestion] = [
    QuizQuestion(
        questionId=1,
        questionText="Who was the first emperor of Rome?",
        options={"A": "Julius Caesar", "B": "Augustus", "C": "Nero", "D": "Constantine"},
    )
]
for i in range(2, 11):
    HARDCODED_QUESTIONS.append(
        QuizQuestion(
            questionId=i,
            questionText=f"Sample question {i}?",
            options={"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
        )
    )


@router.post("/generate", response_model=GenerateQuizResponse, status_code=202)
async def generate_quiz(payload: GenerateQuizRequest):
    return GenerateQuizResponse(message="Quiz generation has been started.", quizId=HARDCODED_QUIZ_ID)


@router.get("/{quiz_id}", response_model=QuizDetailResponse)
async def get_quiz(quiz_id: UUID):
    if quiz_id != HARDCODED_QUIZ_ID:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return QuizDetailResponse(
        quizId=HARDCODED_QUIZ_ID,
        topic="The Roman Empire",
        status="completed",
        questions=HARDCODED_QUESTIONS,
    )


@router.post("/{quiz_id}/submit", response_model=SubmitQuizResponse)
async def submit_quiz(quiz_id: UUID, payload: SubmitQuizRequest):
    if quiz_id != HARDCODED_QUIZ_ID:
        raise HTTPException(status_code=404, detail="Quiz not found")
    results: List[QuestionResult] = [
        QuestionResult(
            questionId=1,
            yourAnswer="B",
            correctAnswer="B",
            isCorrect=True,
            explanation=(
                "Augustus is considered the first Roman Emperor, marking the end of the Roman Republic."
            ),
        )
    ]
    for i in range(2, 11):
        is_correct = (i % 2 == 0)
        results.append(
            QuestionResult(
                questionId=i,
                yourAnswer="A" if not is_correct else "B",
                correctAnswer="B" if is_correct else "C",
                isCorrect=is_correct,
                explanation=f"Explanation for question {i}.",
            )
        )

    return SubmitQuizResponse(
        quizId=HARDCODED_QUIZ_ID,
        score=80,
        correctAnswers=8,
        totalQuestions=10,
        results=results,
    )


