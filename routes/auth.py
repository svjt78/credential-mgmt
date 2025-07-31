from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import jwt

from models import User
from schemas import (
    UserCreate,
    LoginRequest,
    LoginResponse,
    SignupResponse,  # Newly added schema for signup
    ChangePasswordRequest,
    ResetPasswordRequest,
    ResetPasswordConfirm
)
import auth
from database import SessionLocal
from fastapi.responses import JSONResponse

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Stub for sending email (this function is now unused since verification is suppressed)
def send_email(to_email: str, subject: str, body: str):
    print(f"Sending email to {to_email} with subject '{subject}' and body:\n{body}")

@router.post("/signup", response_model=SignupResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check for existing email or username
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = auth.get_password_hash(user.password)
    generated_user_id = str(uuid.uuid4())
    
    # Immediately mark user as verified by setting is_verified=True
    new_user = User(
        user_id=generated_user_id,
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True,  # Suppress email verification
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate JWT token immediately upon signup
    access_token = auth.create_access_token(data={"user_id": new_user.user_id})
    
    return {
        "id": new_user.id,
        "email": new_user.email,
        "username": new_user.username,
        "is_active": new_user.is_active,
        "is_verified": new_user.is_verified,
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.username,
    }

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not user.hashed_password or not auth.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    # Email verification check removed so login proceeds immediately
    access_token = auth.create_access_token(data={"user_id": user.user_id})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.username}

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    # This endpoint is now redundant, but left in case it's needed in the future
    user = db.query(User).filter(User.email_verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    if user.token_expiration < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token expired")
    
    user.is_verified = True
    user.email_verification_token = None
    user.token_expiration = None
    db.commit()
    return {"message": "Email verified successfully"}

@router.post("/reset-password/request")
def reset_password_request(request_data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}
    
    reset_token = str(uuid.uuid4())
    user.password_reset_token = reset_token
    user.token_expiration = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    reset_link = f"http://yourdomain.com/auth/reset-password/confirm?token={reset_token}"
    send_email(user.email, "Password Reset", f"Click here to reset your password: {reset_link}")
    
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password/confirm")
def reset_password_confirm(data: ResetPasswordConfirm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.password_reset_token == data.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    if user.token_expiration < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token expired")
    
    user.hashed_password = auth.get_password_hash(data.new_password)
    user.password_reset_token = None
    user.token_expiration = None
    db.commit()
    return {"message": "Password reset successfully"}

@router.post("/change-password")
def change_password(data: ChangePasswordRequest, token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id = payload.get("user_id")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not auth.verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    
    user.hashed_password = auth.get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
