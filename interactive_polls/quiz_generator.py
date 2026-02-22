#!/usr/bin/env python3
"""
Generate interactive quiz/poll from lecture content using AI
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
import poll_config as config

# Load environment variables from .env file
load_dotenv()

def generate_quiz_gemini(lecture_content):
    """Generate quiz using Google Gemini"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel(config.QUIZ_AI_MODEL)
        
        prompt = f"""You are creating an engaging interactive quiz to re-energize students during a lecture.

Based on the recent lecture content below, generate {config.NUM_QUESTIONS} questions that:
1. Test understanding of key concepts just taught
2. Are engaging and thought-provoking
3. Include a mix of question types
4. Are at {config.DIFFICULTY} difficulty level
5. Help students review and consolidate learning

Question types to include:
- Multiple choice (4 options, 1 correct)
- True/False
- Poll/Opinion questions (no right answer, gauge understanding)
- Quick recall questions

Recent Lecture Content:
{lecture_content}

Return ONLY a valid JSON object with this structure:
{{
  "title": "Quick Knowledge Check",
  "description": "Let's review what we just covered!",
  "questions": [
    {{
      "id": 1,
      "type": "multiple_choice",
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "Brief explanation of the answer",
      "points": 10
    }},
    {{
      "id": 2,
      "type": "poll",
      "question": "Which concept would you like more explanation on?",
      "options": ["Concept A", "Concept B", "Concept C", "All clear"],
      "correct_answer": null,
      "points": 5
    }},
    {{
      "id": 3,
      "type": "true_false",
      "question": "Statement to verify",
      "options": ["True", "False"],
      "correct_answer": 0,
      "explanation": "Why this is true/false",
      "points": 10
    }}
  ]
}}

Important: 
- Use question types: "multiple_choice", "true_false", "poll", "open_ended"
- For polls, set correct_answer to null
- Keep questions concise and clear
- Explanations should be 1-2 sentences
- Make it fun and engaging!
"""
        
        response = model.generate_content(prompt)
        text = response.text
        
        # Extract JSON from markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        quiz_data = json.loads(text)
        return quiz_data
    
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return create_fallback_quiz()

def generate_quiz_openai(lecture_content):
    """Generate quiz using OpenAI GPT"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""Create an engaging interactive quiz based on recent lecture content.

Lecture Content:
{lecture_content}

Generate {config.NUM_QUESTIONS} questions at {config.DIFFICULTY} difficulty.
Mix multiple choice, true/false, and poll questions.

Return as JSON with structure:
{{
  "title": "Quick Review",
  "questions": [
    {{
      "id": 1,
      "type": "multiple_choice",
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "correct_answer": 0,
      "explanation": "...",
      "points": 10
    }}
  ]
}}
"""
        
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        quiz_data = json.loads(response.choices[0].message.content)
        return quiz_data
    
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return create_fallback_quiz()

def create_fallback_quiz():
    """Fallback quiz if AI generation fails"""
    return {
        "title": "Quick Energy Break!",
        "description": "Let's take a quick interactive break",
        "questions": [
            {
                "id": 1,
                "type": "poll",
                "question": "How are you feeling about today's material so far?",
                "options": [
                    "😊 Clear and following along",
                    "🤔 Some parts are confusing",
                    "😵 Need more explanation",
                    "🚀 Ready for more challenges"
                ],
                "correct_answer": None,
                "points": 5
            },
            {
                "id": 2,
                "type": "poll",
                "question": "What would help you engage better right now?",
                "options": [
                    "Quick recap of key points",
                    "A practical example",
                    "A short break",
                    "Continue with new material"
                ],
                "correct_answer": None,
                "points": 5
            },
            {
                "id": 3,
                "type": "multiple_choice",
                "question": "Which teaching method helps you learn best?",
                "options": [
                    "Visual diagrams and charts",
                    "Step-by-step explanations",
                    "Hands-on practice",
                    "Real-world examples"
                ],
                "correct_answer": None,
                "points": 5
            }
        ]
    }

def gather_recent_content():
    """Gather recent lecture content from various sources"""
    content_parts = []
    
    # Get whiteboard OCR text
    if config.USE_WHITEBOARD_OCR:
        from pathlib import Path
        ocr_file = Path('whiteboard_notes/raw_ocr.txt')
        if ocr_file.exists():
            with open(ocr_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Get recent content (last N captures)
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                content_parts.append("Whiteboard Content:\n" + ''.join(recent_lines))
    
    # Get audio transcription (if available)
    if config.USE_AUDIO_TRANSCRIPTION:
        # Placeholder for audio transcription integration
        pass
    
    if not content_parts:
        return "No recent lecture content available. Generate general engagement questions."
    
    return "\n\n".join(content_parts)

def generate_quiz():
    """Main function to generate quiz"""
    print("="*60)
    print("GENERATING INTERACTIVE QUIZ")
    print("="*60)
    print(f"Trigger: Low class concentration detected")
    print(f"AI Provider: {config.QUIZ_AI_PROVIDER}")
    print(f"Questions: {config.NUM_QUESTIONS}")
    print(f"Difficulty: {config.DIFFICULTY}")
    print("="*60 + "\n")
    
    # Gather content
    print("📚 Gathering recent lecture content...")
    lecture_content = gather_recent_content()
    print(f"   Content length: {len(lecture_content)} characters\n")
    
    # Generate quiz
    print("🤖 Generating quiz with AI...")
    if config.QUIZ_AI_PROVIDER == 'gemini':
        quiz_data = generate_quiz_gemini(lecture_content)
    elif config.QUIZ_AI_PROVIDER == 'openai':
        quiz_data = generate_quiz_openai(lecture_content)
    else:
        print("   Unknown provider, using fallback")
        quiz_data = create_fallback_quiz()
    
    # Add metadata
    quiz_data['generated_at'] = datetime.now().isoformat()
    quiz_data['source'] = 'auto_trigger'
    quiz_data['trigger_reason'] = 'low_concentration'
    
    # Save quiz
    quiz_file = f"{config.OUTPUT_DIR}/current_quiz.json"
    with open(quiz_file, 'w', encoding='utf-8') as f:
        json.dump(quiz_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Quiz generated and saved to: {quiz_file}\n")
    print("="*60)
    print(f"Title: {quiz_data.get('title', 'Quiz')}")
    print(f"Questions: {len(quiz_data['questions'])}")
    print("="*60)
    
    return quiz_data, quiz_file

if __name__ == "__main__":
    quiz_data, quiz_file = generate_quiz()
    
    # Preview
    print("\nQuiz Preview:")
    for i, q in enumerate(quiz_data['questions'], 1):
        print(f"\n{i}. [{q['type']}] {q['question']}")
        for j, opt in enumerate(q['options']):
            marker = "✓" if q.get('correct_answer') == j else " "
            print(f"   {marker} {chr(65+j)}. {opt}")
