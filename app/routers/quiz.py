from uuid import UUID, uuid4
from typing import List, Dict
from fastapi import APIRouter, HTTPException
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from ..schemas import (
    GenerateQuizRequest,
    GenerateQuizResponse,
    QuizDetailResponse,
    SubmitQuizRequest,
    SubmitQuizResponse,
    QuestionResult,
    QuizQuestion,
    QuizBundle,
    QuizBundleLLM,
)

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

# ---- LLM Setup ----
parser = PydanticOutputParser(pydantic_object=QuizBundleLLM)

prompt = PromptTemplate(
    template=(
        "Generate exactly {num_questions} multiple-choice quiz questions "
        "about the topic: {topic} with {difficulty} difficulty level.\n"
        "Each question must have options with keys A, B, C, D.\n"
        "Return JSON that matches this schema:\n{format_instructions}\n"
        "Rules:\n"
        "- correct_answer must be a single-key object like {{\"B\": \"Augustus\"}}\n"
        "- explanation must be 1–2 sentences.\n"
        "- For {difficulty} difficulty: adjust question complexity accordingly.\n"
    ),
    input_variables=["topic", "num_questions", "difficulty"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

llm = ChatGroq(model="llama3-8b-8192", temperature=0)
# Use structured outputs to reduce JSON parsing errors from the LLM
structured_llm = llm.with_structured_output(QuizBundleLLM)
chain = prompt | structured_llm

# ---- In-memory store ----
QUIZ_DB: Dict[UUID, QuizBundle] = {}

# ---- Endpoints ----

@router.post("/generate", response_model=GenerateQuizResponse, status_code=202)
async def generate_quiz(payload: GenerateQuizRequest):
    """
    Generate a new quiz with the specified topic, difficulty, and number of questions.
    """
    quiz_id = uuid4()

    # Generate quiz with LLM
    raw_bundle: QuizBundleLLM = chain.invoke({
        "topic": payload.topic,
        "num_questions": payload.num_questions,
        "difficulty": payload.difficulty
    })

    # Attach metadata (convert to full QuizBundle)
    bundle = QuizBundle(
        quizId=quiz_id,
        topic=raw_bundle.topic,
        difficulty=raw_bundle.difficulty,
        createdAt=datetime.utcnow().isoformat(),
        questions=raw_bundle.questions
    )

    QUIZ_DB[quiz_id] = bundle

    return GenerateQuizResponse(
        message="Quiz generated successfully",
        quizId=quiz_id
    )


@router.post("/generate-and-return", response_model=QuizDetailResponse, status_code=201)
async def generate_quiz_and_return(payload: GenerateQuizRequest):
    """
    Generate a new quiz and return the full quiz payload instead of just the ID.
    """
    quiz_id = uuid4()

    # Generate quiz with LLM
    raw_bundle: QuizBundleLLM = chain.invoke({
        "topic": payload.topic,
        "num_questions": payload.num_questions,
        "difficulty": payload.difficulty
    })

    # Attach metadata (convert to full QuizBundle)
    bundle = QuizBundle(
        quizId=quiz_id,
        topic=raw_bundle.topic,
        difficulty=raw_bundle.difficulty,
        createdAt=datetime.utcnow().isoformat(),
        questions=raw_bundle.questions
    )

    QUIZ_DB[quiz_id] = bundle

    return QuizDetailResponse(
        quizId=bundle.quizId,
        topic=bundle.topic,
        difficulty=bundle.difficulty,
        status="completed",
        questions=bundle.questions
    )


@router.get("/{quiz_id}", response_model=QuizDetailResponse)
async def get_quiz(quiz_id: UUID):
    """
    Retrieve a generated quiz by its ID.
    """
    quiz = QUIZ_DB.get(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return QuizDetailResponse(
        quizId=quiz.quizId,
        topic=quiz.topic,
        difficulty=quiz.difficulty,
        status="completed",
        questions=quiz.questions
    )


@router.post("/{quiz_id}/submit", response_model=SubmitQuizResponse)
async def submit_quiz(quiz_id: UUID, payload: SubmitQuizRequest):
    """
    Submit answers for a quiz and get evaluation results.
    """
    quiz = QUIZ_DB.get(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    results: List[QuestionResult] = []
    correct_count = 0

    # Evaluate each answer
    for ans in payload.answers:
        q = next((q for q in quiz.questions if q.questionId == ans.questionId), None)
        if not q:
            continue

        # Extract correct answer key/value
        correct_key, correct_value = list(q.correct_answer.items())[0]
        is_correct = ans.selectedOption == correct_key

        if is_correct:
            correct_count += 1

        results.append(
            QuestionResult(
                questionId=q.questionId,
                yourAnswer=ans.selectedOption,
                correctAnswer=correct_key,
                isCorrect=is_correct,
                explanation=q.explanation
            )
        )

    total_questions = len(quiz.questions)
    score = int((correct_count / total_questions) * 100)

    return SubmitQuizResponse(
        quizId=quiz.quizId,
        score=score,
        correctAnswers=correct_count,
        totalQuestions=total_questions,
        results=results
    )


@router.delete("/{quiz_id}")
async def delete_quiz(quiz_id: UUID):
    """
    Delete a quiz from the in-memory store.
    """
    if quiz_id not in QUIZ_DB:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    del QUIZ_DB[quiz_id]
    return {"message": "Quiz deleted successfully"}
