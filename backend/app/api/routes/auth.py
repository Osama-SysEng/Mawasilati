from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.audit import append_audit
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token, hash_password, verify_password
from app.models import AuthSession, User
from app.schemas import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenResponse, UserOut

router = APIRouter()


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        name=user.name,
        phone=user.phone,
        role=user.role,
        wallet_balance=float(user.wallet_balance),
    )


def _tokens(user: User, session: AuthSession) -> TokenResponse:
    return TokenResponse(
        user=_user_out(user),
        access_token=create_access_token(user.id, session.id),
        refresh_token=create_refresh_token(user.id, session.id, session.refresh_jti),
        expires_in=settings.access_token_expire_minutes * 60,
        session_id=session.id,
    )


def _create_session(db: Session, user: User, request: Request) -> AuthSession:
    session = AuthSession(
        id=str(uuid4()),
        user_id=user.id,
        refresh_jti=str(uuid4()),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(session)
    append_audit(
        db,
        actor_id=user.id,
        action='AUTH_SESSION_CREATED',
        entity_type='AuthSession',
        entity_id=session.id,
        correlation_id=request.headers.get('X-Request-Id'),
    )
    db.commit()
    db.refresh(session)
    return session


@router.post('/register', response_model=TokenResponse)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(User).filter(User.phone == payload.phone).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail='Phone number already registered')
    user = User(
        id=str(uuid4()),
        name=payload.name,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=payload.role,
        wallet_balance=payload.wallet_balance,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _tokens(user, _create_session(db, user, request))


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.phone == payload.phone).first()
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid phone number or password')
    return _tokens(user, _create_session(db, user, request))


@router.post('/refresh', response_model=TokenResponse)
def refresh(payload: RefreshTokenRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    claims = decode_refresh_token(payload.refresh_token)
    if not claims:
        raise HTTPException(status_code=401, detail='Invalid refresh token')
    session = db.query(AuthSession).filter(AuthSession.id == claims['sid'], AuthSession.user_id == claims['sub']).first()
    if not session or session.revoked_at is not None:
        raise HTTPException(status_code=401, detail='Refresh session is not active')
    expiry = session.expires_at.replace(tzinfo=timezone.utc) if session.expires_at.tzinfo is None else session.expires_at
    if expiry <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail='Refresh token expired')
    user = db.query(User).filter(User.id == session.user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    if session.refresh_jti != claims['jti']:
        session.revoked_at = datetime.now(timezone.utc)
        session.revoke_reason = 'refresh_replay_detected'
        append_audit(db, actor_id=user.id, action='AUTH_SESSION_REPLAY_BLOCKED', entity_type='AuthSession', entity_id=session.id, correlation_id=request.headers.get('X-Request-Id'))
        db.commit()
        raise HTTPException(status_code=401, detail='Refresh token replay detected')
    session.refresh_jti = str(uuid4())
    append_audit(db, actor_id=user.id, action='AUTH_SESSION_REFRESHED', entity_type='AuthSession', entity_id=session.id, correlation_id=request.headers.get('X-Request-Id'))
    db.commit()
    db.refresh(session)
    return _tokens(user, session)


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    token = request.headers.get('authorization', '').removeprefix('Bearer ')
    claims = decode_access_token(token) or {}
    session = db.query(AuthSession).filter(AuthSession.id == claims.get('sid'), AuthSession.user_id == current_user.id).first()
    if session and session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        session.revoke_reason = 'user_logout'
        append_audit(db, actor_id=current_user.id, action='AUTH_SESSION_REVOKED', entity_type='AuthSession', entity_id=session.id, correlation_id=request.headers.get('X-Request-Id'))
        db.commit()


@router.get('/me', response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return _user_out(current_user)


@router.get('/profile', response_model=UserOut)
def profile(current_user: User = Depends(get_current_user)) -> UserOut:
    return _user_out(current_user)
