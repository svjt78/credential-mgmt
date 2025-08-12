from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import jwt
import os

from models import User
from schemas import (
    UserCreate,
    LoginRequest,
    LoginResponse,
    SignupResponse,
    ChangePasswordRequest,
    ResetPasswordRequest,
    ResetPasswordConfirm,
)
import auth
from database import SessionLocal

router = APIRouter()

# ----------------------------
# DB session dependency
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------
# SIGNUP (no email sent here)
# Returns verificationToken for the blog app to email.
# ----------------------------
@router.post("/signup", response_model=SignupResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Enforce unique email
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(user.password)
    generated_user_uuid = str(uuid.uuid4())

    verification_token = str(uuid.uuid4())
    token_ttl_hours = int(os.getenv("EMAIL_VERIFICATION_TTL_HOURS", "24"))
    expires_at = datetime.utcnow() + timedelta(hours=token_ttl_hours)

    new_user = User(
        user_id=generated_user_uuid,
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,
        email_verification_token=verification_token,
        token_expiration=expires_at,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "user_id": new_user.user_id,          # UUID
        "email": new_user.email,
        "username": new_user.username,
        "is_active": new_user.is_active,
        "is_verified": new_user.is_verified,
        "verificationToken": verification_token,
    }

# ----------------------------
# LOGIN (requires verified email)
# Returns bearer token + profile fields for blog auto-linking.
# ----------------------------
@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not user.hashed_password or not auth.verify_password(login_data.password, user.hashed_password):
        # generic message (no user enumeration)
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = auth.create_access_token(data={"user_id": user.user_id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,      # UUID
        "email": user.email,
        "username": user.username,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }

# ----------------------------
# VERIFY EMAIL (token-based)
# ----------------------------
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email_verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    if user.token_expiration and user.token_expiration < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token expired")

    user.is_verified = True
    user.email_verification_token = None
    user.token_expiration = None
    db.commit()

    return {"message": "Email verified successfully"}

# ----------------------------
# RESET PASSWORD (REQUEST)
# Returns resetToken for the blog app to email.
# ----------------------------
@router.post("/reset-password/request")
def reset_password_request(request_data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user:
        # Do not disclose existence
        return {"message": "If the email exists, a reset link has been sent"}

    reset_token = str(uuid.uuid4())
    user.password_reset_token = reset_token
    user.token_expiration = datetime.utcnow() + timedelta(hours=1)
    db.commit()

    return {"message": "If the email exists, a reset link has been sent", "resetToken": reset_token}

# ----------------------------
# RESET PASSWORD (CONFIRM)
# ----------------------------
@router.post("/reset-password/confirm")
def reset_password_confirm(data: ResetPasswordConfirm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.password_reset_token == data.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    if user.token_expiration and user.token_expiration < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token expired")

    user.hashed_password = auth.get_password_hash(data.new_password)
    user.password_reset_token = None
    user.token_expiration = None
    db.commit()

    return {"message": "Password reset successfully"}

# ----------------------------
# CHANGE PASSWORD (auth via token param)
# ----------------------------
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

# ----------------------------
# UPDATED DELETE USER ENDPOINT
# Make sure this endpoint exists and works properly
# ----------------------------
@router.delete("/users/{user_uuid}")
def delete_user(user_uuid: str, db: Session = Depends(get_db),
    x_service_token: str = Header(default="")):
    internal_token = os.getenv("INTERNAL_SERVICE_TOKEN", "")
    if not internal_token:
        raise HTTPException(status_code=500, detail="Server missing INTERNAL_SERVICE_TOKEN")
    if x_service_token != internal_token:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    user = db.query(User).filter(User.user_id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.post("/verify-email/resend")
def resend_verification_token(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Re-issue an email verification token for an unverified account.
    Returns: { verificationToken: "<token>" } on success.
    404 if user not found, 409 if already verified.
    """
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # Keep explicit so the blog app can show the right message (it falls back to 409 guidance)
        return JSONResponse(status_code=404, content={"detail": "User not found"})

    if user.is_verified:
        return JSONResponse(status_code=409, content={"detail": "User already verified"})

    # Issue a fresh token and expiry (24h window)
    new_token = str(uuid.uuid4())
    user.email_verification_token = new_token
    user.token_expiration = datetime.utcnow() + timedelta(hours=24)
    db.commit()

    return {"verificationToken": new_token}

# ----------------------------
# GET USER BY EMAIL (service-to-service)
# Protected by X-Service-Token header
# ----------------------------
@router.get("/users/by-email/{email}")
def get_user_by_email(
    email: str, 
    db: Session = Depends(get_db),
    x_service_token: str = Header(default="")
):
    """
    Fetch user details by email for service-to-service communication.
    Protected by internal service token.
    """
    import urllib.parse
    # Decode the email in case it's URL encoded
    email = urllib.parse.unquote(email)
    
    internal_token = os.getenv("INTERNAL_SERVICE_TOKEN", "")
    
    if not internal_token:
        raise HTTPException(status_code=500, detail="Server missing INTERNAL_SERVICE_TOKEN")
    
    if x_service_token != internal_token:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "user_id": user.user_id,  # UUID
        "email": user.email,
        "username": user.username,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
