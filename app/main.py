from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.schemas import ResumeInput, ResumeEvaluation
from app.agent import screen_resume

app = FastAPI(title="Resume Screener AI Agent")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Screener AI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-width: 800px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #555;
            font-weight: 600;
            margin-bottom: 8px;
        }
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .results {
            margin-top: 30px;
            display: none;
        }
        .results.show {
            display: block;
        }
        .result-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .score {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            text-align: center;
            margin-bottom: 20px;
        }
        .recommendation {
            text-align: center;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-weight: 600;
            font-size: 18px;
        }
        .recommendation.hire {
            background: #d4edda;
            color: #155724;
        }
        .recommendation.reject {
            background: #f8d7da;
            color: #721c24;
        }
        .strengths, .weaknesses {
            margin-bottom: 15px;
        }
        .strengths h3, .weaknesses h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .strengths h3 {
            color: #28a745;
        }
        .weaknesses h3 {
            color: #dc3545;
        }
        ul {
            list-style: none;
            padding-left: 0;
        }
        li {
            padding: 8px 0;
            padding-left: 20px;
            position: relative;
            color: #555;
        }
        .strengths li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #28a745;
            font-weight: bold;
        }
        .weaknesses li:before {
            content: "✗";
            position: absolute;
            left: 0;
            color: #dc3545;
            font-weight: bold;
        }
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            font-weight: 600;
        }
        .loading.show {
            display: block;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 5px;
            margin-top: 20px;
            display: none;
        }
        .error.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Resume Screener AI</h1>
        
        <form id="screeningForm">
            <div class="form-group">
                <label for="jobDescription">Job Description</label>
                <textarea id="jobDescription" name="jobDescription" rows="6" placeholder="Paste the job description here..." required></textarea>
            </div>

            <div class="form-group">
                <label for="resumeText">Resume Text</label>
                <textarea id="resumeText" name="resumeText" rows="8" placeholder="Paste the resume here..." required></textarea>
            </div>

            <button type="submit">Analyze Resume</button>
        </form>

        <div class="loading" id="loading">
            <p>🔄 Analyzing resume...</p>
        </div>

        <div class="error" id="error"></div>

        <div class="results" id="results">
            <div class="result-card">
                <div class="score" id="score">-</div>
                <div class="recommendation" id="recommendation">-</div>
                
                <div class="strengths" id="strengthsDiv"></div>
                <div class="weaknesses" id="weaknessesDiv"></div>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('screeningForm');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const errorDiv = document.getElementById('error');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const jobDescription = document.getElementById('jobDescription').value;
            const resumeText = document.getElementById('resumeText').value;

            loading.classList.add('show');
            results.classList.remove('show');
            errorDiv.classList.remove('show');

            try {
                const response = await fetch('/screen-resume', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        job_description: jobDescription,
                        resume_text: resumeText
                    })
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                displayResults(data);
            } catch (error) {
                console.error('Error:', error);
                errorDiv.textContent = 'Error analyzing resume: ' + error.message;
                errorDiv.classList.add('show');
            } finally {
                loading.classList.remove('show');
            }
        });

        function displayResults(data) {
            // Score
            document.getElementById('score').textContent = data.score + '/100';

            // Recommendation
            const recommendationEl = document.getElementById('recommendation');
            recommendationEl.textContent = '👤 Recommendation: ' + data.recommendation;
            recommendationEl.className = 'recommendation ' + data.recommendation.toLowerCase();

            // Strengths
            const strengthsDiv = document.getElementById('strengthsDiv');
            if (data.strengths && data.strengths.length > 0) {
                strengthsDiv.innerHTML = '<h3>✓ Strengths</h3><ul>' +
                    data.strengths.map(s => '<li>' + s + '</li>').join('') +
                    '</ul>';
            }

            // Weaknesses
            const weaknessesDiv = document.getElementById('weaknessesDiv');
            if (data.weaknesses && data.weaknesses.length > 0) {
                weaknessesDiv.innerHTML = '<h3>✗ Weaknesses</h3><ul>' +
                    data.weaknesses.map(w => '<li>' + w + '</li>').join('') +
                    '</ul>';
            }

            results.classList.add('show');
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTML_TEMPLATE


@app.post("/screen-resume", response_model=ResumeEvaluation)
def screen_resume_api(data: ResumeInput):
    return screen_resume(
        resume_text=data.resume_text,
        job_description=data.job_description
    )
