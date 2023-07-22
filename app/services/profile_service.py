from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
import mysql.connector as connector
from passlib.context import CryptContext
import os

from database import db_conn
from app.utils.token import is_token_revoked
from app.utils.auth import verify_password


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def view_profile(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        cursor = db_conn.cursor(dictionary=True)

        # Check if the token is revoked
        if is_token_revoked(token):
            raise HTTPException(status_code=401, detail="Token revoked")

        # Retrieve the user data excluding the password field
        query = "SELECT id, username, first_name, last_name, phone, affiliated_institute, email FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err
    
def update_profile(profile, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        cursor = db_conn.cursor(dictionary=True)

        # Check if the token is revoked
        if is_token_revoked(token):
            raise HTTPException(status_code=401, detail="Token revoked")

        # Retrieve the user's current password from the database
        query_password = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query_password, (username,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        current_password = result["password"]

        # Check if the provided old password matches the current password
        if not verify_password(profile.old_password, current_password):
            raise HTTPException(status_code=401, detail="Invalid old password")

        # Update the profile fields except for the password
        query_update = """
            UPDATE users
            SET first_name = %s, last_name = %s, phone = %s,
                affiliated_institute = %s
            WHERE username = %s
        """
        values_update = (
            profile.first_name,
            profile.last_name,
            profile.phone,
            profile.affiliated_institute,
            username
        )
        cursor.execute(query_update, values_update)

        # Update the password if a new password is provided
        if profile.new_password:
            pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
            hashed_password = pwd_context.hash(profile.new_password)
            query_password_update = "UPDATE users SET password = %s WHERE username = %s"
            values_password_update = (hashed_password, username)
            cursor.execute(query_password_update, values_password_update)

        db_conn.commit()
        cursor.close()
        return {"message": "Profile updated successfully"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err