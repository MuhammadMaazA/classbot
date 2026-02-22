#!/usr/bin/env python3
"""
Web server for interactive quiz
Students access via browser (mobile/desktop)
"""

from flask import Flask, render_template_string, request, jsonify
import json
import os
from datetime import datetime
import poll_config as config
import threading
import webbrowser
import time

app = Flask(__name__)

# Global state
current_quiz = None
responses = {}
quiz_active = False
quiz_start_time = None

# HTML template for quiz interface
QUIZ_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ quiz.title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .description {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .timer {
            background: #ff6b6b;
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            display: inline-block;
            font-size: 1.2em;
            margin-bottom: 20px;
            font-weight: bold;
        }
        .question {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            border-left: 5px solid #667eea;
        }
        .question-number {
            color: #667eea;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .question-text {
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #333;
        }
        .options {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .option {
            background: white;
            border: 2px solid #e0e0e0;
            padding: 15px 20px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1.1em;
        }
        .option:hover {
            border-color: #667eea;
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }
        .option.selected {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        .submit-btn {
            background: #51cf66;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.2em;
            border-radius: 10px;
            cursor: pointer;
            width: 100%;
            font-weight: bold;
            transition: all 0.3s;
        }
        .submit-btn:hover {
            background: #40c057;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(81, 207, 102, 0.3);
        }
        .submit-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .thank-you {
            text-align: center;
            padding: 50px 20px;
        }
        .thank-you h2 {
            color: #51cf66;
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        .results {
            margin-top: 30px;
        }
        .result-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .correct {
            border-left: 5px solid #51cf66;
        }
        .incorrect {
            border-left: 5px solid #ff6b6b;
        }
        @media (max-width: 600px) {
            .container { padding: 20px; }
            h1 { font-size: 1.5em; }
            .question-text { font-size: 1.1em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ quiz.title }}</h1>
        <p class="description">{{ quiz.description }}</p>
        
        {% if time_remaining %}
        <div class="timer" id="timer">⏱️ Time: <span id="time-left">{{ time_remaining }}</span>s</div>
        {% endif %}
        
        <form id="quiz-form">
            {% for question in quiz.questions %}
            <div class="question">
                <div class="question-number">Question {{ question.id }} / {{ quiz.questions|length }}</div>
                <div class="question-text">{{ question.question }}</div>
                <div class="options">
                    {% for option in question.options %}
                    <div class="option" data-question="{{ question.id }}" data-answer="{{ loop.index0 }}" 
                         onclick="selectOption(this)">
                        {{ option }}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
            
            <button type="submit" class="submit-btn">Submit Answers 🚀</button>
        </form>
    </div>
    
    <script>
        const answers = {};
        
        function selectOption(element) {
            const questionId = element.dataset.question;
            const answer = element.dataset.answer;
            
            // Deselect other options for this question
            document.querySelectorAll(`[data-question="${questionId}"]`).forEach(opt => {
                opt.classList.remove('selected');
            });
            
            // Select this option
            element.classList.add('selected');
            answers[questionId] = parseInt(answer);
        }
        
        // Timer countdown
        {% if time_remaining %}
        let timeLeft = {{ time_remaining }};
        const timerInterval = setInterval(() => {
            timeLeft--;
            document.getElementById('time-left').textContent = timeLeft;
            
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                document.getElementById('quiz-form').submit();
            }
        }, 1000);
        {% endif %}
        
        // Form submission
        document.getElementById('quiz-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const response = await fetch('/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(answers)
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.location.href = '/results';
            }
        });
    </script>
</body>
</html>
"""

RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Quiz Results</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #51cf66 0%, #37b24d 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        h1 {
            color: #51cf66;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .score {
            font-size: 3em;
            color: #667eea;
            margin: 20px 0;
            font-weight: bold;
        }
        .message {
            font-size: 1.2em;
            color: #666;
            margin-bottom: 30px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 Thank You!</h1>
        <p class="message">Your answers have been submitted</p>
        
        {% if score is not none %}
        <div class="score">{{ score }}%</div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{{ correct }}</div>
                <div class="stat-label">Correct</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ total }}</div>
                <div class="stat-label">Total</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ participants }}</div>
                <div class="stat-label">Participants</div>
            </div>
        </div>
        {% endif %}
        
        <p style="margin-top: 30px; color: #666;">
            Let's continue with the lecture! 📚
        </p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Main quiz page"""
    global quiz_start_time, quiz_active
    
    if not current_quiz or not quiz_active:
        return "<h1>No active quiz</h1><p>Wait for the teacher to start an activity!</p>"
    
    time_elapsed = int(time.time() - quiz_start_time) if quiz_start_time else 0
    time_remaining = max(0, config.QUIZ_DURATION - time_elapsed)
    
    return render_template_string(QUIZ_TEMPLATE, 
                                 quiz=current_quiz, 
                                 time_remaining=time_remaining)

@app.route('/submit', methods=['POST'])
def submit():
    """Submit quiz answers"""
    student_id = request.remote_addr  # Use IP as temp ID
    data = request.json
    
    # Store response
    responses[student_id] = {
        'answers': data,
        'timestamp': datetime.now().isoformat()
    }
    
    # Save responses
    with open(config.QUIZ_RESULTS_FILE, 'w') as f:
        json.dump({'responses': responses, 'quiz': current_quiz}, f, indent=2)
    
    return jsonify({'success': True})

@app.route('/results')
def results():
    """Show results page"""
    student_id = request.remote_addr
    
    if student_id not in responses:
        return "<h1>No submission found</h1>"
    
    # Calculate score
    user_answers = responses[student_id]['answers']
    correct = 0
    total = 0
    
    for question in current_quiz['questions']:
        if question.get('correct_answer') is not None:
            total += 1
            user_answer = user_answers.get(str(question['id']))
            if user_answer == question['correct_answer']:
                correct += 1
    
    score = int((correct / total * 100)) if total > 0 else None
    
    return render_template_string(RESULTS_TEMPLATE, 
                                 score=score,
                                 correct=correct,
                                 total=total,
                                 participants=len(responses))

def start_quiz_server(quiz_data):
    """Start the web server with quiz"""
    global current_quiz, quiz_active, quiz_start_time, responses
    
    current_quiz = quiz_data
    quiz_active = True
    quiz_start_time = time.time()
    responses = {}
    
    print("\n" + "="*60)
    print("🌐 STARTING WEB SERVER")
    print("="*60)
    print(f"URL: http://localhost:{config.WEB_PORT}")
    print(f"Duration: {config.QUIZ_DURATION} seconds")
    print("="*60)
    print("\n📱 Students can access the quiz at:")
    print(f"   http://{get_local_ip()}:{config.WEB_PORT}")
    print("\n" + "="*60)
    
    if config.AUTO_OPEN_BROWSER:
        threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{config.WEB_PORT}')).start()
    
    app.run(host='0.0.0.0', port=config.WEB_PORT, debug=False)

def get_local_ip():
    """Get local IP address"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

if __name__ == "__main__":
    # Test with sample quiz
    quiz_file = f"{config.OUTPUT_DIR}/current_quiz.json"
    
    if os.path.exists(quiz_file):
        with open(quiz_file, 'r') as f:
            quiz_data = json.load(f)
        start_quiz_server(quiz_data)
    else:
        print("No quiz found. Run: python quiz_generator.py first")
