from pydantic import BaseModel

class ATSScoreResponse(BaseModel):
    score: float
