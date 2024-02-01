from pydantic import AnyHttpUrl, EmailStr, validator
from pydantic import BaseSettings
import datetime

class Settings(BaseSettings):
    MSG_DATA_EXISTS = "User already exist"
    DB_NAME : str 
    DB_HOST : str
    DB_USER : str
    DB_PASSWORD : str
    DB_PORT : str
    authjwt_secret_key: str 
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False
    WEB_APP_URL :str
    WEB_API_URL :str
    API_AUTH_LOGIN_URL : str
    API_AUTH_ADMIN_LOGIN_URL: str
    PAGE_LIMIT : int
    MSG_EMAIL_EXISTS = "Email ID already exists"
    MSG_LEAVE_REQUEST = "Request has been send to admin"
    MSG_CHECK_EMAIL = "Email is not Registered"
    USERNAME = 'vishaladdnectar@gmail.com'
    PASSWORD = 'uwbo xlli ijmt bkwc'
    SECRET_KEY = "your_secret_key"
    ALGORITHM = "HS256"
    TOKEN_EXPIRATION = datetime.timedelta(hours=1)
    class Config:
        env_file = ".env"

settings = Settings()
