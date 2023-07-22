from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from app.services import team_service
from app.models.team import Team

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")

@router.post("/create_team")
async def create_team(team: Team, token: str = Depends(oauth2_scheme)):
    return await team_service.create_team(team, token)
