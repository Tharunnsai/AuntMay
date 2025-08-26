from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import UUID


class SignupRequest(BaseModel):
    email: str
    password: str


class SignupResponse(BaseModel):
    message: str
    userId: UUID


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str
    accessToken: str


class GenerateQuizRequest(BaseModel):
    topic: str
    difficulty: str
    num_questions: int = Field(gt=0, le=50)


class GenerateQuizResponse(BaseModel):
    message: str
    quizId: UUID


class QuizQuestion(BaseModel):
    questionId: int
    questionText: str
    options: Dict[str, str]


class QuizDetailResponse(BaseModel):
    quizId: UUID
    topic: str
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


class HistoryItem(BaseModel):
    quizId: UUID
    topic: str
    dateTaken: str
    score: int


class QuizRecord(BaseModel):
    quizId: UUID
    topic: str
    difficulty: str
    requestedQuestions: int
    status: str  # processing | completed | failed
    questions: List[QuizQuestion] = []
    answerKey: Dict[int, str] = {}
    createdAt: str


