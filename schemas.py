from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional,List

class CreateUser(BaseModel):
    email : EmailStr 
    username : str 
    password : str


class UserLogin(BaseModel):
    email : EmailStr
    password : str


class UserResponse(BaseModel):
    id : int
    username : str 

    class Config:
        from_attributes = True


class CreateTask(BaseModel):
    title : str 
    content : str 


class TaskAiExtraction(BaseModel):
    priority: str
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    id : int 
    title : str 
    content : str 
    priority: str
    due_date : Optional[datetime]
    created_at : datetime
    user_id : int

    class Config:
        from_attrbutes = True