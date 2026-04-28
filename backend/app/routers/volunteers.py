"""
Volunteer Management API Router.
Handles volunteer registration, skill matching, task assignment, and status management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timezone
import uuid
import math
import structlog

from ..core.security import get_current_user, require_role
from ..core.supabase import get_supabase_client
from ..models.schemas import (
    UserCreate, UserResponse, VolunteerMatchRequest,
    VolunteerMatchResponse, VolunteerMatch, TaskCreate, TaskResponse, TaskStatus,
)
from ..services.gemini_service import match_volunteers, detect_fraud

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/volunteers", tags=["Volunteers"])


def _haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates in km."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_volunteer(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user),
):
    """Register as a volunteer with skill verification."""
    db = get_firestore_client()
    uid = current_user.get("uid")

    # Fraud detection on registration
    fraud_check = await detect_fraud(
        {"uid": uid, "email": user_data.email, "skills": user_data.skills},
        {"action": "volunteer_registration", "location": user_data.location.model_dump() if user_data.location else None},
    )
    if fraud_check.get("recommendation") == "block":
        raise HTTPException(403, "Registration blocked due to security concerns")

    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "uid": uid, "email": user_data.email,
        "display_name": user_data.display_name,
        "phone": user_data.phone, "role": "volunteer",
        "skills": user_data.skills, "languages": user_data.languages,
        "location": user_data.location.model_dump() if user_data.location else None,
        "organization_id": user_data.organization_id,
        "verified": False, "status": "available",
        "trust_score": 50.0 - (fraud_check.get("fraud_risk_score", 0) * 0.3),
        "tasks_completed": 0, "created_at": now,
        "fraud_risk_score": fraud_check.get("fraud_risk_score", 0),
    }
    db.collection("users").document(uid).set(doc, merge=True)
    return UserResponse(**doc)


@router.get("/", response_model=list[UserResponse])
async def list_volunteers(
    status: str = Query("available"),
    skill: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(require_role(["admin", "ngo_manager", "government"])),
):
    """List volunteers (admin/NGO/gov only)."""
    db = get_firestore_client()
    query = db.collection("users").where("role", "==", "volunteer")
    if status != "all":
        query = query.where("status", "==", status)
    docs = query.limit(limit).stream()
    results = []
    for d in docs:
        data = d.to_dict()
        if skill and skill not in data.get("skills", []):
            continue
        results.append(UserResponse(**data))
    return results


@router.post("/match", response_model=VolunteerMatchResponse)
async def match_volunteers_to_task(
    request: VolunteerMatchRequest,
    current_user: dict = Depends(require_role(["admin", "ngo_manager"])),
):
    """AI-powered volunteer-task matching."""
    db = get_firestore_client()
    import time
    start = time.time()

    # Get task
    task_doc = db.collection("tasks").document(request.task_id).get()
    if not task_doc.exists:
        raise HTTPException(404, "Task not found")
    task = task_doc.to_dict()

    # Get available volunteers
    vols = db.collection("users").where("role", "==", "volunteer").where("status", "==", "available").stream()
    available = []
    task_loc = task.get("location", {})
    for v in vols:
        vd = v.to_dict()
        vol_loc = vd.get("location", {})
        if vol_loc and task_loc:
            dist = _haversine(
                vol_loc.get("latitude", 0), vol_loc.get("longitude", 0),
                task_loc.get("latitude", 0), task_loc.get("longitude", 0),
            )
            if dist <= request.max_distance_km:
                vd["distance_km"] = round(dist, 1)
                available.append(vd)
        else:
            vd["distance_km"] = 999
            available.append(vd)

    # AI matching
    ai_matches = await match_volunteers(task, available)
    matches = []
    for m in ai_matches[:request.max_results]:
        vol = next((v for v in available if v.get("uid") == m.get("volunteer_id")), {})
        matches.append(VolunteerMatch(
            volunteer_id=m.get("volunteer_id", ""),
            display_name=vol.get("display_name", "Unknown"),
            match_score=m.get("match_score", 0),
            skill_match=m.get("skill_match", 0),
            distance_km=vol.get("distance_km", 999),
            availability=vol.get("status", "unknown"),
            trust_score=vol.get("trust_score", 50),
            languages=vol.get("languages", ["en"]),
            reasoning=m.get("reasoning", ""),
        ))

    return VolunteerMatchResponse(
        task_id=request.task_id, matches=matches,
        total_available=len(available),
        processing_time_ms=round((time.time() - start) * 1000, 1),
    )


@router.patch("/{volunteer_id}/verify")
async def verify_volunteer(
    volunteer_id: str,
    current_user: dict = Depends(require_role(["admin"])),
):
    """Admin-only volunteer verification."""
    db = get_firestore_client()
    ref = db.collection("users").document(volunteer_id)
    if not ref.get().exists:
        raise HTTPException(404, "Volunteer not found")
    ref.update({"verified": True, "trust_score": 75.0})
    return {"message": "Volunteer verified", "volunteer_id": volunteer_id}
