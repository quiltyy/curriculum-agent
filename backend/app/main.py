from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db import models
from backend.app.db.database import engine, get_db
from backend.app.db.schemas import RegisterIn, LoginIn, TokenOut, MeOut, RefreshIn
from backend.app.api.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)

# Ensure tables exist (mostly for dev, Alembic is preferred in prod)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# ------------------ AUTH ENDPOINTS ------------------ #


@app.post("/auth/register", response_model=MeOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # ✅ use user.user_id
    return MeOut(user_id=user.user_id, email=user.email, role=user.role)


@app.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token({"user_id": user.user_id})
    refresh = create_refresh_token({"user_id": user.user_id})
    return TokenOut(access_token=access, refresh_token=refresh)


@app.post("/auth/refresh", response_model=TokenOut)
def refresh(payload: RefreshIn):
    data = decode_token(payload.refresh_token)
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = data.get("user_id")
    access = create_access_token({"user_id": user_id})
    refresh = create_refresh_token({"user_id": user_id})
    return TokenOut(access_token=access, refresh_token=refresh)


@app.get("/auth/me", response_model=MeOut)
def me(current_user: models.User = Depends(get_current_user)):
    return MeOut(
        user_id=current_user.user_id, email=current_user.email, role=current_user.role
    )


@app.post("/auth/logout")
def logout(_: models.User = Depends(get_current_user)):
    # Stateless JWT logout = client just discards token
    return {"message": "Logged out"}
