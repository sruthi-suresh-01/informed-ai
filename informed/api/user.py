import json
import secrets
import traceback
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import ColumnElement, delete, select
from sqlalchemy.exc import IntegrityError

from informed.helper.utils import get_current_user
from informed.api.api_types import (
    CreateUserRequest,
    LoginRequest,
    UserDetailsRequest,
    UserDetailsResponse,
    UserMedicalDetailsRequest,
    UserMedicalDetailsResponse,
)
from informed.db import session_maker
from informed.db_models.users import (
    User,
    UserDetails,
    UserHealthConditions,
    UserLanguage,
    UserMedicalDetails,
    UserMedications,
    WeatherSensitivities,
)

user_router = APIRouter()


def set_session_cookie(
    request: Request, response: Response, session_object: dict
) -> None:
    redis_client = request.app.state.redis_client
    session_token = secrets.token_urlsafe()
    serialized_session = json.dumps(session_object)
    redis_client.set(session_token, serialized_session, ex=3600)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )


@user_router.post(
    "/register", response_model=CreateUserRequest, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user: CreateUserRequest, request: Request, response: Response
) -> CreateUserRequest:
    try:
        async with session_maker() as session:
            # Check if user with the same username or email already exists
            existing_user = await session.execute(
                select(User).filter(
                    cast(
                        ColumnElement[bool],
                        (User.username == user.username) | (User.email == user.email),
                    )
                )
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=400, detail="Username or email already exists"
                )

            new_user = User(
                username=user.username,
                email=user.email,
                is_active=True,
                account_type="user",
            )
            session.add(new_user)
            try:
                await session.commit()
                session_object = {"username": user.username, "role": "admin"}
                set_session_cookie(request, response, session_object)
                return CreateUserRequest(
                    username=new_user.username, email=new_user.email
                )
            except IntegrityError as ie:
                await session.rollback()
                if "users_email_key" in str(ie):
                    raise HTTPException(status_code=400, detail="Email already exists")
                elif "users_username_key" in str(ie):
                    raise HTTPException(
                        status_code=400, detail="Username already exists"
                    )
                else:
                    print(f"Unexpected IntegrityError: {ie!s}")
                    raise HTTPException(
                        status_code=500, detail="An unexpected database error occurred"
                    )
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        print(f"Unexpected error in register_user: {e!s}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while registering the user",
        )


@user_router.post("/details")
async def set_user_details(
    details: UserDetailsRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    async with session_maker() as session:
        # Check if the user exists
        user = current_user
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Handle the user details
        if not user.details:
            user.details = UserDetails(
                user_id=user.id,
                first_name=details.first_name,
                last_name=details.last_name,
            )

        # Update user details
        user.details.first_name = details.first_name
        user.details.last_name = details.last_name
        user.details.age = details.age
        user.details.address_line1 = details.address_line1
        user.details.address_line2 = details.address_line2
        user.details.city = details.city
        user.details.state = details.state
        user.details.zip_code = details.zip_code
        user.details.country = details.country
        user.details.phone_number = details.phone_number
        user.details.ethnicity = details.ethnicity
        session.add(user.details)

        # Clear existing languages
        stmt = delete(UserLanguage).where(
            cast(ColumnElement[bool], UserLanguage.user_details_id == user.details.id)
        )
        await session.execute(stmt)

        # Add new languages
        for lang in details.languages:
            user_lang = UserLanguage(
                user_details_id=user.details.id, **lang.model_dump()
            )
            session.add(user_lang)

        try:
            await session.commit()
            await session.flush()
        except IntegrityError as e:
            await session.rollback()
            print(f"IntegrityError: {e!s}")
            raise HTTPException(
                status_code=500, detail="An error occurred while updating user details"
            )

    return {"message": "User details updated successfully"}


@user_router.get("/details")
async def get_user_details(
    current_user: User = Depends(get_current_user),
) -> UserDetailsResponse:

    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.details:
        raise HTTPException(status_code=404, detail="User details not found")

    # Construct the response
    return UserDetailsResponse.from_user_details(user.details)


@user_router.get("/medical-details", response_model=UserMedicalDetailsResponse)
async def get_medical_details(
    current_user: User = Depends(get_current_user),
) -> UserMedicalDetailsResponse:

    user = current_user
    if not user.medical_details:
        raise HTTPException(status_code=404, detail="Medical details not found")

    return UserMedicalDetailsResponse.from_user_medical_details(user.medical_details)


@user_router.post("/medical-details")
async def set_medical_details(
    details: UserMedicalDetailsRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    user = current_user
    try:
        async with session_maker() as session:
            # Update or create medical details
            if user.medical_details:
                medical_details = user.medical_details
            else:
                medical_details = UserMedicalDetails(user_id=user.id)
                # db.add(medical_details)

            medical_details.blood_type = details.blood_type
            medical_details.height = details.height
            medical_details.weight = details.weight

            # Handle health conditions
            medical_details.health_conditions = []
            for condition in details.health_conditions:
                health_condition = UserHealthConditions(
                    user_medical_id=medical_details.id,
                    condition=condition.condition,
                    severity=condition.severity,
                    description=condition.description,
                )
                medical_details.health_conditions.append(health_condition)

            # Handle medications
            medical_details.medications = []
            for med in details.medications:
                medication = UserMedications(
                    user_medical_id=medical_details.id,
                    name=med.name,
                    dosage=med.dosage,
                    frequency=med.frequency,
                )
                medical_details.medications.append(medication)

            # Handle weather sensitivities
            medical_details.weather_sensitivities = []
            for sensitivity in details.weather_sensitivities:
                weather_sensitivity = WeatherSensitivities(
                    user_medical_id=medical_details.id,
                    type=sensitivity.type,
                    description=sensitivity.description,
                )
                medical_details.weather_sensitivities.append(weather_sensitivity)

            user.medical_details = medical_details
            session.add(user)
            await session.commit()
            return {"message": "Medical details updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e!s}"
        )


@user_router.post("/login")
async def login(
    request: Request, login_request: LoginRequest, response: Response
) -> dict:

    try:
        async with session_maker() as session:
            result = await session.execute(
                select(User).filter(
                    cast(ColumnElement[bool], User.username == login_request.username)
                )
            )
            db_user = result.unique().scalar_one_or_none()
            if db_user:
                session_object = {"username": login_request.username, "role": "admin"}
                set_session_cookie(request, response, session_object)
                return {"data": db_user, "message": "Login Successful"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username"
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e!s}")


@user_router.get("/me")
async def read_users_me(
    request: Request, current_user: User = Depends(get_current_user)
) -> dict:
    try:
        return {
            "data": current_user,
            "sessionAlive": True,
            "message": "Login Successful",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e!s}")


@user_router.get("/logout")
async def logout(request: Request, response: Response) -> dict:
    session_token = request.cookies.get("session_token")
    redis_client = request.app.state.redis_client
    if session_token:
        redis_client.delete(session_token)
        # response.delete_cookie("session_token")
        return {"message": "Logged out"}
    raise HTTPException(status_code=400, detail="No active session found")
