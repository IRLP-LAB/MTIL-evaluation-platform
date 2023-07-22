from fastapi import HTTPException
from jose import jwt
import mysql.connector as connector
import uuid
import os

from database import db_conn
from app.utils.auth import send_invitation_email

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

async def create_team(team, token: str):
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
    except connector.Error as err:
        print(err)
        raise HTTPException(status_code=500, detail="Database error") from err