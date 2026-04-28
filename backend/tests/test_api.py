"""
Comprehensive test suite for ReliefSync-AI API.
Tests all endpoints, AI services, and edge cases.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import json

# Mock Firebase before importing app
with patch("firebase_admin.initialize_app"), \
     patch("firebase_admin.firestore.client"), \
     patch("firebase_admin.auth.verify_id_token") as mock_verify:
    mock_verify.return_value = {
        "uid": "test-user-123",
        "email": "test@reliefsync.ai",
        "role": "admin",
    }
    from app.main import app

client = TestClient(app)

# ── Fixtures ────────────────────────────────────────────────────

MOCK_USER = {
    "uid": "test-user-123",
    "email": "test@reliefsync.ai",
    "role": "admin",
    "verified": True,
    "display_name": "Test Admin",
    "skills": [],
}

AUTH_HEADER = {"Authorization": "Bearer mock-firebase-token"}


# ── Health Check Tests ──────────────────────────────────────────

class TestHealthCheck:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "ReliefSync-AI"
        assert "version" in data
        assert "google_services" in data

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data

    def test_openapi_schema(self):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert schema["info"]["title"] == "ReliefSync-AI API"


# ── Schema Validation Tests ────────────────────────────────────

class TestSchemaValidation:
    def test_emergency_create_valid(self):
        """Test valid emergency creation schema."""
        from app.models.schemas import EmergencyCreate, GeoLocation
        emergency = EmergencyCreate(
            title="Flood in Mumbai",
            description="Heavy flooding in western suburbs due to monsoon",
            emergency_type="flood",
            location=GeoLocation(latitude=19.076, longitude=72.877, city="Mumbai"),
            affected_people=500,
        )
        assert emergency.title == "Flood in Mumbai"
        assert emergency.location.latitude == 19.076

    def test_emergency_create_invalid_title(self):
        """Test that short titles are rejected."""
        from app.models.schemas import EmergencyCreate, GeoLocation
        with pytest.raises(Exception):
            EmergencyCreate(
                title="Hi",  # Too short
                description="Description must be at least 10 characters long",
                emergency_type="flood",
                location=GeoLocation(latitude=19.0, longitude=72.0),
            )

    def test_geolocation_bounds(self):
        """Test GeoLocation latitude/longitude validation."""
        from app.models.schemas import GeoLocation
        with pytest.raises(Exception):
            GeoLocation(latitude=200, longitude=72.0)  # Invalid lat

    def test_volunteer_match_score_bounds(self):
        """Test match score is bounded 0-100."""
        from app.models.schemas import VolunteerMatch
        match = VolunteerMatch(
            volunteer_id="v1", display_name="Test",
            match_score=85.5, skill_match=90.0,
            distance_km=5.2, availability="available",
            trust_score=75.0, languages=["en", "hi"],
            reasoning="Good skill match",
        )
        assert 0 <= match.match_score <= 100

    def test_user_email_validation(self):
        """Test email normalization."""
        from app.models.schemas import UserCreate
        user = UserCreate(
            email="Test@Example.COM",
            display_name="Test User",
            skills=["first_aid"],
        )
        assert user.email == "test@example.com"


# ── AI Service Tests ────────────────────────────────────────────

class TestAIServices:
    def test_fallback_severity_prediction(self):
        """Test deterministic fallback when Gemini is unavailable."""
        from app.services.gemini_service import _fallback_severity_prediction
        result = _fallback_severity_prediction("earthquake", 500)
        assert result["severity"] == "critical"
        assert result["confidence_score"] == 0.6
        assert result["ai_model"] == "fallback_heuristic"

    def test_fallback_severity_low(self):
        from app.services.gemini_service import _fallback_severity_prediction
        result = _fallback_severity_prediction("other", 5)
        assert result["severity"] == "low"

    def test_fallback_demand_prediction(self):
        """Test WHO-standard resource predictions."""
        from app.services.gemini_service import _fallback_demand_prediction
        result = _fallback_demand_prediction("flood", 1000, 48)
        assert len(result) == 4
        water = next(r for r in result if r["resource_type"] == "water")
        assert water["predicted_quantity"] == 40000  # 1000 * 20 * 2 days
        assert water["urgency"] == "immediate"

    def test_fallback_severity_high_affected(self):
        """Test severity escalation for high affected count."""
        from app.services.gemini_service import _fallback_severity_prediction
        result = _fallback_severity_prediction("other", 200)
        assert result["severity"] == "critical"


# ── Security Tests ──────────────────────────────────────────────

class TestSecurity:
    def test_unauthenticated_access_blocked(self):
        """Endpoints requiring auth should return 401/403."""
        response = client.get("/api/v1/emergencies/")
        assert response.status_code in (401, 403)

    def test_rate_limiter_logic(self):
        """Test rate limiter allows and blocks correctly."""
        from app.core.security import RateLimiter
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        assert not limiter.is_rate_limited("192.168.1.1")
        assert not limiter.is_rate_limited("192.168.1.1")
        assert not limiter.is_rate_limited("192.168.1.1")
        assert limiter.is_rate_limited("192.168.1.1")  # 4th request blocked
        assert not limiter.is_rate_limited("192.168.1.2")  # Different IP ok


# ── Enum Tests ──────────────────────────────────────────────────

class TestEnums:
    def test_all_emergency_types(self):
        from app.models.schemas import EmergencyType
        types = [e.value for e in EmergencyType]
        assert "flood" in types
        assert "earthquake" in types
        assert "medical" in types
        assert len(types) == 10

    def test_all_roles(self):
        from app.models.schemas import UserRole
        roles = [r.value for r in UserRole]
        assert "admin" in roles
        assert "volunteer" in roles
        assert "citizen" in roles
        assert "ngo_manager" in roles
        assert "government" in roles

    def test_task_statuses(self):
        from app.models.schemas import TaskStatus
        statuses = [s.value for s in TaskStatus]
        assert "pending" in statuses
        assert "completed" in statuses
        assert "escalated" in statuses


# ── Edge Case Tests ─────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_skills_list(self):
        from app.models.schemas import UserCreate
        user = UserCreate(email="a@b.com", display_name="Test")
        assert user.skills == []

    def test_max_priority_task(self):
        from app.models.schemas import TaskCreate
        task = TaskCreate(
            emergency_id="e1", title="Critical rescue op",
            description="Urgent", priority=5,
        )
        assert task.priority == 5

    def test_invalid_priority_rejected(self):
        from app.models.schemas import TaskCreate
        with pytest.raises(Exception):
            TaskCreate(
                emergency_id="e1", title="Bad priority",
                description="Invalid", priority=10,
            )

    def test_haversine_distance(self):
        """Test geospatial distance calculation."""
        from app.routers.volunteers import _haversine
        # Mumbai to Delhi ~1150 km
        dist = _haversine(19.076, 72.877, 28.613, 77.209)
        assert 1050 < dist < 1250
