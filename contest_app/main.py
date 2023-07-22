from fastapi import FastAPI
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.profile import router as profile_router
from app.api.endpoints.team import router as team_router
# https://chat.openai.com/c/67f60051-698d-43c0-bced-6192ee6ac172
app = FastAPI()

app.include_router(auth_router, tags=["Authentication"])
app.include_router(profile_router, tags=["Profile"])
app.include_router(team_router, tags=["Team"])
