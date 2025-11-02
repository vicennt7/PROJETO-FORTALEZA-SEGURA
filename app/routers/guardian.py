from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..models import GuardianMode, LockEvent, SecurityCheck, User
from ..schemas import (
    GUARDIAN_SEQUENCE_LENGTH,
    GuardianActivationRequest,
    GuardianConfirmationRequest,
    GuardianStatusResponse,
    GuardianUnlockRequest,
)

router = APIRouter(prefix="/guardian", tags=["Guardian Mode"])
settings = get_settings()


def _resolve_interval_hours(requested_hours: int | None) -> int:
    """Return a sanitized confirmation interval respecting configured bounds."""

    if requested_hours is None:
        return settings.guardian_check_interval_hours

    min_hours = settings.guardian_min_check_interval_hours
    max_hours = settings.guardian_max_check_interval_hours
    if not (min_hours <= requested_hours <= max_hours):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Intervalo de checagem inválido. Informe um valor entre "
                f"{min_hours} e {max_hours} horas."
            ),
        )

    return requested_hours


def _ensure_guardian_mode(session: Session, user_id: UUID) -> GuardianMode:
    guardian_mode = session.query(GuardianMode).filter(GuardianMode.user_id == user_id).one_or_none()
    if not guardian_mode:
        guardian_mode = GuardianMode(
            user_id=user_id,
            active=False,
            check_interval=timedelta(hours=settings.guardian_check_interval_hours),
        )
        session.add(guardian_mode)
        session.flush()
    elif not guardian_mode.check_interval:
        guardian_mode.check_interval = timedelta(hours=settings.guardian_check_interval_hours)
    return guardian_mode


def _calculate_next_deadline(guardian_mode: GuardianMode) -> datetime | None:
    if not guardian_mode.last_confirmation_at:
        return None
    return guardian_mode.last_confirmation_at + guardian_mode.check_interval


def _enforce_lock(session: Session, guardian_mode: GuardianMode, reason: str) -> GuardianMode:
    if not guardian_mode.lock_active:
        guardian_mode.lock_active = True
        lock_event = LockEvent(
            guardian_mode_id=guardian_mode.id,
            locked_at=datetime.utcnow(),
            reason=reason,
        )
        session.add(lock_event)
    return guardian_mode


def _auto_lock_if_overdue(session: Session, guardian_mode: GuardianMode) -> GuardianMode:
    if not guardian_mode.active:
        return guardian_mode
    if guardian_mode.lock_active:
        return guardian_mode
    deadline = _calculate_next_deadline(guardian_mode)
    if deadline and datetime.utcnow() > deadline:
        guardian_mode = _enforce_lock(session, guardian_mode, reason="confirmation-overdue")
        security_check = SecurityCheck(
            guardian_mode_id=guardian_mode.id,
            confirmed=False,
            requested_at=deadline,
        )
        session.add(security_check)
    return guardian_mode


