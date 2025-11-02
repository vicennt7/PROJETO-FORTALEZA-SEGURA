from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Badge, Report, User, UserBadge
from ..schemas import (
    BadgeCreate,
    BadgeRead,
    LeaderboardEntry,
    ReportCreate,
    ReportRead,
    ReportValidateRequest,
)

router = APIRouter(prefix="/community", tags=["Community"])


POINTS_VALIDATION_LIMIT = 100


def _point_from_latlon(latitude: float, longitude: float) -> WKTElement:
    return WKTElement(f"POINT({longitude} {latitude})", srid=4326)


def _award_badges(session: Session, user: User) -> None:
    badges = session.query(Badge).order_by(Badge.points_threshold).all()
    owned_badge_ids = {badge.badge_id for badge in user.badges}
    for badge in badges:
        if badge.id in owned_badge_ids:
            continue
        if user.points >= badge.points_threshold:
            session.add(UserBadge(user_id=user.id, badge_id=badge.id))


@router.post("/reports", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate, session: Session = Depends(get_db)) -> Report:
    user = session.query(User).filter(User.id == payload.user_id).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    descricao = payload.description.strip()
    if not descricao:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Descrição do relato não pode ser vazia")

    report = Report(
        user_id=user.id,
        description=descricao,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location=_point_from_latlon(payload.latitude, payload.longitude),
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


@router.post("/reports/{report_id}/validate", response_model=ReportRead)
def validate_report(
    report_id: UUID,
    payload: ReportValidateRequest,
    session: Session = Depends(get_db),
) -> Report:
    report = session.query(Report).filter(Report.id == report_id).one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relato não encontrado")

    if report.is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Relato já validado")

    if payload.points > POINTS_VALIDATION_LIMIT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pontuação inválida")

    user = session.query(User).filter(User.id == report.user_id).one()
    validator = session.query(User).filter(User.id == payload.validator_id).one_or_none()
    if not validator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validador não encontrado")

    if validator.id == report.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não pode validar o próprio relato",
        )

    report.is_valid = True
    report.points_awarded = payload.points
    report.validated_at = datetime.utcnow()

    user.points += payload.points
    _award_badges(session, user)

    session.commit()
    session.refresh(report)
    return report


@router.get("/reports", response_model=List[ReportRead])
def list_reports(session: Session = Depends(get_db)) -> List[Report]:
    reports = session.query(Report).order_by(Report.created_at.desc()).all()
    return reports


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def leaderboard(session: Session = Depends(get_db), limit: int = 10) -> List[LeaderboardEntry]:
    limit = min(max(limit, 1), 50)
    users = session.query(User).order_by(User.points.desc()).limit(limit).all()

    leaderboard_entries: List[LeaderboardEntry] = []
    for user in users:
        badges = [entry.badge.name for entry in user.badges]
        leaderboard_entries.append(
            LeaderboardEntry(user_id=user.id, name=user.name, points=user.points, badges=badges)
        )
    return leaderboard_entries


@router.post("/badges", response_model=BadgeRead, status_code=status.HTTP_201_CREATED)
def create_badge(payload: BadgeCreate, session: Session = Depends(get_db)) -> Badge:
    existing = session.query(Badge).filter(Badge.points_threshold == payload.points_threshold).one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe medalha para essa pontuação")

    badge = Badge(
        name=payload.name,
        description=payload.description,
        points_threshold=payload.points_threshold,
    )
    session.add(badge)
    session.commit()
    session.refresh(badge)
    return badge


@router.get("/badges", response_model=List[BadgeRead])
def list_badges(session: Session = Depends(get_db)) -> List[Badge]:
    badges = session.query(Badge).order_by(Badge.points_threshold).all()
    return badges
