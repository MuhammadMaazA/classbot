#!/usr/bin/env python3
"""
Generate structured notes from OCR text using LLM
"""

import os
from datetime import datetime
from dotenv import load_dotenv
import wb_config as config

# Load environment variables from .env file
load_dotenv()

def generate_notes_openai(raw_text):
    """Generate notes using OpenAI GPT"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""You are a helpful teaching assistant. Below is raw text extracted from whiteboard captures during a lecture using OCR. The text may have errors, be out of order, or contain fragments.

Your task:
1. Clean up and organize the text into coherent notes
2. Structure it with proper headings and bullet points
3. Fix OCR errors where obvious
4. Identify key concepts, formulas, and definitions
5. Add brief explanations where helpful
6. Use markdown formatting

Raw OCR Text:
{raw_text}

Generate well-organized lecture notes in markdown format:"""
        
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"❌ OpenAI Error: {e}\n\nSet OPENAI_API_KEY environment variable"

def generate_notes_gemini(raw_text):
    """Generate notes using Google Gemini"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        
        prompt = f"""You are a helpful teaching assistant. Below is raw text extracted from whiteboard captures during a lecture using OCR. The text may have errors, be out of order, or contain fragments.

Your task:
1. Clean up and organize the text into coherent notes
2. Structure it with proper headings and bullet points
3. Fix OCR errors where obvious
4. Identify key concepts, formulas, and definitions
5. Add brief explanations where helpful
6. Use markdown formatting

Raw OCR Text:
{raw_text}

Generate well-organized lecture notes in markdown format:"""
        
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        return f"❌ Gemini Error: {e}\n\nSet GOOGLE_API_KEY environment variable"

def generate_notes_anthropic(raw_text):
    """Generate notes using Anthropic Claude"""
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        prompt =f"""You are a helpful teaching assistant. Below is raw text extracted from whiteboard captures during a lecture using OCR. The text may have errors, be out of order, or contain fragments.

Your task:
1. Clean up and organize the text into coherent notes
2. Structure it with proper headings and bullet points
3. Fix OCR errors where obvious
4. Identify key concepts, formulas, and definitions
5. Add brief explanations where helpful
6. Use markdown formatting

Raw OCR Text:
{raw_text}

Generate well-organized lecture notes in markdown format:"""
        
        message = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    except Exception as e:
        return f"❌ Claude Error: {e}\n\nSet ANTHROPIC_API_KEY environment variable"

def generate_notes(input_file=None):
    """Generate notes from raw OCR text"""
    # Read raw text
    if input_file is None:
        input_file = config.RAW_TEXT_FILE
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    
    if not raw_text.strip():
        print("❌ No text found in input file")
        return
    
    print("="*60)
    print("GENERATING LECTURE NOTES")
    print("="*60)
    print(f"Input: {input_file}")
    print(f"LLM Provider: {config.LLM_PROVIDER}")
    print(f"Input length: {len(raw_text)} characters")
    print("="*60)
    print("\nProcessing... (this may take a moment)\n")
    
    # Generate notes based on provider
    if config.LLM_PROVIDER == 'openai':
        notes = generate_notes_openai(raw_text)
    elif config.LLM_PROVIDER == 'gemini':
        notes = generate_notes_gemini(raw_text)
    elif config.LLM_PROVIDER == 'anthropic':
        notes = generate_notes_anthropic(raw_text)
    elif config.LLM_PROVIDER == 'none':
        notes = "# Lecture Notes\n\n" + raw_text
        print("⚠ No LLM processing (config.LLM_PROVIDER = 'none')")
    else:
        notes = f"❌ Unknown LLM provider: {config.LLM_PROVIDER}"
    
    # Save notes
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = f"""# Lecture Notes
**Generated:** {timestamp}  
**Source:** Whiteboard OCR Captures  
**Provider:** {config.LLM_PROVIDER}

---

"""
    
    full_notes = header + notes
    
    with open(config.NOTES_FILE, 'w', encoding='utf-8') as f:
        f.write(full_notes)
    
    print("="*60)
    print("✓ NOTES GENERATED")
    print("="*60)
    print(f"Saved to: {config.NOTES_FILE}")
    print(f"Length: {len(notes)} characters")
    print("="*60)
    print("\nPreview:")
    print("-"*60)
    print(notes[:500] + "..." if len(notes) > 500 else notes)
    print("-"*60)

if __name__ == "__main__":
    import sys
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    generate_notes(input_file)
