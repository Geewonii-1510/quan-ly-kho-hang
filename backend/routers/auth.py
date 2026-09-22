"""
Auth router - API xác thực
Login, register endpoints / Đăng nhập, đăng ký
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, Role
from schemas.user import UserLogin, UserCreate, UserResponse, Token
from services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication / Xác thực"])


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and get JWT token / Đăng nhập và lấy JWT token
    """
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu / Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa / Account is disabled"
        )

    token = create_access_token(data={"sub": str(user.id)})

    return Token(
        access_token=token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role_id=user.role_id,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    )


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register new user / Đăng ký người dùng mới
    """
    # Check existing username / Kiểm tra username đã tồn tại
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập đã tồn tại / Username already exists"
        )

    # Check existing email / Kiểm tra email đã tồn tại
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã tồn tại / Email already exists"
        )

    # Check role exists / Kiểm tra role tồn tại
    role = db.query(Role).filter(Role.id == user_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vai trò không tồn tại / Role does not exist"
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        role_id=user_data.role_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
