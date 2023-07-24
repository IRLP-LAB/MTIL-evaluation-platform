from fastapi import HTTPException
import mysql.connector as connector
from datetime import timedelta
import os
from dotenv import load_dotenv

from database import db_conn
from app.utils.auth import get_user
from app.utils.auth import pwd_context, authenticate_user
from app.utils.token import create_access_token, create_token
from app.models.util import Token
from app.utils.mailer import account_mail_verifier
from app.utils.auth import is_account_verified

load_dotenv()
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

        #Varification mail
        subject = "Account verification || MTIL"
        with open('./app/static/varification_mail.html', "r") as file:
                html_template = file.read()
        

        User_placeholder = {
        "name": user.first_name, 
        "link": os.getenv("VARIFICATION_URL") + user.email, 
        "sender_name": "MTIL"
        }

        print(User_placeholder["link"])
        account_mail_verifier(subject, html_template, user.email, User_placeholder)
        return {"message": "User created successfully"}
    except connector.Error as err:
        print(err)
        raise HTTPException(status_code=500, detail="Database error") from err
    
def signin(user):
    try:
        if not is_account_verified(user.username):
            return {
                    "status": "error",
                    "message": "Account not verified",
                    "status_code": 403
                }
        
        authenticated_user = authenticate_user(user.username, user.password)
        if not authenticated_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token(authenticated_user['username'])
        refresh_token = create_token({'sub': authenticated_user['username']}, timedelta(days=30))
        return {
                "status": "success",
                "data": Token(access_token=access_token, refresh_token=refresh_token),
                "message": "User authenticated successfully",
                "status_code": 200
        }
    except connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err
    

def mailaccountverify(email:str):
    try:
        cursor = db_conn.cursor(dictionary=True)
        query_email = "UPDATE users SET mail_verified = 1 WHERE users.email = %s"
        cursor.execute(query_email, (email,))
        # result = cursor.fetchone()
        db_conn.commit()
        return {
                "status": "success",
                "message": "Mail Verified successfully",
                "status_code": 200
        }
    except connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err
