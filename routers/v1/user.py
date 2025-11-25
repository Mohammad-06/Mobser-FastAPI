from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from models.user import User
from database import get_db
from schemas.user import UserCreate, UserResponse
from dependencies.limiter import limiter
from sqlalchemy import asc, desc
from typing import Optional
from dependencies.permissions import admin_required


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
@limiter.limit("3 per second")
def create_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(name=user.name, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[UserResponse])
@limiter.limit("3 per second")
def list_users(
    request: Request,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):

    offset = (page - 1) * limit
    users = db.query(User).offset(offset).limit(limit).all()
    return users


@router.get("/search", response_model=list[UserResponse])
@limiter.limit("3 per second")
def search_users(
    request: Request,
    name: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):
    query = db.query(User)

    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))

    if email:
        query = query.filter(User.email == email)

    return query.all()


@router.get("/sorted", response_model=list[UserResponse])
@limiter.limit("3 per second")
def sorted_users(
    request: Request,
    sort: str = "id",
    db: Session = Depends(get_db),
    current_user = Depends(admin_required)
):
    order = asc(sort) if not sort.startswith("-") else desc(sort[1:])
    return db.query(User).order_by(order).all()


@router.get("/{user_id}", response_model=UserResponse)
@limiter.limit("3 per second")
def get_user(request: Request, user_id: int, db: Session = Depends(get_db), current_user = Depends(admin_required)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return user