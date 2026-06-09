from pydantic import BaseModel

class ReviewOutput(BaseModel):
    score: int
    issues: list[str]
    recommendation: str