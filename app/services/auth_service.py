from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token, 
    create_refresh_token,
    get_password_hash,
    verify_password,
)

from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def register(self, data: RegisterRequest) -> TokenResponse:
        existing = self.db.query(User).filter(User.email == data.email).first()

        if existing:
            raise HTTPException(
                status_code = 409, detail= "Bu email allaqachon mavjud"
            )
        user = User(
            name=data.name, 
            email=data.email, 
            password=get_password_hash(data.password), 
            role="user",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )
    
    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.db.query(User).filter(User.email == data.email).first()
        
        if not user or not verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login yoki parol noto'g'ri",
            )

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )