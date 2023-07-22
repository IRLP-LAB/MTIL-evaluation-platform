from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.services import auth_service
from app.models.user import User
from app.models.auth import SignupUser

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")

@router.post("/signup")
def signup(user: SignupUser):
    return auth_service.signup(user)

@router.post("/signin")
def signin(user: User):
    return auth_service.signin(user)

