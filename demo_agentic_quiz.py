#!/usr/bin/env python3
"""
Demo script for the Agentic Quiz Generation System.
This script demonstrates the key features of the new system.
"""

import json
from app.schemas import AgenticQuizRequest, ResearchInfo, TopicResearch

def demo_schemas():
    """Demonstrate the new schemas."""
    print("📋 Demo: New Schemas")
    print("=" * 40)
    
    # Create a sample agentic quiz request
    request = AgenticQuizRequest(
        topic="Machine Learning Fundamentals",
        difficulty="medium",
        num_questions=5,
        research_depth="comprehensive"
    )
    
    print("Sample Agentic Quiz Request:")
    print(json.dumps(request.model_dump(), indent=2))
    
    # Create a sample research info
    sample_source = ResearchInfo(
        source="https://example.com/ml-basics",
        content="Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.",
        relevance_score=0.92
    )
    
    print("\nSample Research Source:")
    print(json.dumps(sample_source.model_dump(), indent=2))
    
    # Create a sample topic research
    sample_research = TopicResearch(
        topic="Machine Learning Fundamentals",
        research_summary="Machine learning is a core technology driving modern AI applications, from recommendation systems to autonomous vehicles.",
        key_concepts=[
            "Supervised Learning",
            "Unsupervised Learning", 
            "Neural Networks",
            "Feature Engineering",
            "Model Evaluation"
        ],
        difficulty_appropriate_facts=[
            "Machine learning models learn patterns from data rather than following explicit rules",
            "Supervised learning uses labeled training data to make predictions",
            "Unsupervised learning finds hidden patterns in unlabeled data",
            "Neural networks are inspired by biological brain structures",
            "Feature engineering is crucial for model performance"
        ],
        sources=[sample_source]
    )
    
    print("\nSample Topic Research:")
    print(json.dumps(sample_research.model_dump(), indent=2))

def demo_api_structure():
    """Demonstrate the API structure."""
    print("\n\n🌐 Demo: API Structure")
    print("=" * 40)
    
    print("New Endpoint: POST /api/quiz/generate-agentic")
    print()
    print("Request Body Structure:")
    print("- topic: string (required)")
    print("- difficulty: string (easy/medium/hard, default: medium)")
    print("- num_questions: integer (1-50, required)")
    print("- research_depth: string (basic/comprehensive/expert, default: comprehensive)")
    print()
    
    print("Response Structure:")
    print("- quizId: UUID")
    print("- topic: string")
    print("- difficulty: string")
    print("- status: string")
    print("- questions: array of quiz questions")
    print("- research_summary: string")
    print("- key_concepts: array of strings")
    print("- sources: array of research sources")
    print()
    
    print("Additional Endpoints:")
    print("- GET /api/quiz/{quiz_id}/research - Get research data for a quiz")
    print("- All existing endpoints remain available")

def demo_workflow():
    """Demonstrate the agentic workflow."""
    print("\n\n🔄 Demo: Agentic Workflow")
    print("=" * 40)
    
    print("Step 1: Web Research")
    print("  - Search DuckDuckGo for topic information")
    print("  - Extract content from top search results")
    print("  - Calculate relevance scores for sources")
    print("  - Aggregate research data")
    print()
    
    print("Step 2: Research Analysis")
    print("  - Send research data to Groq LLM")
    print("  - Generate structured research summary")
    print("  - Extract key concepts and facts")
    print("  - Identify difficulty-appropriate content")
    print()
    
    print("Step 3: Question Generation")
    print("  - Use research data to formulate questions")
    print("  - Ensure questions match difficulty level")
    print("  - Generate accurate explanations")
    print("  - Verify factual accuracy from sources")
    print()
    
    print("Step 4: Response Assembly")
    print("  - Combine questions with research context")
    print("  - Include source attribution")
    print("  - Provide comprehensive quiz package")
    print("  - Store for future reference")

def main():
    """Run all demos."""
    print("🚀 Agentic Quiz Generation System Demo")
    print("=" * 50)
    print()
    
    # Demo 1: Schemas
    demo_schemas()
    
    # Demo 2: API Structure
    demo_api_structure()
    
    # Demo 3: Workflow
    demo_workflow()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    print("\nTo test the full system:")
    print("1. Set your GROQ_API_KEY environment variable")
    print("2. Start the FastAPI server: uvicorn app.main:app --reload")
    print("3. Run: python test_agentic_quiz.py")
    print("4. Or use the API directly: POST /api/quiz/generate-agentic")
    print()
    print("Key Benefits of the New System:")
    print("✅ Factual accuracy through web research")
    print("✅ Difficulty-appropriate question generation")
    print("✅ Source attribution and transparency")
    print("✅ Comprehensive explanations")
    print("✅ Research-based learning content")

if __name__ == "__main__":
    main()
