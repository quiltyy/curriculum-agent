from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models
from app.database import engine, get_db
from app.schemas import RegisterIn, LoginIn, TokenOut, MeOut, RefreshIn
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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
    return MeOut(id=user.id, email=user.email, role=user.role)


@app.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token({"user_id": user.id})
    refresh = create_refresh_token({"user_id": user.id})
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
    return MeOut(id=current_user.id, email=current_user.email, role=current_user.role)


@app.post("/auth/logout")
def logout(_: models.User = Depends(get_current_user)):
    # For stateless JWT, logout is handled client-side (token discard)
    return {"message": "Logged out"}
