# Resume Screener AI Agent

An AI-powered resume screening tool that uses Google's Gemini API to evaluate resumes against job descriptions.

## Features

- Analyzes resumes against job descriptions
- Provides match scores (0-100)
- Identifies strengths and weaknesses
- Gives hiring recommendations
- Returns structured JSON responses

## Setup

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API key:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### POST /screen-resume

Evaluate a resume against a job description.

**Request:**
```json
{
  "resume_text": "John Doe\n...",
  "job_description": "We are looking for..."
}
```

**Response:**
```json
{
  "score": 85,
  "strengths": [
    "5+ years of relevant experience",
    "Strong technical skills"
  ],
  "weaknesses": [
    "Missing cloud experience",
    "No leadership background"
  ],
  "recommendation": "Hire"
}
```

## Project Structure

- `app/main.py` - FastAPI application and routes
- `app/agent.py` - Resume screening logic using Gemini API
- `app/schemas.py` - Pydantic data models
- `app/prompts.py` - AI prompts and instructions
- `tests/sample_data.py` - Sample test data

## Testing

Use the provided Swagger UI at `http://localhost:8000/docs` to test the API interactively.

## License

MIT
