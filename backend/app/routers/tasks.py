"""
Task Management API Router.
Handles task creation, assignment, status tracking, and completion workflows.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timezone
import uuid
import structlog

from ..core.security import get_current_user, require_role
from ..core.supabase import get_supabase_client
from ..models.schemas import TaskCreate, TaskResponse, TaskStatus

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    current_user: dict = Depends(require_role(["admin", "ngo_manager", "government"])),
):
    """Create a new task linked to an emergency."""
    db = get_firestore_client()
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "id": task_id, "emergency_id": task.emergency_id,
        "title": task.title, "description": task.description,
        "status": TaskStatus.PENDING.value, "priority": task.priority,
        "required_skills": task.required_skills,
        "assigned_volunteers": [], "max_volunteers": task.max_volunteers,
        "location": task.location.model_dump() if task.location else None,
        "resource_requirements": task.resource_requirements,
        "estimated_duration_hours": task.estimated_duration_hours,
        "created_at": now, "created_by": current_user.get("uid"),
        "completed_at": None,
    }
    db.collection("tasks").document(task_id).set(doc)
    return TaskResponse(**doc)


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    emergency_id: str = Query(None),
    status: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    """List tasks with optional filters."""
    db = get_firestore_client()
    query = db.collection("tasks")
    if emergency_id:
        query = query.where("emergency_id", "==", emergency_id)
    if status:
        query = query.where("status", "==", status)
    query = query.order_by("priority").limit(limit)
    return [TaskResponse(**d.to_dict()) for d in query.stream()]


@router.post("/{task_id}/assign/{volunteer_id}")
async def assign_volunteer(
    task_id: str, volunteer_id: str,
    current_user: dict = Depends(require_role(["admin", "ngo_manager"])),
):
    """Assign a volunteer to a task."""
    db = get_firestore_client()
    task_ref = db.collection("tasks").document(task_id)
    task_doc = task_ref.get()
    if not task_doc.exists:
        raise HTTPException(404, "Task not found")

    task_data = task_doc.to_dict()
    assigned = task_data.get("assigned_volunteers", [])
    if volunteer_id in assigned:
        raise HTTPException(400, "Volunteer already assigned")
    if len(assigned) >= task_data.get("max_volunteers", 1):
        raise HTTPException(400, "Task has reached maximum volunteers")

    assigned.append(volunteer_id)
    task_ref.update({
        "assigned_volunteers": assigned,
        "status": TaskStatus.ASSIGNED.value,
    })

    # Update volunteer status
    db.collection("users").document(volunteer_id).update({"status": "on_task"})
    return {"message": "Volunteer assigned", "task_id": task_id}


@router.patch("/{task_id}/complete")
async def complete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Mark a task as completed."""
    db = get_firestore_client()
    task_ref = db.collection("tasks").document(task_id)
    task_doc = task_ref.get()
    if not task_doc.exists:
        raise HTTPException(404, "Task not found")

    now = datetime.now(timezone.utc).isoformat()
    task_ref.update({
        "status": TaskStatus.COMPLETED.value,
        "completed_at": now,
    })

    # Free up volunteers and increment their completed count
    task_data = task_doc.to_dict()
    for vid in task_data.get("assigned_volunteers", []):
        vol_ref = db.collection("users").document(vid)
        vol_doc = vol_ref.get()
        if vol_doc.exists:
            vd = vol_doc.to_dict()
            vol_ref.update({
                "status": "available",
                "tasks_completed": vd.get("tasks_completed", 0) + 1,
                "trust_score": min(100, vd.get("trust_score", 50) + 2),
            })

    return {"message": "Task completed", "task_id": task_id}
