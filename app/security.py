from passlib.context import CryptContext
from datetime import datetime, timedelta,timezone
from jose import JWTError, jwt
from app.models.user import User
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.db.database import get_db
from dotenv import load_dotenv
import os

load_dotenv()  # Loads environment variables from a .env file
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer instance to use for token extraction from headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT Token settings
SECRET_KEY = "this is a special key" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # You can set this to your desired expiry time


# Function to verify the plain password against the hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to hash the password before storing it in the database
def get_password_hash(password):
    return pwd_context.hash(password)

# Function to create a JWT token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to decode the JWT token and retrieve the current user from the database
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # 'sub' is where the email was stored in the token
        if email is None:
            raise credentials_exception
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
