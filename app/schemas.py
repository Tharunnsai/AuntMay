from pydantic import BaseModel, Field
from typing import List, Dict, Optional
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


# Schema for LLM output (used with PydanticOutputParser)
class QuizBundleLLM(BaseModel):
    topic: str
    difficulty: str
    questions: List[QuizQuestion]


# Schema for backend (with metadata, for API responses)
class QuizBundle(QuizBundleLLM):
    quizId: UUID
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
    correctOption: str
    isCorrect: bool
    explanation: str


class SubmitQuizResponse(BaseModel):
    quizId: UUID
    score: int
    correctAnswers: int
    totalQuestions: int
    results: List[QuestionResult]


# New schemas for agentic quiz generation
class ResearchInfo(BaseModel):
    source: str
    content: str
    relevance_score: float


class TopicResearch(BaseModel):
    topic: str
    research_summary: str
    key_concepts: List[str]
    difficulty_appropriate_facts: List[str]
    sources: List[ResearchInfo]


class AgenticQuizRequest(BaseModel):
    topic: str
    difficulty: str = Field(default="medium", description="Quiz difficulty level")
    num_questions: int = Field(gt=0, le=50, description="Number of questions to generate")
    research_depth: str = Field(default="comprehensive", description="Research depth: basic, comprehensive, or expert")


class AgenticQuizResponse(BaseModel):
    quizId: UUID
    topic: str
    difficulty: str
    status: str
    questions: List[QuizQuestion]
    research_summary: str
    key_concepts: List[str]
    sources: List[ResearchInfo]


