from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from utils.auth import hash_password, verify_password, create_access_token
from dependencies.auth import get_current_user
from pydantic import BaseModel
from dependencies.limiter import limiter
from dependencies.permissions import admin_required, user_required

router = APIRouter(prefix="/auth", tags=["Auth"])

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse)
@limiter.limit("1 per second")
def register(request: Request,user: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == user.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed, is_admin=False)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
@limiter.limit("1/second")
def login(request:Request ,user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
@limiter.limit("3 per second")
def me(request:Request ,current_user=Depends(get_current_user)):
    return current_user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(admin_required)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.put("/{user_id}", response_model=UserUpdate)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), current_user = Depends(user_required)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        existing_user = db.query(User).filter(User.email == data.email, User.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = data.email

    if data.password is not None:
        user.password = hash_password(data.password)

    db.commit()
    db.refresh(user)
    return user