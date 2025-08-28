from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import UUID


class GenerateQuizRequest(BaseModel):
    topic: str
    difficulty: str = Field(default="medium", description="Quiz difficulty level")
    num_questions: int = Field(gt=0, le=50, description="Number of questions to generate")


class GenerateQuizResponse(BaseModel):
    message: str
    quizId: UUID


class QuizQuestion(BaseModel):
    questionId: int
    questionText: str
    options: Dict[str, str]
    correct_answer: Dict[str, str]
    explanation: str


class QuizBundle(BaseModel):
    quizId: UUID
    topic: str
    questions: List[QuizQuestion]
    difficulty: str
    createdAt: str


class QuizDetailResponse(BaseModel):
    quizId: UUID
    topic: str
    difficulty: str
    status: str
    questions: List[QuizQuestion]


class SubmitAnswer(BaseModel):
    questionId: int
    selectedOption: str


class SubmitQuizRequest(BaseModel):
    answers: List[SubmitAnswer]


class QuestionResult(BaseModel):
    questionId: int
    yourAnswer: str
    correctAnswer: str
    isCorrect: bool
    explanation: str


class SubmitQuizResponse(BaseModel):
    quizId: UUID
    score: int
    correctAnswers: int
    totalQuestions: int
    results: List[QuestionResult]


