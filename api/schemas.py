from pydantic import BaseModel
from datetime import date

class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True

class User(OurBaseModel):
    name: str
    email: str
    password: str

class ShowUser(User):
    email: str
    password: str
    class Config():
        orm_mode = True

class Admin(OurBaseModel):
    email: str
    password: str
    
class LeaveRequest(OurBaseModel):
    name: str
    email: str
    leave_type: str
    from_date: str
    to_date: str
    no_of_days: int
    reason: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class Login(BaseModel):
    email :str
    password :str

    class Config:
        orm_mode = True

class forgot(BaseModel):
    email :str

    class Config:
        orm_mode = True

class reset(OurBaseModel):
    new_password :str
    confirm_password: str