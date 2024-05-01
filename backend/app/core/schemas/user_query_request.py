from pydantic import BaseModel
from typing import List, Optional

class QuestionsRequest(BaseModel):
    question: str
    user_id: str

class GetQuestionAndFactsResponse(BaseModel):
    question: str
    facts: Optional[List[str]] = None
    status: str
