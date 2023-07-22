from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from typing import Optional, List
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import mysql.connector
import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import asyncio

# Replace the placeholders with your MySQL connection details
db_config = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'mtil_evaluation_platform'
}
db_conn = mysql.connector.connect(**db_config)

# Define the secret key used for JWT
SECRET_KEY = 'your-secret-key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Define a function to generate access and refresh tokens
def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class User(BaseModel):
    username: str
    password: str

class SignupUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    phone: Optional[str] = None
    affiliated_institute: Optional[str] = None
    email: EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str

class UpdateProfile(BaseModel):
    first_name: str
    last_name: str
    password: str
    phone: Optional[str] = None
    affiliated_institute: Optional[str] = None
    username: str

class Team(BaseModel):
    team_name: str
    emails: List[EmailStr]
    leader_id: int


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        return user
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user['password']):
        return False
    return user

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
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err

def is_token_revoked(token: str) -> bool:
    try:
        cursor = db_conn.cursor()
        query = "SELECT COUNT(*) FROM _revoked_tokens WHERE token = %s"
        cursor.execute(query, (token,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err

async def send_invitation_email(email: str, link: str, User: str, sender_name: str, team_name: str):
    # Configure your email settings
    email_config = ConnectionConfig(
        MAIL_USERNAME="cspgosoff@gmail.com",
        MAIL_PASSWORD="GANESh@123",
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_TLS=True,
        MAIL_SSL=False
        )

    # Compose the email message
    with open('email_template.html', 'r') as file:
        html_string = file.read()
    template = html_string.format(link, User, sender_name, team_name)

    message = MessageSchema(
       subject="Invitation to Join Team",
       recipients=email.dict().get("email"),  # List of recipients, as many as you can pass  
       body=template,
       subtype="html"
       )
    try:
        fm = FastMail(email_config)
        await fm.send_message(message)
    except smtplib.SMTPException as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to send email") from e


app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.post("/signup")
def signup(user: SignupUser):
    try:
        existing_user = get_user(user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        cursor = db_conn.cursor()
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
        return {"message": "User created successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err


@app.post("/signin")
def signin(user: User):
    try:
        authenticated_user = authenticate_user(user.username, user.password)
        if not authenticated_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token(authenticated_user['username'])
        refresh_token = create_token({'sub': authenticated_user['username']}, timedelta(days=30))
        return Token(access_token=access_token, refresh_token=refresh_token)
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err

@app.get("/profile")
def view_profile(token: str = Depends(oauth2_scheme)):
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
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err


@app.put("/profile")
def update_profile(profile: UpdateProfile, token: str = Depends(oauth2_scheme)):
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

        # Check if the provided password matches the current password
        if not verify_password(profile.password, current_password):
            raise HTTPException(status_code=401, detail="Invalid password")

        # Update the profile fields
        query_update = """
            UPDATE users
            SET first_name = %s, last_name = %s, password = %s, phone = %s,
                affiliated_institute = %s, username = %s
            WHERE username = %s
        """
        values_update = (
            profile.first_name,
            profile.last_name,
            pwd_context.hash(profile.new_password),
            profile.phone,
            profile.affiliated_institute,
            profile.username,
            username
        )
        cursor.execute(query_update, values_update)
        db_conn.commit()
        cursor.close()

        return {"message": "Profile updated successfully"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err

        
@app.put("/profile")
def update_profile(profile: UpdateProfile, token: str = Depends(oauth2_scheme)):
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
                affiliated_institute = %s, username = %s
            WHERE username = %s
        """
        values_update = (
            profile.first_name,
            profile.last_name,
            profile.phone,
            profile.affiliated_institute,
            profile.username,
            username
        )
        cursor.execute(query_update, values_update)

        # Update the password if a new password is provided
        if profile.new_password:
            hashed_password = pwd_context.hash(profile.new_password)
            query_password_update = "UPDATE users SET password = %s WHERE username = %s"
            values_password_update = (hashed_password, username)
            cursor.execute(query_password_update, values_password_update)

        db_conn.commit()
        cursor.close()
        return {"message": "Profile updated successfully"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error") from err
    

@app.post("/create_team")
async def create_team(team: Team,token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        # Generate a unique team ID
        team_id = str(uuid.uuid4())

        # Insert the team into the 'teams' table
        cursor = db_conn.cursor()
        insert_team_query = "INSERT INTO teams (team_id, team_name, leader_id) VALUES (%s, %s, %s)"
        cursor.execute(insert_team_query, (team_id, team.team_name, team.leader_id))
        db_conn.commit()

        # Insert team members into the 'team_members' table
        insert_members_query = "INSERT INTO team_members (team_id, user_id) VALUES (%s, %s)"
        for email in team.emails:
            # Retrieve the user_id based on the email
            get_user_id_query = "SELECT id FROM users WHERE email = %s"
            cursor.execute(get_user_id_query, (email,))
            result = cursor.fetchone()
            if result is not None:
                user_id = result[0]
                cursor.execute(insert_members_query, (team_id, user_id))
        db_conn.commit()

        cursor.close()

        # Send invitation emails to the team members
        # email: str, link: str, User: str, sender_name: str, team_name: str
        link="http://example.com/"
        User="user"
        for email in team.emails:
            await send_invitation_email(email,link,User,username,team_id)
        
        return {"message": "Team created successfully", "team_id": team_id}
    except mysql.connector.Error as err:
        print(err)
        raise HTTPException(status_code=500, detail="Database error") from err