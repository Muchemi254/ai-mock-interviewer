# backend/services/api-gateway/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
# Import models
from common import models # Pydantic models
from common.config import settings
# Import database functions
from common.database import get_db_session, get_user_by_username # Import DB functions
from common.database_models import User as DBUser # SQLAlchemy model for type hints if needed
# Import auth functions
from common.auth import authenticate_user, create_access_token, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


from common.models import User, UserCreate
from common.database import create_user, get_user_by_username
from common.auth import get_password_hash

@router.post("/users", response_model=User)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)):
    # Check if username already exists
    existing_user = await get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash password
    hashed_pw = get_password_hash(user_in.password)

    # Create user
    new_user = await create_user(db, user_in.username, user_in.email, hashed_pw)

    # Map SQLAlchemy → Pydantic
    return User(
        id=str(new_user.id),
        username=new_user.username,
        email=new_user.email,
        hashed_password=new_user.hashed_password,  # ⚠ don’t expose in prod!
        is_active=new_user.is_active,
        is_superuser=new_user.is_superuser,
    )


@router.post("/token", response_model=models.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)):
    db_user = await get_user_by_username(db, form_data.username)
    if not db_user or not auth.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# @router.get("/users/me", response_model=models.User)
# async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
#     return current_user

# --- Updated endpoint to fetch user from DB ---
@router.get("/users/me/db", response_model=models.User) # New endpoint name to distinguish
async def read_users_me_from_db(current_user: models.TokenData = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)):
    """
    Fetches the current user's details from the database.
    """
    # current_user is the TokenData (contains username from JWT)
    if not current_user.username:
        raise HTTPException(status_code=400, detail="Invalid token data")

    # Fetch user from database using the username from the token
    db_user = await get_user_by_username(db, current_user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found in database")

    # Convert SQLAlchemy model instance to Pydantic model for response
    # This mapping assumes the fields match. For complex fields, manual mapping might be needed.
    try:
        user_pydantic = models.User(
            id=str(db_user.id), # Convert UUID to string
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password, # Usually not returned! Just for example.
            is_active=db_user.is_active,
            is_superuser=db_user.is_superuser
            # created_at, updated_at are in Pydantic model but not necessarily needed in response
        )
        return user_pydantic
    except Exception as e:
        logger.error(f"Error converting DB user to Pydantic model: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Optional: Endpoint to create a test user in the DB
from fastapi import BackgroundTasks
from common.auth import get_password_hash

@router.post("/users/test-db-user")
async def create_test_db_user(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db_session)):
    """
    Creates a test user directly in the database.
    WARNING: This is for testing Phase 0 setup only. Remove or secure in production.
    """
    test_username = "db_testuser"
    test_email = "db_test@example.com"
    test_password = "db_testpass"
    hashed_pw = get_password_hash(test_password)

    # Check if user already exists
    existing_user = await get_user_by_username(db, test_username)
    if existing_user:
         return {"message": f"Test user '{test_username}' already exists."}

    try:
        new_user = await create_user(db, test_username, test_email, hashed_pw)
        return {"message": f"Test user '{test_username}' created successfully.", "user_id": str(new_user.id)}
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Failed to create test user: {e}")
