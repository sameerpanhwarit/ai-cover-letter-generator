import httpx
import re
from fastapi import HTTPException
from app.config import settings

async def get_ats_score(cv_text: str) -> float:
    prompt = f"""
You are a world-class Applicant Tracking System (ATS) used by top companies.

Your task is to evaluate the following resume and return an ATS compatibility score based on the following criteria:

- Overall structure and readability
- Keyword relevance for common job roles (backend, frontend, fullstack, data, devops, etc.)
- Presence of key sections (contact info, skills, experience, education)
- Format and clarity
- Use of action words and measurable results

Return **only a numeric score from 0 to 100** — no text, no explanation, no formatting. The score should reflect how well this resume would perform in modern ATS systems.

Resume:
{cv_text}
"""

    try:
        timeout = httpx.Timeout(30.0)  # 30 seconds timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                settings.LLM_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.LLM_API_KEY}",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "ATSScoreChecker"
                },
                json={
                    "model": "qwen/qwen3-coder:free",  # or the same model you're using in /generate
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
            )

        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()

        # Extract numeric score (0-100)
        score_match = re.search(r"\b([0-9]{1,3})\b", content)
        if score_match:
            score = int(score_match.group(1))
            return max(0, min(score, 100))  # Clamp to 0–100
        else:
            raise ValueError(f"No numeric score found in response: {content}")

    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="LLM API timed out while scoring the resume.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
