from utils.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Date, Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    is_verified = Column(Boolean, default=False)
    leaves = relationship("LeaveRequest", back_populates="user")

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)

class LeaveRequest(Base):
    __tablename__ = "leaves"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, ForeignKey("users.email"))
    user = relationship("User",back_populates="leaves")
    leave_type = Column(String) 
    from_date = Column(String) 
    to_date = Column(String)  
    no_of_days = Column(Integer)
    applied_on = Column(String, default=func.strftime('%m/%d/%Y', func.now()))
    reason = Column(String)  
    status = Column("status", String, default="Pending")
    