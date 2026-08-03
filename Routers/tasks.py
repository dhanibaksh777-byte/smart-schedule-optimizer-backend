from database import get_db
from Routers.auth import get_current_user
from fastapi import APIRouter,Depends,HTTPException,status
from schemas import CreateTask
from sqlalchemy.orm import Session
from llm_client import get_response
from models import User
from models import Task
from pydantic import BaseModel
from typing import Optional


class UpdatedTask(BaseModel):
    title : Optional[str] = None
    content : Optional[str] 


router = APIRouter(prefix="/task", tags=["Task Manager"])


@router.post("/Create-task",status_code = status.HTTP_201_CREATED)
def create_task(task : CreateTask,current_user : User = Depends(get_current_user),db : Session = Depends(get_db)):
    try:
        ai_data = get_response(task.content)
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    
    new_task = Task(title = task.title,content = task.content,user_id = current_user.id,due_date = ai_data.due_date,priority = ai_data.priority)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/get-all-tasks")
def get_all_tasks(current_user : User = Depends(get_current_user), db : Session = Depends(get_db)):
        task = db.query(Task).filter(Task.user_id == current_user.id).all()
        return task


@router.get("/get-one-task/{task_id}")
def get_one_task(task_id : int,current_user : User = Depends(get_current_user),db : Session = Depends(get_db)):
        task = db.query(Task).filter(Task.id == task_id,Task.user_id == current_user.id).first()
        if not task:
               raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="task not found!")
        return task



@router.patch("/update-task/{task_id}")
def update_task(task_id : int,updated : UpdatedTask ,current_user : User = Depends(get_current_user),db : Session = Depends(get_db)):
            task = db.query(Task).filter(Task.id == task_id,Task.user_id == current_user.id).first()
            if not task:
                   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="task not found!")
            if updated.title is not None:
               task.title = updated.title
            if updated.content is not None: 
                task.content = updated.content

            try:
                ai_data = get_response(updated.content)
                task.due_date = ai_data.due_date
                task.priority = ai_data.priority

            except ValueError as e:
                     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

            db.add(task)
            db.commit()
            db.refresh(task)
            return {"message" : "task updated successfully!"}


@router.delete("/delete-task/{task_id}")
def delete_task(task_id : int, current_user : User = Depends(get_current_user),db : Session = Depends(get_db)):
         task = db.query(Task).filter(Task.id == task_id,Task.user_id == current_user.id).first()
         if not task:
                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="task not found!")
         db.delete(task)
         db.commit()
         return {"message" : "task deleted successfully!"}
         
