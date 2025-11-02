from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, PositiveInt, conlist


GUARDIAN_SEQUENCE_LENGTH = 4


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    face_reference: str = Field(
        ...,
        description="Opaque token that represents the enrolled facial template.",
        min_length=1,
        max_length=512,
    )


class UserRead(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    face_reference: str
    points: int
    created_at: datetime

    class Config:
        orm_mode = True


class GuardianActivationRequest(BaseModel):
    user_id: UUID
    button_sequence: conlist(PositiveInt, min_items=GUARDIAN_SEQUENCE_LENGTH, max_items=GUARDIAN_SEQUENCE_LENGTH) = Field(
        ...,
        description="Sequência de contagem dos toques físicos no botão configurado.",
    )
    accessibility_permission_granted: bool
    check_interval_hours: Optional[int] = Field(
        None,
        ge=1,
        description="Quantidade desejada de horas entre confirmações do modo guardião.",
    )


class GuardianStatusResponse(BaseModel):
    active: bool
    lock_active: bool
    last_confirmation_at: Optional[datetime]
    next_confirmation_deadline: Optional[datetime]
    check_interval_hours: Optional[int]


class GuardianConfirmationRequest(BaseModel):
    user_id: UUID


class GuardianUnlockRequest(BaseModel):
    user_id: UUID
    face_reference: str = Field(..., min_length=1, max_length=512)


class CameraCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class LightingCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class FeatureResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    latitude: float
    longitude: float

    class Config:
        orm_mode = True


class RouteSuggestionResponse(BaseModel):
    cameras: List[FeatureResponse]
    lighting_spots: List[FeatureResponse]
    coverage_score: float = Field(..., description="Simple heuristic representing how well the path is covered.")


class ReportCreate(BaseModel):
    user_id: UUID
    description: str = Field(..., min_length=5, max_length=1000)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class ReportValidateRequest(BaseModel):
    validator_id: UUID
    points: int = Field(..., ge=0, le=100)


class ReportRead(BaseModel):
    id: UUID
    user_id: UUID
    description: str
    latitude: float
    longitude: float
    created_at: datetime
    is_valid: bool
    points_awarded: int
    validated_at: Optional[datetime]

    class Config:
        orm_mode = True


class LeaderboardEntry(BaseModel):
    user_id: UUID
    name: str
    points: int
    badges: List[str]


class BadgeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=5, max_length=1000)
    points_threshold: PositiveInt


class BadgeRead(BaseModel):
    id: UUID
    name: str
    description: str
    points_threshold: int

    class Config:
        orm_mode = True
