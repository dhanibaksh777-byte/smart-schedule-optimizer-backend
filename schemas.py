from pydantic import BaseModel,EmailStr,Field
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
    title : str = Field(max_length=50)
    content : str = Field(min_length=50,max_length=500)


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
        from_attributes = True


class ResetPasswordRequest(BaseModel):
    token : str 
    new_password : str = Field(min_length=8)






