from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import SessionDep
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.models.user import User

router = APIRouter()

@router.post("/login/access-token")
def login_access_token(
    db: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            data={"sub": user.username, "role": user.role, "tenant_id": user.tenant_id},
            expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
