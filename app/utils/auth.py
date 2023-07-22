from passlib.context import CryptContext
from database import db_conn
from fastapi import HTTPException
import mysql.connector as connector

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    try:
        print(db_conn)
        cursor = db_conn.cursor(dictionary=True)
        print(cursor)
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        return user
    except connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err
    
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user['password']):
        return False
    return user

def send_invitation_email(email: str, link: str, User: str, sender_name: str, team_name: str):
    return "Send invitation email to: " + email



