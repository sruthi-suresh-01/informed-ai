
from fastapi import APIRouter, Depends, status, HTTPException, Request, Response, Cookie
import json
import secrets
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.core.models.users import User, UserDetails, UserLanguage, Language, UserAllergies, UserHealthConditions, UserMedicalDetails, UserMedications
from app.core.schemas.user_request import CreateUserRequest, LoginRequest, UserDetailsRequest, UserDetailsResponse, LanguageResponse, MedicalDetails, UserMedicalDetailsRequest
from app.dependencies import db_dependency, get_db, redis_client
from app.services.user_services import get_current_user


user_router = APIRouter()


@user_router.post("/register", response_model=CreateUserRequest, status_code=status.HTTP_201_CREATED)
async def register_user(user: CreateUserRequest, request: Request, db: db_dependency):
    # Check if the username or email already exists
    existing_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Create new user if it doesn't exist
    new_user = User(username=user.username, email=user.email, is_active=True, account_type="user")
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)  # Refresh to retrieve the new user data with ID
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create user due to a database error")

    return CreateUserRequest(username=new_user.username, email=new_user.email)


@user_router.post("/set-user-details/{username}")
async def set_user_details(username: str, details: UserDetailsRequest, db: db_dependency, current_user: User = Depends(get_current_user)):

    if current_user.username != username and current_user.account_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's details")
    # Check if the user exists
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Handle the language details
    user_detail = user.details
    if not user_detail:
        user_detail = UserDetails(user_id=user.id)
        db.add(user_detail)
    
    user_detail.first_name = details.first_name
    user_detail.last_name = details.last_name
    user_detail.age = details.age
    user_detail.address_line1 = details.address_line1
    user_detail.address_line2 = details.address_line2
    user_detail.city = details.city
    user_detail.state = details.state
    user_detail.zip_code = details.zip_code
    user_detail.country = details.country
    user_detail.phone_number = details.phone_number
    user_detail.ethnicity = details.ethnicity

    # Update languages
    for lang in details.languages:
        language = db.query(Language).filter(Language.name == lang.name).first()
        if not language:
            language = Language(name=lang.name)
            db.add(language)
        db.flush()  # Ensure language has an ID
        user_lang = db.query(UserLanguage).filter_by(user_details_id=user_detail.id, language_id=language.id).first()
        if not user_lang:
            user_lang = UserLanguage(user_details_id=user_detail.id, language_id=language.id)
            db.add(user_lang)
        user_lang.is_preferred = lang.is_preferred

    db.commit()
    return {"message": "User details updated successfully"}

@user_router.get("/get-user-details/{username}", response_model=UserDetailsResponse)
async def get_user_details(username: str, db: db_dependency, current_user: User = Depends(get_current_user)):

    if current_user.username != username and current_user.account_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's details")

    # Fetch user by username including details and languages
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.details:
        raise HTTPException(status_code=404, detail="User details not found")

    # Build language details including preferences
    languages = []
    for ul in db.query(UserLanguage).filter(UserLanguage.user_details_id == user.details.id).all():
        language = db.query(Language).filter(Language.id == ul.language_id).first()
        if language:
            languages.append(LanguageResponse(name=language.name, is_preferred=ul.is_preferred))

    # Construct the response
    return UserDetailsResponse(
        first_name=user.details.first_name,
        last_name=user.details.last_name,
        age= user.details.age,
        address_line1=user.details.address_line1,
        address_line2=user.details.address_line2,
        city=user.details.city,
        state=user.details.state,
        zip_code=user.details.zip_code,
        country=user.details.country,
        phone_number=user.details.phone_number,
        ethnicity=user.details.ethnicity,
        languages=languages
    )



@user_router.get("/{username}/medical-details", response_model=MedicalDetails)
async def get_medical_details(username: str, db: db_dependency, current_user: User = Depends(get_current_user)):

    if current_user.username != username and current_user.account_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's details")
    
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_medical_details = db.query(UserMedicalDetails).options(
        joinedload(UserMedicalDetails.health_conditions),
        joinedload(UserMedicalDetails.medications)
    ).filter(UserMedicalDetails.user_id == user.id).first()
    if not user_medical_details:
        raise HTTPException(status_code=404, detail="Medical details not found")
    return user_medical_details


@user_router.post("/{username}/medical-details")
async def set_medical_details(username: str, details: UserMedicalDetailsRequest, db: db_dependency, current_user: User = Depends(get_current_user)):
    if current_user.username != username and current_user.account_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's details")
    
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update or create medical details
    if user.medical_details:
        medical_details = user.medical_details
    else:
        medical_details = UserMedicalDetails(user_id=user.id)
        db.add(medical_details)

    medical_details.blood_type = details.blood_type
    medical_details.height = details.height
    medical_details.weight = details.weight
    print("medical_details id ", medical_details.id)
    # Handle health conditions
    for condition in details.health_conditions:
        if condition.id:
            hc = db.query(UserHealthConditions).filter(
                UserHealthConditions.id == condition.id,
                UserHealthConditions.user_medical_id == medical_details.id
            ).first()
            if hc:
                hc.condition = condition.condition
                hc.severity = condition.severity
                hc.description = condition.description
        else:
            hc = UserHealthConditions(
                user_medical_id=medical_details.id,
                condition=condition.condition,
                severity=condition.severity,
                description=condition.description
            )
            db.add(hc)

    # Handle medications
    for med in details.medications:
        if med.id:
            medication = db.query(UserMedications).filter(
                UserMedications.id == med.id,
                UserMedications.user_medical_id == medical_details.id
            ).first()
            if medication:
                medication.name = med.name
                medication.dosage = med.dosage
                medication.frequency = med.frequency
        else:
            medication = UserMedications(
                user_medical_id=medical_details.id,
                name=med.name,
                dosage=med.dosage,
                frequency=med.frequency
            )
            db.add(medication)

    db.commit()
    return {"message": "Medical details updated successfully"}



@user_router.post("/login")
async def login(login_request: LoginRequest, response: Response, db: db_dependency):
    db_user = db.query(User).filter(User.username == login_request.username).first()
    if db_user:
        session_token = secrets.token_urlsafe()
        session_object = {
            "username": login_request.username,
            "role" : "admin"
        }
        serialized_session = json.dumps(session_object)
        redis_client.set(session_token, serialized_session, ex=3600)  # Store session with 1-hour expiration
        response.set_cookie(key="session_token", value=session_token, httponly=True, secure=True, samesite='Lax')
        return {"message": "Login Successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username"
        )
    
@user_router.get("/me")
async def read_users_me(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token:
        # username = redis_client.get(session_token)
        serialized_session = redis_client.get(session_token)
        session_object = json.loads(serialized_session)
        if not session_object or not session_object["username"]:
            raise HTTPException(status_code=400, detail="Invalid session or not logged in")
        return {"username": session_object["username"]}
    raise HTTPException(status_code=400, detail="No active session found")

@user_router.get("/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        redis_client.delete(session_token)
        response.delete_cookie("session_token")
        return {"message": "Logged out"}
    raise HTTPException(status_code=400, detail="No active session found")