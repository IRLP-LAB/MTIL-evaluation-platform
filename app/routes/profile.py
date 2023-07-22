from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.services import profile_service
from app.models.user import UpdateProfile

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")

@router.get("/profile")
def view_profile(token: str = Depends(oauth2_scheme)):
    return profile_service.view_profile(token)

@router.put("/profile")
def update_profile(profile: UpdateProfile, token: str = Depends(oauth2_scheme)):
    return profile_service.update_profile(profile, token)