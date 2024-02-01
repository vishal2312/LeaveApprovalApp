from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from api.router import api_router
from apps.router import apps_router
import models, api.schemas as schemas
from utils.database import SessionLocal, engine
from db.deps import get_db
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from config import settings
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

models.Base.metadata.create_all(engine)

app.mount('/static,', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

# callback to get your configuration
@AuthJWT.load_config
def get_config():
    return settings

# in production, you can tweak performance using orjson response
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    # return JSONResponse(
    #     status_code=exc.status_code,
    #     content={"detail": exc.message}
    # )
    return RedirectResponse(url="/login",status_code=302)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000","http://127.0.0.1:8000", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(apps_router)

# @app.post("/leave_request")
# def leave_request(request: schemas.LeaveRequest, db: Session = Depends(get_db)):
#     leave = models.LeaveRequest(emp_id=request.emp_id, start_date=request.start_date, end_date=request.end_date, reason = request.reason)
#     db.add(leave)
#     db.commit()
#     db.refresh(leave)
#     return leave


# @app.post("/admin")
# def admin_login(request: schemas.Admin, db: Session = Depends(get_db)):
#     admin_cred = db.query(models.Admin).filter(models.Admin.email == request.email).first()
#     if not admin_cred:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
#     if not (admin_cred.password == request.password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password")

#     return admin_cred

