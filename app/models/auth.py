from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    phone: Optional[str] = None
    affiliated_institute: Optional[str] = None
    email: EmailStr