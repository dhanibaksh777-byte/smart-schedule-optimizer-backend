from database import get_db
from Routers.auth import get_current_user
from fastapi import APIRouter,Depends,HTTPException,status
from schemas import CreateTask
from sqlalchemy.orm import Session
from llm_client import get_response
from models import User
from models import Task


router = APIRouter(prefix="/task", tags=["Task Manager"])

@router.post("/Create-task",status_code = status.HTTP_201_CREATED)
def create_task(task : CreateTask,current_user : User = Depends(get_current_user),db : Session = Depends(get_db)):
    try:
        ai_data = get_response(task.content)

    except ValueError as e:
        raise HTTPException(status_Code = status.HTTP_500_INTERNAL_SERVER_ERROR,detail=e)
    
    new_task = Task(title = task.title,content = task.content,user_id = current_user.id,due_date = ai_data.Extracted_due_date,priority = ai_data.Extracted_priority)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/get-all-tasks")
def get_all_tasks(task_id : int,current_user : User = Depends(get_db), db : Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id,Task.user_id == current_user.id).first()
    return task

@router.get("/get-one-task/{task_id}")
def get_one_task(task_id : int,current_user : User = Depends(get_db),db : Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id,Task.user_id == current_user.id).first()
    return task




