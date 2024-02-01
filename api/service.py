from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
import models, api.schemas as schemas
from api.schemas import Login
from utils.hashing import encrypt, verify 
from models import User, LeaveRequest, Admin
from config import settings
import yagmail
from db.deps import get_db
from fastapi_jwt_auth import AuthJWT
import datetime, jwt
from config import settings
from typing import Optional
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse


def authenticate_user(email:str,password:str,db:Session):

    user = db.query(User).filter(User.email == email).first()
    if not user:
        print('Username is incorrect')
        raise HTTPException(status_code=403 , detail="Account is not verified")
    
    user = db.query(User).filter(User.email == email, User.is_verified == True).first()
    if user is None:
        print('Account is not verified')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Account is not verified")
    
    if not verify(user.password,password):
        print('Password is incorrect')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password is incorrect")
    return user


def authenticate_admin(email:str,password:str,db:Session):

    user = db.query(Admin).filter(Admin.email == email).first()
    if not user:
        return None
    if not (user.password == password):
        return None
    return user


def create_user(name: str,
                 email:str,
                 password:str,
                 db:Session):
    email_exists = db.query(User).filter(User.email == email).first()
    if email_exists:
        raise HTTPException(status_code=403, detail=settings.MSG_EMAIL_EXISTS)

    new_user = User(name=name,
                    email=email,
                    password=encrypt(password))
    
    reset_token = create_reset_token(email)
    
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    subject = "Account Verification"
    reset_link = f"http://localhost:8000/verify_account?token={reset_token}"
    body = f"Hi,<br><br>Please click on the below link to verify your account:<br><br><a href='{reset_link}'>Verify Account</a><br><br>"
    send_email(email, subject, body)

    return new_user



def send_reset_email(email: str, reset_token: str, db:Session):
    user_data = db.query(User).filter(User.email == email).first()

    if not user_data:
        raise HTTPException(status_code=403, detail=settings.MSG_CHECK_EMAIL)
    
    subject = "Reset Password"
    reset_link = f"http://localhost:8000/reset_password?token={reset_token}"
    body = f"Hi,<br><br>Please click on the link below to reset your password:<br><br><a href='{reset_link}'>Reset Password</a><br><br>"
    send_email(email, subject, body)
    return email


def create_reset_token(email: str) -> str:
    expiration_time = datetime.utcnow() + settings.TOKEN_EXPIRATION
    token_data = {"sub": email, "exp": expiration_time}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token.decode("utf-8")



def leave_request(name: str,
                 email:str,
                 leave_type: str,
                 from_date: str,
                 to_date: str,
                 no_of_days: str,
                 reason:str,

                 db:Session):
    
    existing_leave = db.query(LeaveRequest).filter(LeaveRequest.email == email, LeaveRequest.from_date == from_date).first()
    if existing_leave:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Leave already applied for this date.")
    
    user_email = email
    total_leaves, total_planned, total_unplanned, total_leaves_taken, total_planned_taken, total_unplanned_taken, total_lwp_taken = leave_bifurcation(db, user_email)

    rem_planned_leaves = total_planned - total_planned_taken
    rem_unplanned_leaves = total_unplanned - total_unplanned_taken

    if leave_type == 'Planned' and (rem_planned_leaves <= no_of_days):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Alert: You have {rem_planned_leaves} remaining planned leaves.")
    
    if leave_type == 'Unplanned' and (rem_unplanned_leaves <= no_of_days):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Alert: You have {rem_unplanned_leaves} remaining unplanned leaves.")

    request = LeaveRequest(
        name=name,
        email=email,
        leave_type=leave_type,
        from_date=from_date,
        to_date=to_date,
        no_of_days=no_of_days,
        reason=reason
    )
    subject = f"Leave Request: {name}"
    body = f"Dear Team, \n\n{name} has requested leave from {from_date} to {to_date} ({no_of_days} days).\n\nBest Regards,\n{name}"
    send_email(USERNAME, subject, body)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request
    

USERNAME = 'vishaladdnectar@gmail.com'
PASSWORD = 'uwbo xlli ijmt bkwc'



yag = yagmail.SMTP(USERNAME, PASSWORD)

def send_email(receiver_email: str, subject: str, body: str):
    yag.send(receiver_email, subject, body)


def update_leave_status(leave_id: int, new_status: str, db: Session):
    leave_request = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if leave_request:
        leave_request.status = new_status
        db.commit()
        return leave_request
    return None

def leave_response(leave_id, new_status, db):
    email_id =  db.query(LeaveRequest.email).filter(LeaveRequest.id == leave_id).scalar()

    if new_status == 'Approved':
        send_email(email_id, "Leave Approval", "Your leave request has been approved.")
        return {"message": "Leave approved successfully"}
    
    elif new_status == 'Rejected':
        send_email(email_id,"Leave Rejection","Your leave request has been rejected")
        return {"message":"Leave request rejected"}
    
    else:
        raise HTTPException(status_code=404, detail="Leave request not found")
    



