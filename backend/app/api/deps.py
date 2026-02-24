from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

def get_current_user(db: SessionDep, token: TokenDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_active_superuser(current_user: CurrentUser) -> User:
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user

def get_current_active_admin(current_user: CurrentUser) -> User:
    if current_user.role not in ["superadmin", "companyadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user