@router.post("/activate", response_model=GuardianStatusResponse, status_code=status.HTTP_200_OK)
def activate_guardian_mode(
    payload: GuardianActivationRequest,
    session: Session = Depends(get_db),
) -> GuardianStatusResponse:
    user = session.query(User).filter(User.id == payload.user_id).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if len(payload.button_sequence) != GUARDIAN_SEQUENCE_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sequência de ativação deve conter {GUARDIAN_SEQUENCE_LENGTH} pressões válidas.",
        )

    guardian_mode = _ensure_guardian_mode(session, user.id)
    guardian_mode.active = True
    guardian_mode.accessibility_permission = payload.accessibility_permission_granted
    guardian_mode.activated_at = datetime.utcnow()
    guardian_mode.last_confirmation_at = guardian_mode.activated_at
    guardian_mode.lock_active = False

    interval_hours = _resolve_interval_hours(payload.check_interval_hours)
    guardian_mode.check_interval = timedelta(hours=interval_hours)

    security_check = SecurityCheck(
        guardian_mode_id=guardian_mode.id,
        confirmed=True,
        confirmed_at=guardian_mode.activated_at,
        requested_at=guardian_mode.activated_at,
    )
    session.add(security_check)
    session.commit()
    session.refresh(guardian_mode)

    return GuardianStatusResponse(
        active=guardian_mode.active,
        lock_active=guardian_mode.lock_active,
        last_confirmation_at=guardian_mode.last_confirmation_at,
        next_confirmation_deadline=_calculate_next_deadline(guardian_mode),
        check_interval_hours=int(guardian_mode.check_interval.total_seconds() // 3600),
    )


@router.get("/status/{user_id}", response_model=GuardianStatusResponse)
def guardian_status(user_id: UUID, session: Session = Depends(get_db)) -> GuardianStatusResponse:
    guardian_mode = _ensure_guardian_mode(session, user_id)
    guardian_mode = _auto_lock_if_overdue(session, guardian_mode)
    session.commit()

    return GuardianStatusResponse(
        active=guardian_mode.active,
        lock_active=guardian_mode.lock_active,
        last_confirmation_at=guardian_mode.last_confirmation_at,
        next_confirmation_deadline=_calculate_next_deadline(guardian_mode),
        check_interval_hours=int(guardian_mode.check_interval.total_seconds() // 3600)
        if guardian_mode.check_interval
        else None,
    )


@router.post("/confirm", response_model=GuardianStatusResponse)
def confirm_guardian_mode(
    payload: GuardianConfirmationRequest,
    session: Session = Depends(get_db),
) -> GuardianStatusResponse:
    guardian_mode = _ensure_guardian_mode(session, payload.user_id)
    if not guardian_mode.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Modo Guardião não está ativo")

    guardian_mode = _auto_lock_if_overdue(session, guardian_mode)
    if guardian_mode.lock_active:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Modo Guardião está bloqueado")

    guardian_mode.last_confirmation_at = datetime.utcnow()
    security_check = SecurityCheck(
        guardian_mode_id=guardian_mode.id,
        confirmed=True,
        confirmed_at=guardian_mode.last_confirmation_at,
        requested_at=guardian_mode.last_confirmation_at,
    )
    session.add(security_check)
    session.commit()

    return GuardianStatusResponse(
        active=guardian_mode.active,
        lock_active=guardian_mode.lock_active,
        last_confirmation_at=guardian_mode.last_confirmation_at,
        next_confirmation_deadline=_calculate_next_deadline(guardian_mode),
        check_interval_hours=int(guardian_mode.check_interval.total_seconds() // 3600),
    )


@router.post("/lock", response_model=GuardianStatusResponse)
def manual_lock(
    payload: GuardianConfirmationRequest,
    session: Session = Depends(get_db),
) -> GuardianStatusResponse:
    guardian_mode = _ensure_guardian_mode(session, payload.user_id)
    guardian_mode = _enforce_lock(session, guardian_mode, reason="manual")
    session.commit()

    return GuardianStatusResponse(
        active=guardian_mode.active,
        lock_active=guardian_mode.lock_active,
        last_confirmation_at=guardian_mode.last_confirmation_at,
        next_confirmation_deadline=_calculate_next_deadline(guardian_mode),
        check_interval_hours=int(guardian_mode.check_interval.total_seconds() // 3600)
        if guardian_mode.check_interval
        else None,
    )


@router.post("/unlock", response_model=GuardianStatusResponse)
def unlock_guardian_mode(
    payload: GuardianUnlockRequest,
    session: Session = Depends(get_db),
) -> GuardianStatusResponse:
    guardian_mode = _ensure_guardian_mode(session, payload.user_id)
    user = session.query(User).filter(User.id == payload.user_id).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if user.face_reference != payload.face_reference:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Biometria facial não corresponde")

    guardian_mode.lock_active = False
    guardian_mode.active = False
    guardian_mode.last_confirmation_at = datetime.utcnow()

    lock_event = (
        session.query(LockEvent)
        .filter(LockEvent.guardian_mode_id == guardian_mode.id, LockEvent.unlocked_at.is_(None))
        .order_by(LockEvent.locked_at.desc())
        .first()
    )
    if lock_event:
        lock_event.unlocked_at = datetime.utcnow()

    session.commit()

    return GuardianStatusResponse(
        active=guardian_mode.active,
        lock_active=guardian_mode.lock_active,
        last_confirmation_at=guardian_mode.last_confirmation_at,
        next_confirmation_deadline=_calculate_next_deadline(guardian_mode),
        check_interval_hours=int(guardian_mode.check_interval.total_seconds() // 3600)
        if guardian_mode.check_interval
        else None,
    )
