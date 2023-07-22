from fastapi import HTTPException
from fastapi.responses import JSONResponse

class UserNotFoundException(HTTPException):
    def __init__(self, detail="User not found"):
        super().__init__(status_code=404, detail=detail)

class InvalidPasswordException(HTTPException):
    def __init__(self, detail="Invalid password"):
        super().__init__(status_code=401, detail=detail)

async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

async def generic_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

async def user_not_found_exception_handler(request, exc: UserNotFoundException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

async def invalid_password_exception_handler(request, exc: InvalidPasswordException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
