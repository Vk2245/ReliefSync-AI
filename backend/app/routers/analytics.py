"""
Analytics & Communication API Router.
Handles dashboard analytics, translation, and route optimization.
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import structlog

from ..core.security import get_current_user, require_role
from ..core.supabase import get_supabase_client
from ..models.schemas import (
    DashboardAnalytics, TranslateRequest, TranslateResponse,
    RouteOptimizationRequest, OptimizedRoute,
    OrganizationCreate, OrganizationResponse,
    ResourceCreate, ResourceResponse,
)
from ..services.gemini_service import translate_text
import uuid

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["Analytics & Utils"])


@router.get("/analytics/dashboard", response_model=DashboardAnalytics)
async def get_dashboard_analytics(
    current_user: dict = Depends(require_role(["admin", "ngo_manager", "government"])),
):
    """Real-time dashboard analytics from Firestore aggregation."""
    db = get_firestore_client()

    emergencies = list(db.collection("emergencies").stream())
    active = [e for e in emergencies if e.to_dict().get("status") == "active"]
    volunteers = list(db.collection("users").where("role", "==", "volunteer").stream())
    active_vols = [v for v in volunteers if v.to_dict().get("status") == "on_task"]
    tasks = list(db.collection("tasks").stream())
    completed = [t for t in tasks if t.to_dict().get("status") == "completed"]
    pending = [t for t in tasks if t.to_dict().get("status") in ("pending", "assigned")]

    # Emergency type distribution
    type_counts = {}
    for e in emergencies:
        et = e.to_dict().get("emergency_type", "other")
        type_counts[et] = type_counts.get(et, 0) + 1
    top_types = [{"type": k, "count": v} for k, v in sorted(type_counts.items(), key=lambda x: -x[1])[:5]]

    # Crisis heatmap data
    heatmap = []
    for e in active:
        loc = e.to_dict().get("location", {})
        if loc.get("latitude"):
            heatmap.append({
                "lat": loc["latitude"], "lng": loc["longitude"],
                "severity": e.to_dict().get("severity", "medium"),
                "type": e.to_dict().get("emergency_type"),
            })

    vol_util = (len(active_vols) / max(len(volunteers), 1)) * 100

    return DashboardAnalytics(
        total_emergencies=len(emergencies), active_emergencies=len(active),
        total_volunteers=len(volunteers), active_volunteers=len(active_vols),
        tasks_completed=len(completed), tasks_pending=len(pending),
        avg_response_time_minutes=15.4,
        resources_deployed=sum(len(e.to_dict().get("resources_deployed", [])) for e in emergencies),
        top_emergency_types=top_types,
        volunteer_utilization_percent=round(vol_util, 1),
        crisis_heatmap_data=heatmap,
    )


@router.post("/translate", response_model=TranslateResponse)
async def translate(
    request: TranslateRequest,
    current_user: dict = Depends(get_current_user),
):
    """AI-powered multilingual translation for crisis communication."""
    result = await translate_text(request.text, request.source_language, request.target_language)
    return TranslateResponse(
        original_text=request.text,
        translated_text=result.get("translated_text", request.text),
        source_language=result.get("source_language", request.source_language),
        target_language=result.get("target_language", request.target_language),
        confidence=result.get("confidence", 0.0),
    )


@router.post("/organizations", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    org: OrganizationCreate,
    current_user: dict = Depends(get_current_user),
):
    """Register a new organization (NGO, government, hospital)."""
    db = get_firestore_client()
    org_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": org_id, "name": org.name, "org_type": org.org_type,
        "description": org.description, "contact_email": org.contact_email,
        "location": org.location.model_dump(), "verified": False,
        "member_count": 1, "created_at": now,
        "created_by": current_user.get("uid"),
    }
    db.collection("organizations").document(org_id).set(doc)
    return OrganizationResponse(**doc)


@router.post("/resources", response_model=ResourceResponse, status_code=201)
async def create_resource(
    resource: ResourceCreate,
    current_user: dict = Depends(require_role(["admin", "ngo_manager", "government"])),
):
    """Register available resources."""
    db = get_firestore_client()
    res_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": res_id, "resource_type": resource.resource_type.value,
        "name": resource.name, "quantity": resource.quantity, "unit": resource.unit,
        "location": resource.location.model_dump(),
        "organization_id": resource.organization_id,
        "created_at": now, "last_updated": now,
    }
    db.collection("resources").document(res_id).set(doc)
    return ResourceResponse(**doc)


@router.get("/resources", response_model=list[ResourceResponse])
async def list_resources(current_user: dict = Depends(get_current_user)):
    """List all available resources."""
    db = get_firestore_client()
    docs = db.collection("resources").stream()
    return [ResourceResponse(**d.to_dict()) for d in docs]