def user_leave(user_email, db:Session):
    pass



def get_filtered_leave_requests(db: Session, status: str, name: Optional[str], date_range: Optional[str]):
    query = db.query(LeaveRequest)

    if status == "all":
        query = query.order_by(desc(LeaveRequest.id))

    if status != "all":
        query = query.filter(LeaveRequest.status == status)

    if name:
        query = query.filter(func.lower(LeaveRequest.name).ilike(f"%{name.lower()}%"))

    if date_range:
        from_date_str, to_date_str = date_range.split(' to ')
        from_date = datetime.strptime(from_date_str, '%m/%d/%Y')
        to_date = datetime.strptime(to_date_str, '%m/%d/%Y')

        query = query.filter(LeaveRequest.from_date <= to_date_str, LeaveRequest.to_date >= from_date_str)

    return query.all()

def email_filter(db: Session, email: Optional[str]):
    query = db.query(LeaveRequest).filter(LeaveRequest.status != "Pending")

    if email:
        query = query.filter(LeaveRequest.email == email)

    return query.all()


    

def leave_bifurcation(db, user_email):
    total_leaves = 24
    total_planned = 15
    total_unplanned = 9
    

    total_leaves_taken = db.query(func.sum(LeaveRequest.no_of_days)).filter(LeaveRequest.email == user_email, LeaveRequest.status == "Approved").scalar() or 0
    total_planned_taken = db.query(func.sum(LeaveRequest.no_of_days)).filter(LeaveRequest.email == user_email, LeaveRequest.status == "Approved", 
                                                                            LeaveRequest.leave_type == "Planned").scalar() or 0
    total_unplanned_taken = db.query(func.sum(LeaveRequest.no_of_days)).filter(LeaveRequest.email == user_email, LeaveRequest.status == "Approved", 
                                                                          LeaveRequest.leave_type == "Unplanned").scalar() or 0
    total_lwp_taken = db.query(func.sum(LeaveRequest.no_of_days)).filter(LeaveRequest.email == user_email, LeaveRequest.status == "Approved", 
                                                                          LeaveRequest.leave_type == "LWP").scalar() or 0
    rem_planned_leave = total_planned - total_planned_taken
    rem_unplanned_leave = total_unplanned - total_unplanned_taken
    return total_leaves, total_planned, total_unplanned, total_leaves_taken, total_planned_taken, total_unplanned_taken, total_lwp_taken


def monthly_leaves(db, user_email,year):
    leaves_by_month = []
    planned_leaves_by_month = []
    unplanned_leaves_by_month = []
    lwp_by_month = []
    current_date = datetime.now().date()  # Use only the date component
    
    for i in range(1, 13):
        start_date = current_date.replace(day=1, month=i, year=current_date.year)
        end_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        # Convert date objects to strings
        start_date_str = start_date.strftime('%m/%d/%Y')
        end_date_str = end_date.strftime('%m/%d/%Y')

        #Total leaves
        total_leaves_taken = db.query(func.sum(LeaveRequest.no_of_days)).filter(
            LeaveRequest.email == user_email,
            LeaveRequest.status == "Approved",
            LeaveRequest.from_date >= start_date_str,
            LeaveRequest.to_date <= end_date_str,
            # datetime.strptime(LeaveRequest.from_date, "%m/%d/%Y").year == year
        ).scalar() or 0

        leaves_by_month.append(total_leaves_taken)


        #Planned Leaves
        total_planned_leaves_taken = db.query(func.sum(LeaveRequest.no_of_days)).filter(
            LeaveRequest.email == user_email,
            LeaveRequest.status == "Approved",
            LeaveRequest.leave_type == "Planned",
            LeaveRequest.from_date >= start_date_str,
            LeaveRequest.to_date <= end_date_str
        ).scalar() or 0

        planned_leaves_by_month.append(total_planned_leaves_taken)


        #Unplanned Leaves
        total_unplanned_leaves_taken = db.query(func.sum(LeaveRequest.no_of_days)).filter(
            LeaveRequest.email == user_email,
            LeaveRequest.status == "Approved",
            LeaveRequest.leave_type == "Unplanned",
            LeaveRequest.from_date >= start_date_str,
            LeaveRequest.to_date <= end_date_str
        ).scalar() or 0

        unplanned_leaves_by_month.append(total_unplanned_leaves_taken)

        total_lwp_taken = db.query(func.sum(LeaveRequest.no_of_days)).filter(
            LeaveRequest.email == user_email,
            LeaveRequest.status == "Approved",
            LeaveRequest.leave_type == "LWP",
            LeaveRequest.from_date >= start_date_str,
            LeaveRequest.to_date <= end_date_str
        ).scalar() or 0

        lwp_by_month.append(total_lwp_taken)

    return leaves_by_month, planned_leaves_by_month, unplanned_leaves_by_month, lwp_by_month
