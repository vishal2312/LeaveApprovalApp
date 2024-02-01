from fastapi import APIRouter,Request, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT
from config import settings
from typing import Union, Optional
import json, requests
from api.schemas import Login, User, Admin
from api.service import create_user
from db.deps import get_db
import models
from datetime import date
from api.controller import my_leaves, my_profile_data
import api.service as service


router = APIRouter()
templates = Jinja2Templates(directory="templates")
templates.env.globals['API_URL'] = settings.WEB_API_URL
templates.env.globals['APP_URL'] = settings.WEB_APP_URL

# @router.get("/",include_in_schema=False)
# def index(request:Request,Authorize: AuthJWT = Depends()):
#     Authorize.jwt_required()
#     return  templates.TemplateResponse("admin_dashboard.html",{"request":request,"web_app_url":settings.WEB_APP_URL})

@router.get("/",include_in_schema=False)
def index(request:Request,Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user_data = db.query(models.User).filter(models.User.email == email).first()
    admin_data = db.query(models.Admin).filter(models.Admin.email == email).first()
    if user_data:
        return  templates.TemplateResponse("user_dashboard.html",{"request":request,"web_app_url":settings.WEB_APP_URL})
    elif admin_data:
        return  templates.TemplateResponse("admin_dashboard.html",{"request":request,"web_app_url":settings.WEB_APP_URL})
    
    raise HTTPException(status_code=404)
    
@router.get("/api",include_in_schema=False)
def index(request:Request,Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return  templates.TemplateResponse("admin_dashboard.html",{"request":request,"web_app_url":settings.WEB_APP_URL})


# Signup--------------------------------------------------------------------------------------------------------------------------------------
@router.get("/signup", include_in_schema=False)
def user_signup(request: Request, p: Union[str, None] = None):
    if not p:
        p = ''
    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/verify_account", include_in_schema=False)
def verify_account(request: Request):
    token = request.query_params.get('token',None)
    if not token:
        return HTMLResponse("<h3>404 not found</h3>")
    return templates.TemplateResponse("verify_account.html", {"request": request,'token':token})

# Login--------------------------------------------------------------------------------------------------------------------------------------------
@router.get("/login",include_in_schema=False)
def user_login(request:Request,p: Union[str, None] = None):
    if not p:
        p = '/user_dashboard'
    return templates.TemplateResponse("login.html",{"request":request,"return_page": p,"web_app_url":settings.WEB_APP_URL})

@router.post("/user/login",include_in_schema=False)
def login(request:Request, auth_user:Login, Authorize: AuthJWT = Depends()):
    payload = {'email':auth_user.email,'password':auth_user.password}
    auth_response = requests.post(settings.WEB_APP_URL + settings.API_AUTH_LOGIN_URL,json=payload)
    if auth_response.status_code == 200:
        auth_tokens = json.loads(auth_response.text)
        Authorize.set_access_cookies(auth_tokens['access_token'])
        Authorize.set_refresh_cookies(auth_tokens['refresh_token'])
        return {"message": "Success"}
    else:
        raise HTTPException(status_code=403, detail= "Incorrect Username or Password, try again")
    

# Admin--------------------------------------------------------------------------------------------------------------------------------------------
@router.get("/admin_login",include_in_schema=False)
def admin(request:Request,p: Union[str, None] = None):
    if not p:
        p = ''
    return templates.TemplateResponse("admin_login.html",{"request":request,"return_page": p,"web_app_url":settings.WEB_APP_URL})

@router.post("/admin/login",include_in_schema=False)
def admin_login(request:Request, auth_user:Admin, Authorize: AuthJWT = Depends()):
    payload = {'email':auth_user.email,'password':auth_user.password}
    auth_response = requests.post(settings.WEB_APP_URL + settings.API_AUTH_ADMIN_LOGIN_URL,json=payload)
    if auth_response.status_code == 200:
        auth_tokens = json.loads(auth_response.text)
        Authorize.set_access_cookies(auth_tokens['access_token'])
        Authorize.set_refresh_cookies(auth_tokens['refresh_token'])
        return {"message": "Success"}
    else:
        raise HTTPException(status_code=203, detail= "Incorrect Username or Password, try again")
    

@router.get("/forgot_password", include_in_schema=False)
def forgot_password(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.get("/reset_password", include_in_schema=False)
def reset_password(request: Request):
    token = request.query_params.get('token',None)
    if not token:
        return HTMLResponse("<h3>404 not found</h3>")
    return templates.TemplateResponse("reset_password.html", {"request": request,'token':token})

@router.get("/apply_leave", include_in_schema=False)
def apply_leave(request: Request,  db: Session = Depends(get_db),Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    user_data = db.query(models.User).filter(models.User.email == user_email).first()
    name1 = str(user_data.name)
    email1 = str(user_data.email)
    errors = {"from_date": "From date must be a future date", 
              "to_date": "To Date must be after From date", 
              "no_of_days": "Number of days must be a positive integer and less than or equal to 10", 
              "reason": "Reason cannot be empty and should be less than or equal to 50 characters"}
    
    return templates.TemplateResponse("apply_leave.html", {"request": request, "errors": errors, "name": name1, "email": email1})


@router.get("/manage_leave", include_in_schema=False, response_class=HTMLResponse)
def manage_leave(request: Request, status: Optional[str] = Query("all"), name: Optional[str] = Query(None), date_range: Optional[str] = Query(None), db: Session = Depends(get_db)):
    items = service.get_filtered_leave_requests(db, status, name, date_range)
    return templates.TemplateResponse("manage_leave.html", {"request": request, "items": items})


@router.get("/admin_dashboard", include_in_schema=False)
def apply_leave(request: Request, email: Optional[str] = Query(None), db: Session = Depends(get_db)):
    emails = db.query(models.User.email).all()
    items = service.email_filter(db, email)
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "emails": emails})


@router.get("/user_dashboard", include_in_schema=False)
def user_dashboard(request: Request, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    year = 2024
    total_leaves, total_planned, total_unplanned, total_leaves_taken, total_planned_taken, total_unplanned_taken, total_lwp_taken = service.leave_bifurcation(db, user_email)
    leaves_by_month, planned_leaves_by_month, unplanned_leaves_by_month, lwp_by_month = service.monthly_leaves(db, user_email, year)
    return templates.TemplateResponse("user_dashboard.html", {"request": request, "total_leaves": total_leaves, "total_planned": total_planned, 
                                                              "total_unplanned": total_unplanned, "total_leaves_taken": total_leaves_taken, 
                                                              "total_planned_taken": total_planned_taken, "total_unplanned_taken": total_unplanned_taken,
                                                              "leaves_by_month": leaves_by_month, "planned_leaves_by_month": planned_leaves_by_month,
                                                              "unplanned_leaves_by_month" : unplanned_leaves_by_month, "total_lwp": total_lwp_taken,
                                                              "lwp_by_month": lwp_by_month})


@router.get("/my_leave", include_in_schema=False, response_class=HTMLResponse)
def my_leave(request: Request, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    leave_history_data, leaves_taken, planned_leaves_taken, unplanned_leaves_taken, leaves_remaining, planned_leaves_rem, unplanned_leaves_rem = my_leaves(Authorize, db)
    # leave_history_data = db.query(LeaveRequest).all()
    return templates.TemplateResponse("my_leave.html", {"request": request, "leave_history": leave_history_data, "leaves_taken": leaves_taken,
                                                        "leaves_remaining": leaves_remaining, "planned_leaves_taken": planned_leaves_taken,
                                                        "unplanned_leaves_taken": unplanned_leaves_taken, "planned_leaves_rem": planned_leaves_rem,
                                                        "unplanned_leaves_rem": unplanned_leaves_rem})


@router.get("/login", response_class=HTMLResponse)
def logout(request: Request):
    response = templates.TemplateResponse("login.html", {"request": request})
    response.delete_cookie("Authorization")
    return response

@router.get("/my_profile", include_in_schema=False)
def apply_leave(request: Request, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    user_data = my_profile_data(Authorize,db)
    return templates.TemplateResponse("my_profile.html", {"request": request, "user_data": user_data})


@router.get("/calendar", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})