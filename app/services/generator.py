import httpx
import re
from fastapi import HTTPException
from app.config import settings
import asyncio


MAX_RETRIES = 3 
RETRY_DELAY = 2

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

# def clean_cover_letter(text: str):
#     text = text.strip()

#     patterns_to_remove = [
#         r"(?i)^here\s+is\s+(a|the)?\s?(professional|clean|well-structured)?\s?cover letter.*?:?\s*",  
#         r"(?i)^based\s+on\s+the\s+provided\s+resume.*?:?\s*",
#         r"(?i)^below\s+is\s+(a|the)?\s?(professional|clean)?\s?cover letter.*?:?\s*",
#     ]
#     for pattern in patterns_to_remove:
#         text = re.sub(pattern, "", text)

#     lines = text.splitlines()
#     seen = set()
#     cleaned = []
#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue
#         if line not in seen:
#             seen.add(line)
#             cleaned.append(line)

#     return '\n'.join(cleaned)


def clean_cover_letter(text: str) -> str:
    # Remove markdown
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)

    # Remove common LLM-generated preambles
    preamble_patterns = [
        r"(?i)^here\s+(is|are)\s+(a|the)?\s?(clean|professional|well-structured)?\s?cover letter.*?:?\s*",
        r"(?i)^based\s+on\s+(the\s+)?(resume|job\s+description).{0,80}$",
        r"(?i)^below\s+is\s+(a|the)?\s?(clean|professional)?\s?cover letter.*?:?\s*",
    ]
    for pattern in preamble_patterns:
        text = re.sub(pattern, "", text.strip(), flags=re.MULTILINE)

    # Remove duplicate greetings like “Dear Hiring Manager”
    lines = text.splitlines()
    seen_greeting = False
    cleaned = []
    for line in lines:
        if line.lower().strip().startswith("dear") and seen_greeting:
            continue
        if line.lower().strip().startswith("dear"):
            seen_greeting = True
        cleaned.append(line.strip())

    return "\n".join([line for line in cleaned if line]).strip()




# async def generate_cover_letter(data: dict) -> str:
#     company_name = extract_company_name(data['job_description'])
    
#     subject_line = f"Subject: Application for {data['position']} Position" if "position" in data else "Subject: Job Application"
#     salutation = f"Dear Hiring Manager{f' at {company_name}' if company_name else ''},"

#     company_name, job_title = extract_company_and_title(data['job_description'])


#     # prompt = f"""
#     # You are a professional cover letter writer.

#     # Your ONLY task is to generate a clean, well-structured cover letter using the resume and job description below. The cover letter MUST follow these rules:

#     # Rules:
#     # - Use a professional tone — {data['tone'].lower()}.
#     # - Keep it under {data['word_limit']} words.
#     # - Do NOT write any introduction or comments like "Here is your cover letter."
#     # - DO NOT repeat the greeting (e.g., write "Dear Hiring Manager," only once).
#     # - DO NOT include markdown, bullet poipreamblesnts, or formatting tags.
#     # - ONLY return the body of the cover letter as plain text. No preambles, no notes.

#     # If a company name is found, use it. Otherwise, say "your organization."
#     # If a job title is found, mention it once in a natural way.

#     # ---

#     # Resume:
#     # {data['resume']}

#     # Job Description:
#     # {data['job_description']}
#     # """


#     prompt = f"""
#     You are a professional cover letter writer.
# 60
#     Your ONLY task is to generate a clean, formal, and well-structured cover letter based on the resume and job description provided below.

#     STRICT RULES:
#     - Write in a professional tone — {data['tone'].lower()}.
#     - Stay strictly under {data['word_limit']} words.
#     - DO NOT include introductory lines like "Here is your cover letter".
#     - DO NOT repeat greetings like "Dear Hiring Manager".
#     - DO NOT include markdown, bullet points, formatting tags, or section labels.
#     - DO NOT mention the resume or job description explicitly.
#     - Mention the job title and company naturally, but only once.
#     - End with a formal closing such as "Sincerely," followed by the candidate’s full name, phone number, and email (only if found in the resume).

#     Your response should contain ONLY the final cover letter — no preambles, no extra comments.

#     ---
#     Resume:
#     {data['resume']}

#     Job Description:
#     {data['job_description']}
#     """





#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             settings.LLM_API_URL,
#             headers={
#                 "Authorization": f"Bearer {settings.LLM_API_KEY}",
#                 "HTTP-Referer": "http://localhost:8000",
#                 "X-Title": "CoverLetterGenerator"
#             },
#             json={
#                 # "model": "meta-llama/llama-3-8b-instruct",
#                 "model":"qwen/qwen3-coder:free",
#                 "messages": [{"role": "user", "content": prompt}],
#                 "temperature": 0.7
#             }
#         )

#         try:
#             result = response.json()
#             raw_text = result["choices"][0]["message"]["content"]
#             cleaned_text = clean_output(raw_text)  # optional
#             final_letter = clean_cover_letter(cleaned_text)

#             # if not final_letter.lower().startswith("dear"):
#             #     final_letter = f"{salutation}\n\n{final_letter}"

#             if not final_letter.lower().startswith("dear"):
#                 final_letter = f"{salutation}\n\n{final_letter}"

#             return final_letter

#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")


async def generate_cover_letter(data: dict) -> str:
    company_name = extract_company_name(data['job_description'])
    salutation = f"Dear Hiring Manager{f' at {company_name}' if company_name else ''},"
    company_name, job_title = extract_company_and_title(data['job_description'])

    prompt = f"""
    You are a professional cover letter writer.

    Your ONLY task is to generate a clean, formal, and well-structured cover letter based on the resume and job description provided below.

    STRICT RULES:
    - Write in a professional tone — {data['tone'].lower()}.
    - The final cover letter MUST be exactly {data['word_limit']} words — not more, not less.
    - DO NOT include introductory lines like "Here is your cover letter".
    - DO NOT repeat greetings like "Dear Hiring Manager".
    - DO NOT include markdown, bullet points, formatting tags, or section labels.
    - DO NOT mention the resume or job description explicitly.
    - Mention the job title and company naturally, but only once.
    - End with a formal closing such as "Sincerely," followed by the candidate’s full name, phone number, and email (only if found in the resume).

    Your response should contain ONLY the final cover letter — no preambles, no extra comments.

    ---
    Resume:
    {data['resume']}

    Job Description:
    {data['job_description']}
    """

    for attempt in range(MAX_RETRIES):
        print(f"Attempt {attempt+1} to generate cover letter...") 
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.LLM_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.LLM_API_KEY}",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "CoverLetterGenerator"
                    },
                    json={
                        "model": "qwen/qwen3-coder:free",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7
                    }
                )

                result = response.json()

                # Robustly check for 'choices'
                if "choices" in result and isinstance(result["choices"], list):
                    raw_text = result["choices"][0]["message"]["content"]
                else:
                    raise ValueError("LLM response missing 'choices' key")

                cleaned_text = clean_output(raw_text)
                final_letter = clean_cover_letter(cleaned_text)

                if not final_letter.lower().startswith("dear"):
                    final_letter = f"{salutation}\n\n{final_letter}"

                return final_letter

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                raise HTTPException(status_code=500, detail=f"Final LLM error after retries: {str(e)}")
