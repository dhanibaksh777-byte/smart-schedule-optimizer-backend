from database import Base 
from sqlalchemy import Column,String,Integer,ForeignKey,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime,timezone

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True,nullable=False,index=True)
    email = Column(String,unique=True,nullable=False,index=True)
    password = Column(String)
    tasks = relationship("Task",back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String(100),nullable=False)
    content = Column(String,nullable=True)
    status = Column(Boolean,default=False)
    priority = Column(String, default="medium", nullable=False)
    created_at = Column(datetime(timezone=True),default=datetime.now(timezone.utc))
    due_date = Column(datetime(timezone=True),nullable = True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    owner = relationship("User",back_populates="tasks")