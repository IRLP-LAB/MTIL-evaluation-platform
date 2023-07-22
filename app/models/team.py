from pydantic import BaseModel, EmailStr
from typing import List

class Team(BaseModel):
    team_name: str
    emails: List[EmailStr]
    leader_id: int