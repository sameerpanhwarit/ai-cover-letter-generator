from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.utils.resume_parser import extract_text_from_resume
from app.services.generator import generate_cover_letter
from app.schemas.coverletter import CoverLetterResponse

router = APIRouter()

@router.post("/generate", response_model=CoverLetterResponse)
async def generate_cover_letter_api(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    tone: str = Form("professional"),
    word_limit: int = Form(300)
):
    content = await resume.read()
    try:
        resume_text = extract_text_from_resume(resume.filename, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    letter = await generate_cover_letter({
        "resume": resume_text,
        "job_description": job_description,
        "tone": tone,
        "word_limit": word_limit
    })
    return {"cover_letter": letter}
