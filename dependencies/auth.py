from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from utils.auth import SECRET_KEY, ALGORITHM
from sqlalchemy.orm import Session
from database import get_db
from models.user import User

bearer_scheme = HTTPBearer()

def get_current_user(token: str = Depends(bearer_scheme), db: Session = Depends(get_db)):
    token = token.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
