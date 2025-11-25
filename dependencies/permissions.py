from fastapi import Depends, HTTPException
from dependencies.auth import get_current_user

def admin_required(current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user

def user_required(user_id: int,current_user = Depends(get_current_user)):
    if not current_user.is_user or current_user.id == user_id:
        return current_user
    raise HTTPException(status_code=403, detail="You do not have access")

