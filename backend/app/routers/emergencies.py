"""
Emergency Management API Router.
Handles emergency CRUD and AI-powered severity prediction.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime, timezone
import uuid
import structlog

from ..core.security import get_current_user, require_role
from ..core.supabase import get_supabase_client
from ..models.schemas import (
    EmergencyCreate, EmergencyResponse, EmergencySeverity,
    DemandPredictionRequest, DemandPredictionResponse,
)
from ..services.gemini_service import predict_crisis_severity, predict_resource_demand

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/emergencies", tags=["Emergencies"])


@router.post("/", response_model=EmergencyResponse, status_code=201)
async def create_emergency(
    emergency: EmergencyCreate,
    current_user: dict = Depends(get_current_user),
):
    """Report a new emergency with AI severity prediction."""
    db = get_firestore_client()
    emergency_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    ai_prediction = None
    severity = emergency.severity
    if severity is None:
        ai_prediction = await predict_crisis_severity(
            emergency.emergency_type.value, emergency.description,
            emergency.affected_people, emergency.location.model_dump(),
        )
        severity = EmergencySeverity(ai_prediction["severity"])

    doc = {
        "id": emergency_id, "title": emergency.title,
        "description": emergency.description,
        "emergency_type": emergency.emergency_type.value,
        "severity": severity.value,
        "ai_severity_score": (ai_prediction or {}).get("confidence_score"),
        "ai_severity_reasoning": (ai_prediction or {}).get("reasoning"),
        "location": emergency.location.model_dump(),
        "affected_people": emergency.affected_people,
        "reported_by": current_user.get("uid"), "status": "active",
        "created_at": now, "updated_at": now,
        "assigned_volunteers": 0, "resources_deployed": [],
        "image_urls": emergency.image_urls,
    }
    db.collection("emergencies").document(emergency_id).set(doc)

    if severity in (EmergencySeverity.CRITICAL, EmergencySeverity.HIGH):
        db.collection("escalations").add({
            "emergency_id": emergency_id, "severity": severity.value,
            "escalated_at": now, "acknowledged": False,
        })

    return EmergencyResponse(**doc)


@router.get("/", response_model=list[EmergencyResponse])
async def list_emergencies(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    """List emergencies with filters."""
    db = get_firestore_client()
    query = db.collection("emergencies")
    if status_filter and status_filter != "all":
        query = query.where("status", "==", status_filter)
    if severity:
        query = query.where("severity", "==", severity)
    query = query.order_by("created_at", direction="DESCENDING").limit(limit)
    return [EmergencyResponse(**d.to_dict()) for d in query.stream()]


@router.get("/{emergency_id}", response_model=EmergencyResponse)
async def get_emergency(emergency_id: str, current_user: dict = Depends(get_current_user)):
    """Get emergency details."""
    db = get_firestore_client()
    doc = db.collection("emergencies").document(emergency_id).get()
    if not doc.exists:
        raise HTTPException(404, "Emergency not found")
    return EmergencyResponse(**doc.to_dict())


@router.patch("/{emergency_id}/status")
async def update_status(
    emergency_id: str,
    new_status: str = Query(...),
    current_user: dict = Depends(require_role(["admin", "ngo_manager", "government"])),
):
    """Update emergency status (admin/NGO/gov only)."""
    db = get_firestore_client()
    ref = db.collection("emergencies").document(emergency_id)
    if not ref.get().exists:
        raise HTTPException(404, "Emergency not found")
    ref.update({"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()})
    return {"message": f"Status updated to {new_status}"}


@router.post("/{emergency_id}/predict-demand", response_model=DemandPredictionResponse)
async def predict_demand(
    emergency_id: str, request: DemandPredictionRequest,
    current_user: dict = Depends(require_role(["admin", "ngo_manager", "government"])),
):
    """AI-powered resource demand prediction."""
    db = get_firestore_client()
    doc = db.collection("emergencies").document(emergency_id).get()
    if not doc.exists:
        raise HTTPException(404, "Emergency not found")
    data = doc.to_dict()
    predictions = await predict_resource_demand(
        data.get("emergency_type"), data.get("severity"),
        data.get("affected_people", 100), request.prediction_hours, [],
    )
    return DemandPredictionResponse(
        emergency_id=emergency_id, predictions=predictions,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
