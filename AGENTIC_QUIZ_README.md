# Agentic Quiz Generation System

## Overview

The quiz generation system has been transformed from a simple LLM API call to an **agentic system** that:

1. **Researches topics** by gathering accurate information from the internet
2. **Analyzes and structures** the research data using LLM intelligence
3. **Formulates questions** based on difficulty levels and research findings
4. **Returns comprehensive quiz responses** with explanations and source attribution

## Key Features

### 🔍 Web Research
- **DuckDuckGo Integration**: Searches the web for current, accurate information
- **Content Extraction**: Automatically extracts and cleans webpage content
- **Relevance Scoring**: Ranks sources by relevance to the topic
- **Source Attribution**: Tracks all research sources used

### 🧠 Intelligent Analysis
- **LLM-Powered Research**: Uses Groq LLM to analyze and structure research data
- **Difficulty Adaptation**: Adjusts content complexity based on quiz difficulty level
- **Concept Extraction**: Identifies key concepts and facts for question generation
- **Fact Verification**: Ensures questions are based on verified research

### 📝 Smart Question Generation
- **Research-Based Questions**: Questions are formulated from actual research, not generic knowledge
- **Difficulty-Appropriate**: Questions match the specified difficulty level
- **Comprehensive Explanations**: Each answer includes detailed explanations
- **Multiple Choice Format**: Standardized A, B, C, D option structure

## API Endpoints

### 1. Generate Agentic Quiz
```http
POST /api/quiz/generate-agentic
```

**Request Body:**
```json
{
  "topic": "Ancient Roman Empire",
  "difficulty": "medium",
  "num_questions": 5,
  "research_depth": "comprehensive"
}
```

**Response:**
```json
{
  "quizId": "uuid",
  "topic": "Ancient Roman Empire",
  "difficulty": "medium",
  "status": "completed",
  "questions": [...],
  "research_summary": "Comprehensive summary of research findings...",
  "key_concepts": ["Concept 1", "Concept 2", ...],
  "sources": [
    {
      "source": "https://example.com",
      "content": "Extracted content...",
      "relevance_score": 0.85
    }
  ]
}
```

### 2. Get Quiz Research Data
```http
GET /api/quiz/{quiz_id}/research
```

Returns the research data used to generate a specific quiz.

### 3. Traditional Quiz Generation (Still Available)
```http
POST /api/quiz/generate
POST /api/quiz/generate-and-return
```

## How It Works

### Step 1: Web Research
1. **Search Query**: System searches DuckDuckGo for the topic
2. **Content Extraction**: Visits top results and extracts text content
3. **Relevance Scoring**: Calculates relevance scores for each source
4. **Data Aggregation**: Combines content from multiple sources

### Step 2: Research Analysis
1. **LLM Processing**: Sends research data to Groq LLM for analysis
2. **Structured Output**: LLM provides:
   - Research summary
   - Key concepts
   - Difficulty-appropriate facts
   - Important details for questions

### Step 3: Question Generation
1. **Research-Based Prompt**: LLM generates questions using research data
2. **Difficulty Adaptation**: Questions match specified difficulty level
3. **Fact Verification**: All questions are based on verified research
4. **Explanation Generation**: Detailed explanations for each answer

### Step 4: Response Assembly
1. **Quiz Bundle**: Combines questions with metadata
2. **Research Attribution**: Includes research summary and sources
3. **Complete Response**: Returns full quiz with research context

## Difficulty Levels

### Easy
- Basic facts and definitions
- Simple recall questions
- Clear, straightforward options

### Medium
- Application of concepts
- Analysis and comparison
- Moderate complexity

### Hard
- Advanced concepts
- Critical thinking required
- Complex scenarios and analysis

## Research Depth Options

### Basic
- Fewer sources (2-3)
- Shorter content extraction
- Quick generation

### Comprehensive (Default)
- Multiple sources (5)
- Full content extraction
- Balanced speed/quality

### Expert
- Maximum sources (8-10)
- Deep content analysis
- Highest quality questions

## Error Handling

The system includes robust error handling for:
- **Web search failures**: Falls back to available sources
- **Content extraction errors**: Skips problematic URLs
- **LLM failures**: Returns appropriate error messages
- **Network timeouts**: Configurable timeout settings

## Performance Considerations

- **Async Processing**: Web requests are handled asynchronously
- **Content Limits**: Webpage content is limited to prevent memory issues
- **Caching**: Research data is stored for potential reuse
- **Timeout Management**: Configurable timeouts for web requests

## Security Features

- **User-Agent Headers**: Proper identification for web requests
- **Content Sanitization**: HTML content is cleaned and sanitized
- **Source Validation**: Only trusted sources are processed
- **Rate Limiting**: Built-in protection against abuse

## Testing

Use the provided test script to verify functionality:

```bash
python test_agentic_quiz.py
```

## Dependencies

```txt
fastapi
uvicorn[standard]
langchain-groq
langchain-core
pydantic
python-dotenv
duckduckgo-search
requests
beautifulsoup4
```

## Configuration

Set environment variables:
```bash
GROQ_API_KEY=your_groq_api_key
```

## Future Enhancements

- **Research Caching**: Store research results for reuse
- **Advanced Filtering**: Better source credibility assessment
- **Multi-Language Support**: Research in multiple languages
- **Image Integration**: Include relevant images in research
- **Citation Management**: Better source attribution and citation

## Troubleshooting

### Common Issues

1. **Web Search Fails**
   - Check internet connectivity
   - Verify DuckDuckGo accessibility
   - Check rate limiting

2. **Content Extraction Issues**
   - Some websites block scraping
   - JavaScript-heavy sites may not work
   - Check timeout settings

3. **LLM Generation Errors**
   - Verify Groq API key
   - Check API rate limits
   - Review prompt formatting

### Debug Mode

Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When contributing to the agentic quiz system:

1. **Maintain Research Quality**: Ensure web research remains accurate
2. **Improve Error Handling**: Add robust error handling for edge cases
3. **Optimize Performance**: Look for ways to improve speed and efficiency
4. **Enhance Security**: Maintain security best practices
5. **Update Documentation**: Keep this README current with changes
