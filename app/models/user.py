from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    password: str

class UpdateProfile(BaseModel):
    first_name: str
    last_name: str
    new_password: str
    phone: Optional[str] = None
    affiliated_institute: Optional[str] = None
    old_password: str