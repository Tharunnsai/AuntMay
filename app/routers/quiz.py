from uuid import UUID, uuid4
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from datetime import datetime
from dotenv import load_dotenv
import asyncio
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import re
import logging

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
    AgenticQuizRequest,
    AgenticQuizResponse,
    TopicResearch,
    ResearchInfo,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

# ---- LLM Setup ----
parser = PydanticOutputParser(pydantic_object=QuizBundleLLM)

# Research prompt for gathering information
research_prompt = PromptTemplate(
    template=(
        "You are a research assistant. Analyze the following information about '{topic}' "
        "and provide a comprehensive summary.\n\n"
        "Research Information:\n{research_data}\n\n"
        "Please provide:\n"
        "1. A concise summary of the topic\n"
        "2. Key concepts and facts\n"
        "3. Difficulty-appropriate facts for {difficulty} level\n"
        "4. Important details that would make good quiz questions\n\n"
        "Focus on accuracy and relevance. Format your response as a structured summary."
    ),
    input_variables=["topic", "difficulty", "research_data"],
)

# Quiz generation prompt that uses research
quiz_generation_prompt = PromptTemplate(
    template=(
        "Based on the following research about '{topic}', generate exactly {num_questions} "
        "multiple-choice quiz questions with {difficulty} difficulty level.\n\n"
        "Research Summary:\n{research_summary}\n\n"
        "Key Concepts:\n{key_concepts}\n\n"
        "Difficulty-Appropriate Facts:\n{difficulty_facts}\n\n"
        "Requirements:\n"
        "- Each question must have options with keys A, B, C, D\n"
        "- correct_answer must be a single-key object like {{\"B\": \"Augustus\"}}\n"
        "- explanation must be 1–2 sentences explaining why the answer is correct\n"
        "- For {difficulty} difficulty: adjust question complexity accordingly\n"
        "- Questions should test understanding, not just memorization\n"
        "- All questions must be factually accurate based on the research\n\n"
        "Return JSON that matches this schema:\n{format_instructions}"
    ),
    input_variables=["topic", "num_questions", "difficulty", "research_summary", "key_concepts", "difficulty_facts"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Fallback prompt for when research fails
fallback_quiz_prompt = PromptTemplate(
    template=(
        "Generate exactly {num_questions} multiple-choice quiz questions about '{topic}' "
        "with {difficulty} difficulty level.\n\n"
        "Requirements:\n"
        "- Each question must have options with keys A, B, C, D\n"
        "- correct_answer must be a single-key object like {{\"B\": \"Augustus\"}}\n"
        "- explanation must be 1–2 sentences explaining why the answer is correct\n"
        "- For {difficulty} difficulty: adjust question complexity accordingly\n"
        "- Questions should test understanding, not just memorization\n\n"
        "Return JSON that matches this schema:\n{format_instructions}"
    ),
    input_variables=["topic", "num_questions", "difficulty"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

llm = ChatGroq(model="deepseek-r1-distill-llama-70b", temperature=0)
structured_llm = llm.with_structured_output(QuizBundleLLM)

# ---- In-memory store ----
QUIZ_DB: Dict[UUID, QuizBundle] = {}
RESEARCH_DB: Dict[UUID, TopicResearch] = {}

# ---- Web Research Functions ----
async def search_web(topic: str, max_results: int = 5) -> List[ResearchInfo]:
    """Search the web for information about a topic using DuckDuckGo."""
    try:
        # Run the blocking DDGS operation in a thread pool
        loop = asyncio.get_event_loop()
        search_results = await loop.run_in_executor(
            None, 
            lambda: list(DDGS().text(topic, max_results=max_results))
        )
        
        research_info = []
        
        # Process results concurrently
        tasks = []
        for result in search_results:
            task = extract_webpage_content(result.get('href', result.get('link', '')))
            tasks.append((result, task))
        
        # Wait for all content extraction tasks
        for result, task in tasks:
            try:
                content = await task
                if content:
                    # Calculate relevance score based on title match
                    title = result.get('title', '')
                    title_relevance = calculate_relevance(title, topic)
                    research_info.append(ResearchInfo(
                        source=result.get('href', result.get('link', '')),
                        content=content[:1500],  # Increased content length
                        relevance_score=title_relevance
                    ))
            except Exception as e:
                logger.warning(f"Error processing result {result.get('link', 'unknown')}: {e}")
                continue
        
        # Sort by relevance and return top results
        research_info.sort(key=lambda x: x.relevance_score, reverse=True)
        return research_info[:max_results]
        
    except Exception as e:
        logger.error(f"Error in web search: {e}")
        return []

async def extract_webpage_content(url: str) -> str:
    """Extract text content from a webpage."""
    if not url:
        return ""
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Run the blocking request in a thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.get(url, headers=headers, timeout=10)
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Focus on main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main'))
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove extra whitespace and limit length
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:2000]  # Reasonable content limit
        
    except Exception as e:
        logger.warning(f"Error extracting content from {url}: {e}")
        return ""

def calculate_relevance(title: str, topic: str) -> float:
    """Calculate relevance score between title and topic."""
    if not title or not topic:
        return 0.0
        
    title_lower = title.lower()
    topic_lower = topic.lower()
    
    # Simple relevance calculation
    topic_words = set(re.findall(r'\w+', topic_lower))
    title_words = set(re.findall(r'\w+', title_lower))
    
    if not topic_words:
        return 0.0
    
    intersection = len(topic_words.intersection(title_words))
    union = len(topic_words.union(title_words))
    
    # Jaccard similarity
    return intersection / union if union > 0 else 0.0

async def research_topic(topic: str, difficulty: str) -> TopicResearch:
    """Research a topic using web search and LLM analysis."""
    try:
        # Search the web
        research_data = await search_web(topic, max_results=5)
        
        if not research_data:
            logger.warning(f"No research data found for topic: {topic}")
            # Return minimal research data
            return TopicResearch(
                topic=topic,
                research_summary=f"Limited information available for {topic}",
                key_concepts=[topic],
                difficulty_appropriate_facts=[f"Basic facts about {topic}"],
                sources=[]
            )
        
        # Combine research data
        combined_content = "\n\n".join([
            f"Source: {r.source}\nContent: {r.content}" 
            for r in research_data if r.content
        ])
        
        if not combined_content:
            raise ValueError("No valid content extracted from research")
        
        # Use LLM to analyze and structure the research
        research_chain = research_prompt | llm
        research_response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: research_chain.invoke({
                "topic": topic,
                "difficulty": difficulty,
                "research_data": combined_content
            })
        )
        
        # Parse the LLM response to extract structured information
        content = research_response.content
        
        # Extract key information with better error handling
        research_summary = extract_section(content, "summary", "Summary") or f"Research summary for {topic}"
        key_concepts = extract_list_section(content, "concepts", "Key Concepts") or [topic]
        difficulty_facts = extract_list_section(content, "facts", "Difficulty-Appropriate Facts") or [f"Facts about {topic}"]
        
        return TopicResearch(
            topic=topic,
            research_summary=research_summary,
            key_concepts=key_concepts,
            difficulty_appropriate_facts=difficulty_facts,
            sources=research_data
        )
        
    except Exception as e:
        logger.error(f"Error in research_topic: {e}")
        # Return fallback research
        return TopicResearch(
            topic=topic,
            research_summary=f"General information about {topic}",
            key_concepts=[topic],
            difficulty_appropriate_facts=[f"Basic concepts related to {topic}"],
            sources=[]
        )

def extract_section(content: str, section_name: str, section_header: str) -> Optional[str]:
    """Extract a section from LLM response content."""
    if not content:
        return None
        
    lines = content.split('\n')
    start_idx = -1
    end_idx = len(lines)
    
    # Look for section headers (case insensitive)
    for i, line in enumerate(lines):
        if section_header.lower() in line.lower() and ('summary' in section_header.lower() or ':' in line):
            start_idx = i + 1
        elif start_idx != -1 and (line.strip().startswith('#') or 
                                 any(header in line.lower() for header in ['key concepts', 'difficulty', 'important'])):
            end_idx = i
            break
    
    if start_idx != -1 and start_idx < len(lines):
        extracted = '\n'.join(lines[start_idx:end_idx]).strip()
        return extracted if extracted else None
    return None

def extract_list_section(content: str, section_name: str, section_header: str) -> List[str]:
    """Extract a list section from LLM response content."""
    section_text = extract_section(content, section_name, section_header)
    if not section_text:
        return []
    
    # Split by common list indicators
    lines = [line.strip() for line in section_text.split('\n') if line.strip()]
    items = []
    
    for line in lines:
        # Remove common list markers
        cleaned = re.sub(r'^[-*•\d]+\.?\s*', '', line).strip()
        if cleaned and len(cleaned) > 3:  # Filter out very short items
            items.append(cleaned)
    
    return items[:10]  # Limit to reasonable number of items

# ---- Endpoints ----

@router.post("/generate-agentic", response_model=AgenticQuizResponse, status_code=201)
async def generate_agentic_quiz(payload: AgenticQuizRequest):
    """
    Generate a quiz using agentic approach: research the topic first, then create questions.
    """
    quiz_id = uuid4()
    
    try:
        # Step 1: Research the topic
        research = await research_topic(payload.topic, payload.difficulty)
        RESEARCH_DB[quiz_id] = research
        
        # Step 2: Generate quiz questions based on research
        quiz_chain = quiz_generation_prompt | structured_llm
        
        # Prepare research data for the prompt
        research_summary = research.research_summary or f"Information about {payload.topic}"
        key_concepts = "\n".join(research.key_concepts) if research.key_concepts else payload.topic
        difficulty_facts = "\n".join(research.difficulty_appropriate_facts) if research.difficulty_appropriate_facts else f"Facts about {payload.topic}"
        
        raw_bundle: QuizBundleLLM = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: quiz_chain.invoke({
                "topic": payload.topic,
                "num_questions": payload.num_questions,
                "difficulty": payload.difficulty,
                "research_summary": research_summary,
                "key_concepts": key_concepts,
                "difficulty_facts": difficulty_facts
            })
        )
        
        # Step 3: Create quiz bundle with validation
        if not raw_bundle.questions:
            raise ValueError("No questions generated by LLM")
            
        bundle = QuizBundle(
            quizId=quiz_id,
            topic=raw_bundle.topic,
            difficulty=raw_bundle.difficulty,
            createdAt=datetime.utcnow().isoformat(),
            questions=raw_bundle.questions
        )
        
        QUIZ_DB[quiz_id] = bundle
        
        return AgenticQuizResponse(
            quizId=bundle.quizId,
            topic=bundle.topic,
            difficulty=bundle.difficulty,
            status="completed",
            questions=bundle.questions,
            research_summary=research.research_summary,
            key_concepts=research.key_concepts,
            sources=research.sources
        )
        
    except Exception as e:
        logger.error(f"Failed to generate agentic quiz: {e}")
        
        # Fallback: Generate quiz without research
        try:
            fallback_chain = fallback_quiz_prompt | structured_llm
            raw_bundle: QuizBundleLLM = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: fallback_chain.invoke({
                    "topic": payload.topic,
                    "num_questions": payload.num_questions,
                    "difficulty": payload.difficulty
                })
            )
            
            bundle = QuizBundle(
                quizId=quiz_id,
                topic=raw_bundle.topic,
                difficulty=raw_bundle.difficulty,
                createdAt=datetime.utcnow().isoformat(),
                questions=raw_bundle.questions
            )
            
            QUIZ_DB[quiz_id] = bundle
            
            # Create minimal research data for fallback
            fallback_research = TopicResearch(
                topic=payload.topic,
                research_summary=f"Quiz generated for {payload.topic}",
                key_concepts=[payload.topic],
                difficulty_appropriate_facts=[],
                sources=[]
            )
            RESEARCH_DB[quiz_id] = fallback_research
            
            return AgenticQuizResponse(
                quizId=bundle.quizId,
                topic=bundle.topic,
                difficulty=bundle.difficulty,
                status="completed",
                questions=bundle.questions,
                research_summary=fallback_research.research_summary,
                key_concepts=fallback_research.key_concepts,
                sources=fallback_research.sources
            )
            
        except Exception as fallback_error:
            logger.error(f"Fallback quiz generation also failed: {fallback_error}")
            raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@router.post("/generate", response_model=GenerateQuizResponse, status_code=202)
