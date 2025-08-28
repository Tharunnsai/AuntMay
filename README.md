# Quiz Generation Microservice

A FastAPI-based microservice for generating and evaluating quizzes using AI (Groq LLM).

## Features

- **Quiz Generation**: Generate multiple-choice quizzes on any topic with configurable difficulty
- **Quiz Evaluation**: Submit answers and get detailed results with explanations
- **No Authentication**: Simple, stateless microservice design
- **AI-Powered**: Uses Groq's Llama3-8b model for intelligent quiz generation

## API Endpoints

### Generate Quiz
```http
POST /api/quiz/generate
```

**Request Body:**
```json
{
  "topic": "Ancient Rome",
  "difficulty": "medium",
  "num_questions": 5
}
```

**Response:**
```json
{
  "message": "Quiz generated successfully",
  "quizId": "uuid-here"
}
```

### Get Quiz
```http
GET /api/quiz/{quiz_id}
```

**Response:**
```json
{
  "quizId": "uuid-here",
  "topic": "Ancient Rome",
  "difficulty": "medium",
  "status": "completed",
  "questions": [
    {
      "questionId": 1,
      "questionText": "Who was the first Roman emperor?",
      "options": {
        "A": "Julius Caesar",
        "B": "Augustus",
        "C": "Nero",
        "D": "Marcus Aurelius"
      },
      "correct_answer": {"B": "Augustus"},
      "explanation": "Augustus was the first Roman emperor, ruling from 27 BC to 14 AD."
    }
  ]
}
```

### Submit Quiz
```http
POST /api/quiz/{quiz_id}/submit
```

**Request Body:**
```json
{
  "answers": [
    {
      "questionId": 1,
      "selectedOption": "B"
    }
  ]
}
```

**Response:**
```json
{
  "quizId": "uuid-here",
  "score": 100,
  "correctAnswers": 1,
  "totalQuestions": 1,
  "results": [
    {
      "questionId": 1,
      "yourAnswer": "B",
      "correctAnswer": "B",
      "isCorrect": true,
      "explanation": "Augustus was the first Roman emperor, ruling from 27 BC to 14 AD."
    }
  ]
}
```

### Delete Quiz
```http
DELETE /api/quiz/{quiz_id}
```

## Setup

1. Install dependencies:
```bash
pip install fastapi uvicorn langchain-groq langchain-core pydantic
```

2. Set environment variable for Groq API key:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

3. Run the service:
```bash
uvicorn main:app --reload
```

## Configuration

- **Model**: Uses Groq's `llama3-8b-8192` model
- **Temperature**: 0 (for consistent output)
- **Max Questions**: 50 per quiz
- **Storage**: In-memory (quizzes are lost on restart)

## Usage Examples

### Generate a History Quiz
```bash
curl -X POST "http://localhost:8000/api/quiz/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "World War II",
    "difficulty": "hard",
    "num_questions": 10
  }'
```

### Get Quiz Details
```bash
curl "http://localhost:8000/api/quiz/{quiz-id}"
```

### Submit Answers
```bash
curl -X POST "http://localhost:8000/api/quiz/{quiz-id}/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {"questionId": 1, "selectedOption": "A"},
      {"questionId": 2, "selectedOption": "C"}
    ]
  }'
```

## Architecture

- **FastAPI**: Web framework for API endpoints
- **LangChain**: LLM orchestration and prompt management
- **Groq**: High-performance LLM inference
- **Pydantic**: Data validation and serialization
- **In-memory Storage**: Simple dictionary-based storage for quiz data

This microservice is designed to be lightweight, stateless, and easily integrable into larger applications that need quiz generation capabilities.
