from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
load_dotenv()

from app.routes.auth import router as auth_router
from app.routes.profile import router as profile_router
from app.routes.team import router as team_router
from app.utils.error_handler import (
    http_exception_handler,
    generic_exception_handler,
    user_not_found_exception_handler,
    invalid_password_exception_handler,
    UserNotFoundException,  # Import the custom exceptions
    InvalidPasswordException  # Import the custom exceptions
)

app = FastAPI()

#Custom Error Handlers channel
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(UserNotFoundException, user_not_found_exception_handler)
app.add_exception_handler(InvalidPasswordException, invalid_password_exception_handler)

app.include_router(auth_router, tags=["Authentication"])
app.include_router(profile_router, tags=["Profile"])
app.include_router(team_router, tags=["Team"])

