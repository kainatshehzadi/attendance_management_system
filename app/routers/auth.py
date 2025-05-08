from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app import crud
from app.schemas.user import UserCreate, UserResponse, Login
from app.security import get_current_user, verify_password, create_access_token, get_password_hash
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

# Admin signup endpoint
@router.post("/signup", response_model=UserResponse)
def signup_admin(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Validate role
        if user.role not in ['admin', 'employee']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role: must be 'admin' or 'employee'"
            )

        # Password length is already checked via Pydantic schema (constr(min_length=8))

        # Hash the password
        user.password = get_password_hash(user.password)

        # Create user
        return crud.create_user(db=db, user=user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Admin login endpoint
@router.post("/login")
def login_for_access_token(form_data: Login, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.email)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create access token for the logged-in admin
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
