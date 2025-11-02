import uuid
from datetime import datetime, timedelta

from geoalchemy2 import Geography
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Interval,
    Float,
    String,
    Text,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import text

Base = declarative_base()


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    face_reference = Column(String(512), nullable=False)
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("points >= 0", name="ck_users_points_non_negative"),
    )

    guardian_mode = relationship("GuardianMode", back_populates="user", uselist=False)
    reports = relationship("Report", back_populates="user")
    badges = relationship("UserBadge", back_populates="user")


class GuardianMode(Base):
    __tablename__ = "guardian_modes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    active = Column(Boolean, default=False)
    activated_at = Column(DateTime)
    last_confirmation_at = Column(DateTime)
    check_interval = Column(
        Interval,
        nullable=False,
        default=timedelta(hours=6),
        server_default=text("'6 hours'::interval"),
    )
    accessibility_permission = Column(Boolean, default=False)
    lock_active = Column(Boolean, default=False)

    user = relationship("User", back_populates="guardian_mode")
    security_checks = relationship("SecurityCheck", back_populates="guardian_mode")
    locks = relationship("LockEvent", back_populates="guardian_mode")

    __table_args__ = (
        CheckConstraint(
            "check_interval > interval '0 hours'",
            name="ck_guardian_modes_check_interval_positive",
        ),
    )


class SecurityCheck(Base):
    __tablename__ = "security_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    guardian_mode_id = Column(UUID(as_uuid=True), ForeignKey("guardian_modes.id"), nullable=False)
    requested_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)
    confirmed = Column(Boolean, default=False)

    guardian_mode = relationship("GuardianMode", back_populates="security_checks")


class LockEvent(Base):
    __tablename__ = "lock_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    guardian_mode_id = Column(UUID(as_uuid=True), ForeignKey("guardian_modes.id"), nullable=False)
    locked_at = Column(DateTime, default=datetime.utcnow)
    unlocked_at = Column(DateTime)
    reason = Column(String(255))

    guardian_mode = relationship("GuardianMode", back_populates="locks")


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_cameras_latitude_range"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_cameras_longitude_range"),
    )


class LightingSpot(Base):
    __tablename__ = "lighting_spots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_lighting_latitude_range"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_lighting_longitude_range"),
    )


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime)
    is_valid = Column(Boolean, default=False)
    points_awarded = Column(Integer, default=0)

    user = relationship("User", back_populates="reports")

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_reports_latitude_range"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_reports_longitude_range"),
        CheckConstraint("points_awarded >= 0", name="ck_reports_points_awarded_non_negative"),
    )


class Badge(Base):
    __tablename__ = "badges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    points_threshold = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("points_threshold"),
        CheckConstraint("points_threshold > 0", name="ck_badges_points_threshold_positive"),
    )

    awards = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("badges.id"), nullable=False)
    awarded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="awards")

    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)