async def generate_quiz(payload: GenerateQuizRequest):
    """
    Generate a new quiz with the specified topic, difficulty, and number of questions.
    """
    quiz_id = uuid4()

    try:
        # Generate quiz with LLM using fallback prompt
        raw_bundle: QuizBundleLLM = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: structured_llm.invoke({
                "topic": payload.topic,
                "num_questions": payload.num_questions,
                "difficulty": payload.difficulty
            })
        )

        # Validate that questions were generated
        if not raw_bundle.questions:
            raise ValueError("No questions generated by LLM")

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
        
    except Exception as e:
        logger.error(f"Failed to generate quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@router.post("/generate-and-return", response_model=QuizDetailResponse, status_code=201)
async def generate_quiz_and_return(payload: GenerateQuizRequest):
    """
    Generate a new quiz and return the full quiz payload instead of just the ID.
    This endpoint combines generate + get_quiz to reduce redundancy.
    """
    try:
        # Step 1: Generate the quiz (reuse existing logic)
        generate_response = await generate_quiz(payload)
        quiz_id = generate_response.quizId
        
        # Step 2: Get the full quiz details (reuse existing logic)
        quiz_details = await get_quiz(quiz_id)
        
        return quiz_details
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Failed to generate and return quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

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

@router.get("/{quiz_id}/research", response_model=TopicResearch)
async def get_quiz_research(quiz_id: UUID):
    """
    Retrieve the research data used to generate a quiz.
    """
    research = RESEARCH_DB.get(quiz_id)
    if not research:
        raise HTTPException(status_code=404, detail="Research data not found")
    
    return research

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
            logger.warning(f"Question not found: {ans.questionId}")
            continue

        # Extract correct answer key/value with better error handling
        try:
            if not q.correct_answer:
                logger.warning(f"No correct answer for question: {q.questionId}")
                continue
                
            correct_key, correct_value = list(q.correct_answer.items())[0]
            is_correct = ans.selectedOption == correct_key

            if is_correct:
                correct_count += 1

            results.append(
                QuestionResult(
                    questionId=q.questionId,
                    yourAnswer=ans.selectedOption,
                    correctOption=correct_key,
                    isCorrect=is_correct,
                    explanation=q.explanation or "No explanation available"
                )
            )
        except (IndexError, AttributeError) as e:
            logger.error(f"Error processing question {q.questionId}: {e}")
            continue

    total_questions = len(results)  # Use actual processed questions
    if total_questions == 0:
        raise HTTPException(status_code=400, detail="No valid questions found to evaluate")
        
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
    
    # Also delete research data if it exists
    if quiz_id in RESEARCH_DB:
        del RESEARCH_DB[quiz_id]
    
    return {"message": "Quiz deleted successfully"}