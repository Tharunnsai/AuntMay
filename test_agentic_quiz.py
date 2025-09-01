#!/usr/bin/env python3
"""
Test script for the agentic quiz generation system.
This script demonstrates how to use the new agentic quiz generation endpoint.
"""

import asyncio
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
AGENTIC_ENDPOINT = f"{BASE_URL}/api/quiz/generate-agentic"

def test_agentic_quiz_generation():
    """Test the agentic quiz generation endpoint."""
    
    # Test payload
    payload = {
        "topic": "Ancient Roman Empire",
        "difficulty": "medium",
        "num_questions": 5,
        "research_depth": "comprehensive"
    }
    
    print("🚀 Testing Agentic Quiz Generation")
    print("=" * 50)
    print(f"Topic: {payload['topic']}")
    print(f"Difficulty: {payload['difficulty']}")
    print(f"Questions: {payload['num_questions']}")
    print(f"Research Depth: {payload['research_depth']}")
    print()
    
    try:
        print("📚 Researching topic and generating quiz...")
        print("(This may take a few moments as it researches the web)")
        print()
        
        # Make the request
        response = requests.post(AGENTIC_ENDPOINT, json=payload)
        
        if response.status_code == 201:
            quiz_data = response.json()
            
            print("✅ Quiz generated successfully!")
            print(f"Quiz ID: {quiz_data['quizId']}")
            print(f"Status: {quiz_data['status']}")
            print()
            
            # Display research summary
            print("🔍 Research Summary:")
            print("-" * 30)
            print(quiz_data['research_summary'])
            print()
            
            # Display key concepts
            print("🎯 Key Concepts:")
            print("-" * 30)
            for i, concept in enumerate(quiz_data['key_concepts'], 1):
                print(f"{i}. {concept}")
            print()
            
            # Display questions
            print("❓ Quiz Questions:")
            print("-" * 30)
            for i, question in enumerate(quiz_data['questions'], 1):
                print(f"Question {i}: {question['questionText']}")
                print("Options:")
                for key, value in question['options'].items():
                    print(f"  {key}. {value}")
                
                # Get correct answer
                correct_key = list(question['correct_answer'].keys())[0]
                correct_value = question['correct_answer'][correct_key]
                print(f"Correct Answer: {correct_key}. {correct_value}")
                print(f"Explanation: {question['explanation']}")
                print()
            
            # Display sources
            print("📖 Research Sources:")
            print("-" * 30)
            for i, source in enumerate(quiz_data['sources'], 1):
                print(f"{i}. {source['source']}")
                print(f"   Relevance Score: {source['relevance_score']:.2f}")
                print()
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_research_endpoint(quiz_id: str):
    """Test retrieving research data for a specific quiz."""
    
    research_endpoint = f"{BASE_URL}/api/quiz/{quiz_id}/research"
    
    print(f"🔬 Testing Research Data Retrieval for Quiz {quiz_id}")
    print("=" * 60)
    
    try:
        response = requests.get(research_endpoint)
        
        if response.status_code == 200:
            research_data = response.json()
            
            print("✅ Research data retrieved successfully!")
            print()
            print("📚 Topic Research Details:")
            print("-" * 40)
            print(f"Topic: {research_data['topic']}")
            print()
            print("Summary:")
            print(research_data['research_summary'])
            print()
            print("Key Concepts:")
            for i, concept in enumerate(research_data['key_concepts'], 1):
                print(f"{i}. {concept}")
            print()
            print("Difficulty-Appropriate Facts:")
            for i, fact in enumerate(research_data['difficulty_appropriate_facts'], 1):
                print(f"{i}. {fact}")
            print()
            print("Sources:")
            for i, source in enumerate(research_data['sources'], 1):
                print(f"{i}. {source['source']}")
                print(f"   Relevance: {source['relevance_score']:.2f}")
                print()
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Agentic Quiz Generation Test Suite")
    print("=" * 50)
    print()
    
    # Test 1: Generate a new agentic quiz
    test_agentic_quiz_generation()
    
    print("\n" + "=" * 50)
    print("💡 To test the research endpoint, use the quiz ID from above")
    print("Example: test_research_endpoint('your-quiz-id-here')")
    print()
    
    # Uncomment and modify the line below to test research retrieval
    # test_research_endpoint("your-actual-quiz-id")
