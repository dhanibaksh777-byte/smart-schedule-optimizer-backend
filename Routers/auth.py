from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
from schemas import CreateUser,UserLogin,UserResponse
from dotenv import load_dotenv
from datetime import datetime,timezone,timedelta
import json
from json import JSONDecodeError
import os
import bcrypt

load_dotenv()
Oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/Login")

SECRETE_KEY = os.getenv("secrete_key")
if not SECRETE_KEY:
    raise RuntimeError("secrete key is missing from  .env file")
ACCESS_TOKEN_EXPIRE = 30
ALGORITHIM = "HS256"

def hash_password(password : str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"),salt).decode("utf-8")
def create_token(data : dict[str,any]):

    payload = data.copy()
    Expire_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    payload.update({"exp" : Expire_time})
    token = jwt.encode(payload,SECRETE_KEY,algorithm=ALGORITHIM)
    return token

def verify_token(token : str):
    try:
        payload = jwt.decode(token,SECRETE_KEY,algorithms=[ALGORITHIM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid token or session expired!",headers={"www-Authenticate : Bearer"})

def get_current_user(token : str = Depends(Oauth2_scheme),db : Session = Depends(get_db)):
    payload = verify_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="user_id not found in token!")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found!")
    return db_user

router = APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/Register",status_code=status.HTTP_201_CREATED,response_model=UserResponse)
def register_user(user : CreateUser,db : Session = Depends(get_db)):
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="username already exists!")
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="user already exists!")

    hashed_password = hash_password(user.password)
    new_user = User(username = user.username , email = user.email,password = hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/Login")
def Login(user : UserLogin, db : Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not bcrypt.checkpw(user.password.encode("utf-8"),db_user.password.encode("utf-8")):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="email password incorrect!",headers={"www-Authenticate" : "Bearer"})

    token = create_token({"user_id" : db_user.id})
    return {"access_token" : token,"token_type" : "Bearer"}

    
    

      

    
    




    
    
    
        
    
    


