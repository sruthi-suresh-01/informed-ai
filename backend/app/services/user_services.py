from fastapi import APIRouter, Depends, status, HTTPException, Request, Response, Cookie
from sqlalchemy.orm import Session, selectinload, joinedload, subqueryload
import json
from app.dependencies import db_dependency, redis_client, get_db
from app.core.models.users import User, UserDetails, UserLanguage, Language, UserAllergies, UserHealthConditions, UserMedicalDetails, UserMedications


def get_current_user(session_token: str = Cookie(None), db: Session = Depends(get_db)):
    if session_token is None:
        return None
    
    serialized_session = redis_client.get(session_token)
    session_object = json.loads(serialized_session)
    if not session_object or not session_object["username"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session or expired session")
    
    user = db.query(User).options(
        # Load UserDetails
        joinedload(User.details).options(
            # Load languages through UserLanguage and join Language details
            joinedload(UserDetails.languages).joinedload(UserLanguage.language),
        ),
        # Load UserMedicalDetails and nested HealthConditions
        joinedload(User.medical_details).options(
            joinedload(UserMedicalDetails.health_conditions)
        )
    ).filter(User.username == session_object["username"]).one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


user_router = APIRouter()