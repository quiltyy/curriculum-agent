from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.models import User
from app.schemas import RegisterIn, LoginIn, TokenOut, MeOut, RefreshIn
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    TokenType,
)
from app.deps import get_current_user

app = FastAPI(title="Curriculum Agent Backend with Auth")

# Create tables (for dev/demo; in prod use Alembic migrations)
Base.metadata.create_all(bind=engine)


@app.post("/auth/register", response_model=MeOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return MeOut(id=user.id, email=user.email)


@app.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access = create_access_token(user.id, user.token_version)
    refresh = create_refresh_token(user.id, user.token_version)
    return TokenOut(access_token=access, refresh_token=refresh)


@app.get("/auth/me", response_model=MeOut)
def me(current_user: User = Depends(get_current_user)):
    return MeOut(id=current_user.id, email=current_user.email)


@app.post("/auth/refresh", response_model=TokenOut)
def refresh(payload: RefreshIn, db: Session = Depends(get_db)):
    try:
        data = decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    if data.get("type") != TokenType.REFRESH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token type"
        )

    user_id = int(data.get("sub", 0))
    tv = int(data.get("tv", -1))
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    if user.token_version != tv:
        raise HTTPException(status_code=401, detail="Token revoked")

    # Rotate refresh token
    user.token_version += 1
    db.add(user)
    db.commit()
    db.refresh(user)

    access = create_access_token(user.id, user.token_version)
    refresh_token = create_refresh_token(user.id, user.token_version)
    return TokenOut(access_token=access, refresh_token=refresh_token)


@app.post("/auth/register", response_model=MeOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return MeOut(id=user.id, email=user.email, role=user.role)

@app.get("/auth/me", response_model=MeOut)
def me(current_user: User = Depends(get_current_user)):
    return MeOut(id=current_user.id, email=current_user.email, role=current_user.role)

