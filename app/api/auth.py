import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.db import database
from app.core import security
from app.config import settings
import jwt
from jwt.exceptions import InvalidTokenError

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = await database.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    # Check if user exists
    existing_user = await database.get_user_by_email(form_data.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = security.get_password_hash(form_data.password)
    user_data = {
        "id": user_id,
        "email": form_data.username,
        "hashed_password": hashed_password
    }
    
    await database.create_user(user_data)
    
    # Generate token
    access_token = security.create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user_id}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await database.get_user_by_email(form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}
