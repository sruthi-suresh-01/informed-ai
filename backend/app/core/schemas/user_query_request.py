from pydantic import BaseModel
from typing import List, Optional

class QuestionsRequest(BaseModel):
    question: str

class GetQuestionAndFactsResponse(BaseModel):
    question: str
    facts: Optional[List[str]] = None
    status: str
    source: Optional[str] = None
