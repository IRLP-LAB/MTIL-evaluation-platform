from fastapi import HTTPException
import mysql.connector as connector
from datetime import timedelta

from database import db_conn
from app.utils.auth import get_user
from app.utils.auth import pwd_context, authenticate_user
from app.utils.token import create_access_token, create_token
from app.models.util import Token

def signup(user):
    try:
        existing_user = get_user(user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        cursor = db_conn.cursor(dictionary=True)

        #Check email already exists
        query_email = "SELECT email FROM users WHERE email = %s"
        cursor.execute(query_email, (user.email,))
        result = cursor.fetchone()
        if result:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        #Database insertion
        hashed_password = pwd_context.hash(user.password)
        query = """
            INSERT INTO users (username, password, first_name, last_name, phone, affiliated_institute, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            user.username,
            hashed_password,
            user.first_name,
            user.last_name,
            user.phone,
            user.affiliated_institute,
            user.email
        )
        cursor.execute(query, values)
        db_conn.commit()
        cursor.close()

        #TODO: Send Varification email to user
        return {"message": "User created successfully"}
    except connector.Error as err:
        print(err)
        raise HTTPException(status_code=500, detail="Database error") from err
    
def signin(user):
    try:
        #TODO: CHeck if mail varification is done
        authenticated_user = authenticate_user(user.username, user.password)
        if not authenticated_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token(authenticated_user['username'])
        refresh_token = create_token({'sub': authenticated_user['username']}, timedelta(days=30))
        return Token(access_token=access_token, refresh_token=refresh_token)
    except connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err
