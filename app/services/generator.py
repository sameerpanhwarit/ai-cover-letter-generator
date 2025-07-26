import httpx
import re
from fastapi import HTTPException
from app.config import settings

def clean_output(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    
    lines = text.strip().split("\n")
    cleaned = []
    seen_salutation = False
    for line in lines:
        if line.strip().lower().startswith("dear"):
            if seen_salutation:
                continue  
            seen_salutation = True
        if "here is the cover letter" in line.lower():
            continue  
        cleaned.append(line)
    
    return "\n".join(cleaned).strip()


def extract_company_name(job_description: str) -> str | None:
    match = re.search(r"(?:at|@)\s+([A-Z][A-Za-z0-9&.\- ]+)", job_description)
    return match.group(1).strip() if match else None

def extract_company_and_title(job_description: str):
    company_match = re.search(r'at\s+([A-Z][\w&.\s\-]{2,})', job_description, re.IGNORECASE)
    title_match = re.search(r'(?:position|role|job)\s+(?:of|as)?\s*([A-Z][\w\s]{2,})', job_description, re.IGNORECASE)

    company_name = company_match.group(1).strip() if company_match else None
    job_title = title_match.group(1).strip() if title_match else None

    return company_name, job_title

def clean_cover_letter(text: str):
    text = text.strip()

    patterns_to_remove = [
        r"(?i)^here\s+is\s+(a|the)?\s?(professional|clean|well-structured)?\s?cover letter.*?:?\s*",  
        r"(?i)^based\s+on\s+the\s+provided\s+resume.*?:?\s*",
        r"(?i)^below\s+is\s+(a|the)?\s?(professional|clean)?\s?cover letter.*?:?\s*",
    ]
    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text)

    lines = text.splitlines()
    seen = set()
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line not in seen:
            seen.add(line)
            cleaned.append(line)

    return '\n'.join(cleaned)



async def generate_cover_letter(data: dict) -> str:
    company_name = extract_company_name(data['job_description'])
    
    subject_line = f"Subject: Application for {data['position']} Position" if "position" in data else "Subject: Job Application"
    salutation = f"Dear Hiring Manager{f' at {company_name}' if company_name else ''},"

    company_name, job_title = extract_company_and_title(data['job_description'])


    prompt = f"""
    You are a professional cover letter writer.

    Your ONLY task is to generate a clean, well-structured cover letter using the resume and job description below. The cover letter MUST follow these rules:

    Rules:
    - Use a professional tone — {data['tone'].lower()}.
    - Keep it under {data['word_limit']} words.
    - Do NOT write any introduction or comments like "Here is your cover letter."
    - DO NOT repeat the greeting (e.g., write "Dear Hiring Manager," only once).
    - DO NOT include markdown, bullet poipreamblesnts, or formatting tags.
    - ONLY return the body of the cover letter as plain text. No preambles, no notes.

    If a company name is found, use it. Otherwise, say "your organization."
    If a job title is found, mention it once in a natural way.

    ---

    Resume:
    {data['resume']}

    Job Description:
    {data['job_description']}
    """




    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.LLM_API_URL,
            headers={
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "CoverLetterGenerator"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )

        try:
            result = response.json()
            raw_text = result["choices"][0]["message"]["content"]
            cleaned_text = clean_output(raw_text)  # optional
            final_letter = clean_cover_letter(cleaned_text)

            if not final_letter.lower().startswith("dear"):
                final_letter = f"{salutation}\n\n{final_letter}"

            return final_letter

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
