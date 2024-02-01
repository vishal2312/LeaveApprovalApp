from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Form
from db.deps import get_db
from sqlalchemy.orm import Session
import api.schemas as schemas, utils.database as database, models, utils.jwttoken as jwttoken, api.service as service, utils.outh2 as oauth2
# from utils.hashing import Hash
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
import api.service as service
from fastapi_jwt_auth import AuthJWT
from models import User, LeaveRequest
from typing import List, Optional
from config import settings
from utils.hashing import encrypt
import jwt
from sqlalchemy import func


router = APIRouter()


@router.post("/api/signup")
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    user = service.create_user(name = request.name,
                               email = request.email,
                                password = request.password,
                                db = db)

    return user

@router.post("/api/verify_account")
def verify_user(token: str, db: Session = Depends(get_db)):
    try:
        token_data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = token_data.get("sub")
        if not email:
            raise jwt.PyJWTError("Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    user = db.query(User).filter(User.email == email, User.is_verified == False).first()

    if user:
        user.is_verified = True
        db.commit()
        return {"message": "User verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid verification token or user is already verified")

# Login
@router.post("/api/login")
def Login(login_data : schemas.Login,db: Session = Depends(get_db),Authorize: AuthJWT = Depends()):
    """
    This is to authenticate user
    """
    auth_user = service.authenticate_user(email=login_data.email,
                                  password=login_data.password,
                                  db=db)
    if not auth_user:
        raise  HTTPException(status_code=401,detail="credentials not found")
    access_token = Authorize.create_access_token(subject=auth_user.email)
    refresh_token = Authorize.create_refresh_token(subject=auth_user.email)
    # Authorize.set_access_cookies(access_token)
    # Authorize.set_refresh_cookies(refresh_token)
    return {
        "access_token":access_token,
        "refresh_token":refresh_token
    }


# Admin_Login
@router.post("/api/admin_login")
def Admin_Login(login_data : schemas.Admin,db: Session = Depends(get_db),Authorize: AuthJWT = Depends()):
    """
    This is to authenticate user
    """
    auth_user = service.authenticate_admin(email=login_data.email,
                                  password=login_data.password,
                                  db=db)
    if not auth_user:
        raise  HTTPException(status_code=401,detail="creadentials not found")
    access_token = Authorize.create_access_token(subject=auth_user.email)
    refresh_token = Authorize.create_refresh_token(subject=auth_user.email)
    # Authorize.set_access_cookies(access_token)
    # Authorize.set_refresh_cookies(refresh_token)
    return {
        "access_token":access_token,
        "refresh_token":refresh_token
    }



@router.post('/api/forgot_password')
def forgot_password(request: schemas.forgot, db: Session = Depends(get_db)):

    email = request.email

    reset_token = service.create_reset_token(email)

    service.send_reset_email(email, reset_token, db)

    return {"message": "Password reset email sent successfully.", "token": {reset_token}}



@router.post('/api/reset_password')
def reset_password(request : Request, reset_body: schemas.reset, token:str, db: Session = Depends(get_db)):
    try:
        token_data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = token_data.get("sub")
        if not email:
            raise jwt.PyJWTError("Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid reset token")


    if reset_body.new_password != reset_body.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.password = encrypt(reset_body.new_password)
    db.commit()

    return {"message": "Password reset successfully"}





@router.post("/api/apply_leave")
def leave_request(request: schemas.LeaveRequest, db: Session = Depends(get_db),Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    user_data = db.query(User).filter(User.email == user_email).first()
    name1 = str(user_data.name)
    email1 = str(user_data.email)
    leave = service.leave_request(name = name1,
                               email = email1,
                               leave_type=request.leave_type,
                               from_date =request.from_date,
                               to_date=request.to_date,
                               no_of_days=request.no_of_days,
                               reason=request.reason,
                               db = db)
    
    return leave

@router.put("/manage_leave/{leave_id}")
def update_leave(leave_id: int, status: str = Form(None), leave_type: str = Query(None), db: Session = Depends(get_db)):
    leave_request = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == leave_id).first()
    if leave_request:
        if status is not None:
            leave_request.status = status
        if leave_type is not None:
            leave_request.leave_type = leave_type
        db.commit()
        db.refresh(leave_request)
        return {"message": "Leave updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Leave request not found")



@router.post("/manage_leave/{leave_id}/{new_status}")
def update_leave_status_endpoint(leave_id: int, new_status: str, db: Session = Depends(get_db)):
    updated_leave_request = service.update_leave_status(leave_id, new_status, db)
    if updated_leave_request:
        service.leave_response(leave_id, new_status, db)
        return {"message": f"Leave {new_status} successfully"}
    else:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
@router.get("/api/manage_leave")
def manage_leave(request: Request, status: Optional[str] = Query("all"), name: Optional[str] = Query(None), date_range: Optional[str] = Query(None), db: Session = Depends(get_db)):
    items = service.get_filtered_leave_requests(db, status, name, date_range)
    return items

@router.get("/api/admin_dashboard")
def admin_dashboard(request: Request, email: Optional[str] = Query(None), db: Session = Depends(get_db)):
    items = service.email_filter(db, email)
    user_email = email
    total_leaves, total_planned, total_unplanned, total_leaves_taken, total_planned_taken, total_unplanned_taken, total_lwp_taken = service.leave_bifurcation(db, user_email)

    response_data = {
        "items": items,
        "total_leaves": total_leaves,
        "total_planned": total_planned,
        "total_unplanned": total_unplanned,
        "total_lwp": total_lwp_taken,
        "total_leaves_taken": total_leaves_taken,
        "total_planned_taken": total_planned_taken,
        "total_unplanned_taken": total_unplanned_taken
    }

    return response_data


@router.get("/my_leaves")
def my_leaves(Authorize,db):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    leave_history_data = db.query(LeaveRequest).filter(LeaveRequest.email == user_email).all()
    leaves_taken = db.query(func.sum(LeaveRequest.no_of_days)).filter(LeaveRequest.email == user_email, LeaveRequest.status == "Approved").scalar() or 0
    planned_leaves_taken = db.query(func.sum(LeaveRequest.no_of_days)).filter(LeaveRequest.email == user_email, LeaveRequest.status == "Approved",
                                                                              LeaveRequest.leave_type == "Planned").scalar() or 0
    unplanned_leaves_taken = db.query(func.sum(LeaveRequest.no_of_days)).filter(LeaveRequest.email == user_email, LeaveRequest.status == "Approved",
                                                                              LeaveRequest.leave_type == "Unplanned").scalar() or 0
    leaves_remaining = 24 - leaves_taken
    planned_leaves_rem = 15 - planned_leaves_taken
    unplanned_leaves_rem = 9 - unplanned_leaves_taken
    return leave_history_data, leaves_taken, planned_leaves_taken, unplanned_leaves_taken, leaves_remaining, planned_leaves_rem, unplanned_leaves_rem




@router.get("/my_leaves")
def my_profile_data(Authorize,db):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    user_data = db.query(User).filter(User.email == user_email).first()
    return user_data


@router.get("/api/user_dashboard")
def user_dashboard(request: Request, year: str = Query(default=None), db: Session = Depends(get_db)):
    if not year:
        year = datetime.now().year

    user_email = "manav@gmail.com"  # Replace with actual logic to get user email

    total_leaves, total_planned, total_unplanned, total_leaves_taken, total_planned_taken, total_unplanned_taken, total_lwp_taken = service.leave_bifurcation(db, user_email)
    leaves_by_month, planned_leaves_by_month, unplanned_leaves_by_month, lwp_by_month = service.monthly_leaves(db, user_email, year)

    return {
        # "total_leaves": total_leaves,
        # "total_planned": total_planned,
        # "total_unplanned": total_unplanned,
        # "total_leaves_taken": total_leaves_taken,
        # "total_planned_taken": total_planned_taken,
        # "total_unplanned_taken": total_unplanned_taken,
        "leaves_by_month": leaves_by_month,
        "planned_leaves_by_month": planned_leaves_by_month,
        "unplanned_leaves_by_month": unplanned_leaves_by_month,
        "lwp_by_month": lwp_by_month,
        "year": year
    }