from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sqrt
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Camera, LightingSpot
from ..schemas import (
    CameraCreate,
    FeatureResponse,
    LightingCreate,
    RouteSuggestionResponse,
)

router = APIRouter(prefix="/safety", tags=["Safety Planning"])


@dataclass
class GeoFeature:
    id: UUID
    name: str
    description: str | None
    latitude: float
    longitude: float

    def to_response(self) -> FeatureResponse:
        return FeatureResponse(
            id=self.id,
            name=self.name,
            description=self.description,
            latitude=self.latitude,
            longitude=self.longitude,
        )


def _point_from_latlon(latitude: float, longitude: float) -> WKTElement:
    return WKTElement(f"POINT({longitude} {latitude})", srid=4326)


def _distance(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    """Approximate distance between two lat/lon points in meters (Haversine simplified)."""

    # Using a simplified equirectangular approximation for short distances
    lat_rad = radians((a_lat + b_lat) / 2.0)
    x = (radians(b_lon - a_lon)) * cos(lat_rad)
    y = radians(b_lat - a_lat)
    earth_radius = 6371000
    return sqrt(x * x + y * y) * earth_radius


def _feature_from_model(model) -> GeoFeature:
    return GeoFeature(
        id=model.id,
        name=model.name,
        description=model.description,
        latitude=model.latitude,
        longitude=model.longitude,
    )


def _coverage_score(cameras: List[GeoFeature], lighting_spots: List[GeoFeature]) -> float:
    if not cameras and not lighting_spots:
        return 0.0
    return min(1.0, (len(cameras) * 0.6 + len(lighting_spots) * 0.4) / 10)


@router.post("/cameras", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
def register_camera(payload: CameraCreate, session: Session = Depends(get_db)) -> FeatureResponse:
    camera = Camera(
        name=payload.name,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location=_point_from_latlon(payload.latitude, payload.longitude),
    )
    session.add(camera)
    session.commit()
    session.refresh(camera)
    return _feature_from_model(camera).to_response()


@router.post("/lighting", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
def register_lighting(payload: LightingCreate, session: Session = Depends(get_db)) -> FeatureResponse:
    lighting = LightingSpot(
        name=payload.name,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location=_point_from_latlon(payload.latitude, payload.longitude),
    )
    session.add(lighting)
    session.commit()
    session.refresh(lighting)
    return _feature_from_model(lighting).to_response()


@router.get("/cameras", response_model=List[FeatureResponse])
def list_cameras(session: Session = Depends(get_db)) -> List[FeatureResponse]:
    cameras = session.query(Camera).order_by(Camera.created_at.desc()).all()
    return [_feature_from_model(camera).to_response() for camera in cameras]


@router.get("/lighting", response_model=List[FeatureResponse])
def list_lighting(session: Session = Depends(get_db)) -> List[FeatureResponse]:
    spots = session.query(LightingSpot).order_by(LightingSpot.created_at.desc()).all()
    return [_feature_from_model(spot).to_response() for spot in spots]


@router.get("/route", response_model=RouteSuggestionResponse)
def suggest_route(
    origin_latitude: float = Query(..., alias="origin_lat"),
    origin_longitude: float = Query(..., alias="origin_lng"),
    destination_latitude: float = Query(..., alias="destination_lat"),
    destination_longitude: float = Query(..., alias="destination_lng"),
    radius_meters: float = Query(250, ge=50, le=1000),
    session: Session = Depends(get_db),
) -> RouteSuggestionResponse:
    origin = (origin_latitude, origin_longitude)
    destination = (destination_latitude, destination_longitude)

    cameras = session.query(Camera).all()
    lighting_spots = session.query(LightingSpot).all()

    def within_radius(feature: GeoFeature) -> bool:
        return (
            _distance(feature.latitude, feature.longitude, *origin) <= radius_meters
            or _distance(feature.latitude, feature.longitude, *destination) <= radius_meters
        )

    camera_features = [_feature_from_model(camera) for camera in cameras]
    lighting_features = [_feature_from_model(spot) for spot in lighting_spots]

    filtered_cameras = [feature.to_response() for feature in camera_features if within_radius(feature)]
    filtered_lighting = [feature.to_response() for feature in lighting_features if within_radius(feature)]

    score = _coverage_score(
        [feature for feature in camera_features if within_radius(feature)],
        [feature for feature in lighting_features if within_radius(feature)],
    )

    return RouteSuggestionResponse(
        cameras=filtered_cameras,
        lighting_spots=filtered_lighting,
        coverage_score=round(score, 2),
    )
