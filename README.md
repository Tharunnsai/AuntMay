# Quiz Generation Microservice

A focused microservice for generating and evaluating quizzes using AI (Groq LLM).

## Features

- **Quiz Generation**: Generate multiple-choice quizzes on any topic using AI
- **Quiz Evaluation**: Submit answers and get detailed results with explanations
- **Difficulty Levels**: Support for different difficulty levels (easy, medium, hard)
- **Health Check**: Built-in health monitoring endpoint

## API Endpoints

### Generate Quiz
```
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

### Get Quiz
```
GET /api/quiz/{quiz_id}
```

### Submit Quiz Answers
```
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

### Health Check
```
GET /api/quiz/health
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

3. Run the service:
```bash
uvicorn app.main:app --reload
```

## Usage Example

```python
import requests

# Generate a quiz
response = requests.post("http://localhost:8000/api/quiz/generate", json={
    "topic": "Python Programming",
    "difficulty": "medium",
    "num_questions": 3
})
quiz_id = response.json()["quizId"]

# Get the quiz
quiz = requests.get(f"http://localhost:8000/api/quiz/{quiz_id}")

# Submit answers
results = requests.post(f"http://localhost:8000/api/quiz/{quiz_id}/submit", json={
    "answers": [
        {"questionId": 1, "selectedOption": "A"},
        {"questionId": 2, "selectedOption": "B"},
        {"questionId": 3, "selectedOption": "C"}
    ]
})
```

## Architecture

- **Framework**: FastAPI
- **AI Provider**: Groq (llama3-8b-8192 model)
- **Storage**: In-memory (for microservice simplicity)
- **Language**: Python 3.8+

## Notes

- This is a stateless microservice designed for integration with larger systems
- Quiz data is stored in-memory and will be lost on service restart
- For production use, consider adding persistent storage and rate limiting
