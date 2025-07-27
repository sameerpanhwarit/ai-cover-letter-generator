# Cover Letter Generator API

A FastAPI-based backend service that generates professional cover letters using a user's resume and a job description. The service leverages an external LLM (Large Language Model) API to produce tailored cover letters.

## Features
- Upload a resume (PDF or DOCX) and a job description to generate a cover letter.
- Customizable tone and word limit for the generated letter.
- Clean, plain-text output suitable for direct use.
- Check your resume's ATS (Applicant Tracking System) compatibility score.

## Directory Structure
```
app/
  ├── api/           # API route definitions
  │    └── routes.py
  ├── services/      # Business logic (cover letter generation)     
  |    ├──   generator.py
  │    └── ats.py         # Business logic for ATS score checking
  ├── utils/         # Utility functions (resume parsing)
  │    └── resume_parser.py
  ├── schemas/       # Pydantic models for request/response
  │    ├── coverletter.py
  │    └── ats.py         # Pydantic model for ATS score response
  ├── config.py      # Configuration (env variables)
  └── main.py        # FastAPI app entry point
Dockerfile           # Containerization setup
requirements.txt     # Python dependencies
.dockerignore        # Files/folders excluded from Docker builds
```

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/sameerpanhwarit/ai-cover-letter-generator
cd coverletter-api
```

### 2. Set up a virtual environment (optional but recommended)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
Create a `.env` file in the project root with the following variables:
```
LLM_API_KEY=your_llm_api_key
LLM_API_URL=https://your-llm-api-endpoint
```

## Usage
### Run locally
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.

### Run with Docker
Build and start the container:
```bash
docker build -t coverletter-api .
docker run -p 8000:8000 --env-file .env coverletter-api
```

## API Endpoint
### `POST /api/v1/generate`
- **Description:** Generate a cover letter from a resume and job description.
- **Request:**
  - `resume`: File upload (PDF or DOCX)
  - `job_description`: String (form field)
  - `tone`: String (form field, default: "professional")
  - `word_limit`: Integer (form field, default: 300)
- **Response:**
  - `cover_letter`: String (the generated cover letter)

#### Example (using `curl`):
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description=Job description text here" \
  -F "tone=enthusiastic" \
  -F "word_limit=250"
```

### `POST /api/v1/ats-score`
- **Description:** Get an ATS (Applicant Tracking System) compatibility score for a resume. The score (0-100) estimates how well the resume would perform in automated resume screening systems.
- **Request:**
  - `resume`: File upload (PDF or DOCX)
- **Response:**
  - `score`: Float (the ATS compatibility score, 0-100)

#### Example (using `curl`):
```bash
curl -X POST "http://localhost:8000/api/v1/ats-score" \
  -F "resume=@/path/to/resume.pdf"
```

## Core Components
- **app/api/routes.py**: Defines the `/generate` and `/ats-score` endpoints, handles file upload, and orchestrates cover letter generation and ATS scoring.
- **app/services/generator.py**: Contains logic to build prompts and interact with the LLM API for cover letter generation, and post-processes the generated text.
- **app/services/ats.py**: Contains logic to build prompts and interact with the LLM API for ATS score calculation.
- **app/utils/resume_parser.py**: Extracts text from PDF and DOCX resumes (used by both endpoints).
- **app/schemas/coverletter.py**: Pydantic model for the cover letter API response.
- **app/schemas/ats.py**: Pydantic model for the ATS score API response.
- **app/config.py**: Loads environment variables for configuration.

## Dependencies
Key packages (see `requirements.txt` for full list):
- fastapi
- uvicorn
- httpx
- pydantic
- python-dotenv
- PyMuPDF
- python-docx
- redis

## Docker
- The `Dockerfile` sets up a minimal Python environment, installs dependencies, and runs the FastAPI app with Uvicorn.
- The `.dockerignore` file excludes virtual environments, cache, compiled files, and local environment files from the Docker build context.

## License
MIT (or specify your license here) 