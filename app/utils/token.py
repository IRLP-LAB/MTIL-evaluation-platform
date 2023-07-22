from database import db_conn
from fastapi import HTTPException
import mysql.connector as connector
from datetime import datetime, timedelta
from jose import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token(username: str):
    access_token_expires = timedelta(minutes=5)
    return create_token({'sub': username}, access_token_expires)

def store_revoked_token(token: str):
    try:
        cursor = db_conn.cursor()
        query = f"INSERT INTO _revoked_tokens (token) VALUES (%s)"
        cursor.execute(query, (token,))
        db_conn.commit()
        cursor.close()
    except connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err
    
def is_token_revoked(token: str) -> bool:
    try:
        cursor = db_conn.cursor()
        query = "SELECT COUNT(*) FROM _revoked_tokens WHERE token = %s"
        cursor.execute(query, (token,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
    except connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err