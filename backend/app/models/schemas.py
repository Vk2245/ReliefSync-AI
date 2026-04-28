"""
Pydantic schemas for ReliefSync-AI API.
Defines all request/response models for type-safe API contracts.
These mirror the Firestore document structures.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


# ── Enums ───────────────────────────────────────────────────────

class UserRole(str, Enum):
    CITIZEN = "citizen"
    VOLUNTEER = "volunteer"
    NGO_MANAGER = "ngo_manager"
    ADMIN = "admin"
    GOVERNMENT = "government"


class EmergencySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EmergencyType(str, Enum):
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    FIRE = "fire"
    MEDICAL = "medical"
    ACCIDENT = "accident"
    CYCLONE = "cyclone"
    LANDSLIDE = "landslide"
    EPIDEMIC = "epidemic"
    VIOLENCE = "violence"
    OTHER = "other"


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"


class VolunteerStatus(str, Enum):
    AVAILABLE = "available"
    ON_TASK = "on_task"
    OFFLINE = "offline"
    SUSPENDED = "suspended"


class ResourceType(str, Enum):
    FOOD = "food"
    WATER = "water"
    MEDICAL_SUPPLIES = "medical_supplies"
    SHELTER = "shelter"
    CLOTHING = "clothing"
    TRANSPORT = "transport"
    COMMUNICATION = "communication"
    MANPOWER = "manpower"
    BLOOD = "blood"


# ── GeoLocation ─────────────────────────────────────────────────

class GeoLocation(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


# ── User Schemas ────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    display_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.CITIZEN
    location: Optional[GeoLocation] = None
    skills: list[str] = []
    languages: list[str] = ["en"]
    organization_id: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email address")
        return v.lower()


class UserResponse(BaseModel):
    uid: str
    email: str
    display_name: str
    role: UserRole
    verified: bool = False
    skills: list[str] = []
    languages: list[str] = ["en"]
    location: Optional[GeoLocation] = None
    created_at: Optional[str] = None
    trust_score: float = 50.0


# ── Emergency Schemas ───────────────────────────────────────────

class EmergencyCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    emergency_type: EmergencyType
    location: GeoLocation
    severity: Optional[EmergencySeverity] = None  # AI will predict if not provided
    affected_people: Optional[int] = Field(None, ge=0)
    image_urls: list[str] = []
    contact_phone: Optional[str] = None


class EmergencyResponse(BaseModel):
    id: str
    title: str
    description: str
    emergency_type: EmergencyType
    severity: EmergencySeverity
    ai_severity_score: Optional[float] = None
    ai_severity_reasoning: Optional[str] = None
    location: GeoLocation
    affected_people: Optional[int] = None
    reported_by: str
    status: str = "active"
    created_at: str
    updated_at: Optional[str] = None
    assigned_volunteers: int = 0
    resources_deployed: list[str] = []
    image_urls: list[str] = []


# ── Task Schemas ────────────────────────────────────────────────

class TaskCreate(BaseModel):
    emergency_id: str
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., max_length=2000)
    required_skills: list[str] = []
    priority: int = Field(default=3, ge=1, le=5)
    location: Optional[GeoLocation] = None
    estimated_duration_hours: Optional[float] = None
    resource_requirements: list[str] = []
    max_volunteers: int = Field(default=1, ge=1, le=100)


class TaskResponse(BaseModel):
    id: str
    emergency_id: str
    title: str
    description: str
    status: TaskStatus
    priority: int
    required_skills: list[str] = []
    assigned_volunteers: list[str] = []
    location: Optional[GeoLocation] = None
    created_at: str
    completed_at: Optional[str] = None
    ai_match_scores: Optional[dict] = None


# ── Volunteer Matching ──────────────────────────────────────────

class VolunteerMatchRequest(BaseModel):
    task_id: str
    emergency_id: str
    max_results: int = Field(default=10, ge=1, le=50)
    max_distance_km: float = Field(default=50.0, ge=1.0, le=500.0)


class VolunteerMatch(BaseModel):
    volunteer_id: str
    display_name: str
    match_score: float = Field(..., ge=0.0, le=100.0)
    skill_match: float
    distance_km: float
    availability: str
    trust_score: float
    languages: list[str]
    reasoning: str


class VolunteerMatchResponse(BaseModel):
    task_id: str
    matches: list[VolunteerMatch]
    total_available: int
    ai_model_used: str = "gemini-2.0-flash"
    processing_time_ms: float


# ── Resource Schemas ────────────────────────────────────────────

class ResourceCreate(BaseModel):
    resource_type: ResourceType
    name: str
    quantity: int = Field(..., ge=0)
    unit: str = "units"
    location: GeoLocation
    organization_id: Optional[str] = None
    expiry_date: Optional[str] = None


class ResourceResponse(BaseModel):
    id: str
    resource_type: ResourceType
    name: str
    quantity: int
    unit: str
    location: GeoLocation
    organization_id: Optional[str] = None
    created_at: str
    last_updated: str


# ── Resource Demand Prediction ──────────────────────────────────

class DemandPredictionRequest(BaseModel):
    emergency_id: str
    prediction_hours: int = Field(default=24, ge=1, le=168)


class DemandPrediction(BaseModel):
    resource_type: str
    predicted_quantity: int
    confidence: float
    reasoning: str
    urgency: str


class DemandPredictionResponse(BaseModel):
    emergency_id: str
    predictions: list[DemandPrediction]
    ai_model_used: str = "gemini-2.0-flash"
    generated_at: str


# ── Analytics Schemas ───────────────────────────────────────────

class DashboardAnalytics(BaseModel):
    total_emergencies: int
    active_emergencies: int
    total_volunteers: int
    active_volunteers: int
    tasks_completed: int
    tasks_pending: int
    avg_response_time_minutes: float
    resources_deployed: int
    top_emergency_types: list[dict]
    volunteer_utilization_percent: float
    crisis_heatmap_data: list[dict]


# ── Communication Schemas ───────────────────────────────────────

class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source_language: str = "auto"
    target_language: str = "en"


class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float


# ── Route Optimization ──────────────────────────────────────────

class RouteOptimizationRequest(BaseModel):
    origin: GeoLocation
    destinations: list[GeoLocation]
    vehicle_type: str = "car"
    optimize_for: str = "time"  # time | distance


class OptimizedRoute(BaseModel):
    waypoints: list[GeoLocation]
    total_distance_km: float
    total_duration_minutes: float
    route_polyline: Optional[str] = None
    instructions: list[str]


# ── Organization Schemas ────────────────────────────────────────

class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    org_type: str  # ngo, government, hospital, relief_agency
    description: Optional[str] = None
    contact_email: str
    contact_phone: Optional[str] = None
    location: GeoLocation
    website: Optional[str] = None
    verification_doc_url: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    org_type: str
    description: Optional[str] = None
    contact_email: str
    location: GeoLocation
    verified: bool = False
    member_count: int = 0
    created_at: str


# ── Health Check ────────────────────────────────────────────────

class HealthCheck(BaseModel):
    status: str = "healthy"
    version: str
    environment: str
    services: dict[str, str]
