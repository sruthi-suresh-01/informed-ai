from pydantic import BaseModel
from typing import List, Optional

class CreateUserRequest(BaseModel):
    username: str
    email: str