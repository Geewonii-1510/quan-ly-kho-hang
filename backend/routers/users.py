"""
Users router - API quản lý người dùng
CRUD operations for users (admin only) / Quản lý người dùng (chỉ admin)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from database import get_db
from models.user import User, Role
from schemas.user import UserResponse, UserCreate, UserUpdate, RoleResponse
from services.auth_service import get_current_user, require_role, hash_password

router = APIRouter(prefix="/api/users", tags=["Users / Người dùng"])


@router.get("/", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users / Lấy danh sách người dùng"""
    users = db.query(User).options(joinedload(User.role)).all()
    return users


@router.get("/roles", response_model=List[RoleResponse])
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all roles / Lấy danh sách vai trò"""
    return db.query(Role).all()


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info / Lấy thông tin người dùng hiện tại"""
    return current_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update user (admin only) / Cập nhật người dùng (chỉ admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng / User not found"
        )

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Deactivate user (admin only) / Vô hiệu hóa người dùng (chỉ admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng / User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể vô hiệu hóa chính mình / Cannot deactivate yourself"
        )

    user.is_active = False
    db.commit()
    return {"message": "Đã vô hiệu hóa người dùng / User deactivated"}
