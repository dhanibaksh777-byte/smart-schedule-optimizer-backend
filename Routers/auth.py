from fastapi import APIRouter,Depends,HTTPException,status,Request
from sqlalchemy.orm import Session
from database import get_db
from models import User
from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
from schemas import CreateUser,UserLogin,UserResponse,ResetPasswordRequest
from dotenv import load_dotenv
from datetime import datetime,timezone,timedelta
from core.rate_limit import limiter
from core.email_service import send_email
from pydantic import BaseModel,EmailStr
import json
from json import JSONDecodeError
import os
import bcrypt


class forgot_password_request(BaseModel):
    email : EmailStr


load_dotenv()
Oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/Login")

SECRETE_KEY = os.getenv("secrete_key")
if not SECRETE_KEY:
    raise RuntimeError("secrete key is missing from  .env file")
ACCESS_TOKEN_EXPIRE = 30
RESET_ACCESS_TOKEN_EXPIRE = 5
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

def create_token_with_purpose(data : dict[str,any],purpose : str,expiry_time : int):
    payload = data.copy()
    Expire_time = datetime.now(timezone.utc) + timedelta(minutes=expiry_time)
    payload.update({"exp" : Expire_time,"purpose": purpose})
    reset_token = jwt.encode(payload,SECRETE_KEY,algorithm=ALGORITHIM)
    return reset_token

def verify_token(token : str):
    try:
        payload = jwt.decode(token,SECRETE_KEY,algorithms=[ALGORITHIM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid token or session expired!",headers={"www-Authenticate" : "Bearer"})

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

@router.post("/Register",status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def register_user(request : Request,user : CreateUser,db : Session = Depends(get_db)):
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
    print(f"Debug: user_id created")
    email_verification_token = create_token_with_purpose({"user_id" : new_user.id},"email verification",15)
    print(f"token created!")
    verification_link = f"https://frontend-gse2.vercel.app/verify-email?token={email_verification_token}"
    html_content = f"""
<div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 30px; border: 1px solid #e0e0e0; border-radius: 8px;">
    <h2 style="color: #1a1a1a; margin-bottom: 10px;">Verify Your Email</h2>
    <p style="color: #444; font-size: 15px; line-height: 1.6;">
        We received your email for registration. Click the button below to verify your email.
    </p>
    <div style="text-align: center; margin: 30px 0;">
        <a href="{verification_link}" style="display:inline-block; padding:12px 28px; background-color:#2563eb; color:#ffffff; text-decoration:none; border-radius:6px; font-weight:bold; font-size:14px;">
            verify email
        </a>
    </div>
    <p style="color: #666; font-size: 13px; line-height: 1.6;">
        This link will expire in 15 minutes for security reasons.
    </p>
    <p style="color: #666; font-size: 13px; line-height: 1.6;">
        If you did not try to Register, you can safely ignore this email — your account remains secure.
    </p>
    <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
    <p style="color: #999; font-size: 12px;">
        AI Task Automator
    </p>
</div>
"""
    send_email(new_user.email,"Email Verification",html_content)
    print(f"Debug:sending....")
    return {
    "message": "Registration successful! Please check your email to verify your account.",
    "user": {"id": new_user.id, "username": new_user.username}
}  
    


@router.get("/verify-email")
@limiter.limit("10/minute")
def get_verified(request : Request,token : str,db : Session = Depends(get_db)):
    decoded_payload = verify_token(token)
    if decoded_payload.get("purpose") != "email verification":
        raise HTTPException(status = status.HTTP_401_UNAUTHORIZED,detail="invalid token purpose!")
    user_id = decoded_payload.get("user_id")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="user not found!")
    db_user.is_verified = True
    db.commit()
    return {"message":"Email Verified Successfully!"}

    
@router.post("/Login")
@limiter.limit("5/minute")
def Login(request : Request,user : UserLogin, db : Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not bcrypt.checkpw(user.password.encode("utf-8"),db_user.password.encode("utf-8")):
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,detail="email password incorrect!",headers={"www-Authenticate" : "Bearer"})

    token = create_token({"user_id" : db_user.id})
    return {"access_token" : token,"token_type" : "Bearer"}


@router.post("/reset-password")
@limiter.limit("5/minute")
def confirm_reset_token(request : Request,payload :ResetPasswordRequest,db : Session = Depends(get_db)):
       decoded_payload = verify_token(payload.token)

       if decoded_payload.get("purpose") != "password reset":
           raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail ="invalid token payload!")

       user_id = decoded_payload.get("user_id")
       if not user_id:
           raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="invalid token payload!")
       db_user = db.query(User).filter(User.id == user_id).first()
       if not db_user:
           raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="user not found!")
       db_user.password = hash_password(payload.new_password)
       db.commit()


       return {"message" : "password has been reset Successfully!"}
    
     
@router.post("/forgot-password")
@limiter.limit("2/minute")
def reset_password(request : Request,payload : forgot_password_request,db : Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        print(f"no user found for {payload.email}")
    if user:
            print(f"sending email.... to {user.email}")
            token = create_token_with_purpose({"user_id" : user.id},"password reset",15)
            reset_link =f"https://frontend-gse2.vercel.app/reset-password?token={token}"
            html_content = f"""
<div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 30px; border: 1px solid #e0e0e0; border-radius: 8px;">
    <h2 style="color: #1a1a1a; margin-bottom: 10px;">Reset Your Password</h2>
    <p style="color: #444; font-size: 15px; line-height: 1.6;">
        We received a request to reset the password for your account. Click the button below to choose a new password.
    </p>
    <div style="text-align: center; margin: 30px 0;">
        <a href="{reset_link}" style="display:inline-block; padding:12px 28px; background-color:#2563eb; color:#ffffff; text-decoration:none; border-radius:6px; font-weight:bold; font-size:14px;">
            Reset Password
        </a>
    </div>
    <p style="color: #666; font-size: 13px; line-height: 1.6;">
        This link will expire in 15 minutes for security reasons.
    </p>
    <p style="color: #666; font-size: 13px; line-height: 1.6;">
        If you did not request a password reset, you can safely ignore this email — your account remains secure.
    </p>
    <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
    <p style="color: #999; font-size: 12px;">
        AI Task Automator
    </p>
</div>
"""
            send_email(user.email,"password reset",html_content)
    
    return {"message": "If this email exists, a reset link has been sent."}