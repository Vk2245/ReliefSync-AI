"""
Supabase client initialization and management.
Replaces Firebase/Firestore for ReliefSync-AI.
"""
from supabase import create_client, Client
import structlog
from .config import get_settings

logger = structlog.get_logger(__name__)

_supabase_client: Client = None


def get_supabase_client() -> Client:
    """Get or create Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        settings = get_settings()
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        logger.info("supabase_initialized", url=settings.SUPABASE_URL)
    return _supabase_client


async def verify_supabase_token(access_token: str) -> dict:
    """
    Verify Supabase JWT token and return user data.
    Used for authenticating incoming requests.
    """
    try:
        client = get_supabase_client()
        response = client.auth.get_user(access_token)
        user = response.user
        
        if not user:
            raise ValueError("Invalid token")
        
        # Get user profile from database
        profile = client.table("users").select("*").eq("id", user.id).execute()
        
        user_data = {
            "uid": user.id,
            "email": user.email,
            "role": "citizen",
            "verified": False,
            "display_name": "",
            "skills": []
        }
        
        if profile.data and len(profile.data) > 0:
            user_profile = profile.data[0]
            user_data.update({
                "role": user_profile.get("role", "citizen"),
                "verified": user_profile.get("verified", False),
                "display_name": user_profile.get("display_name", ""),
                "skills": user_profile.get("skills", [])
            })
        
        logger.info("token_verified", uid=user.id)
        return user_data
        
    except Exception as e:
        logger.warning("invalid_token", error=str(e))
        raise ValueError("Invalid authentication token")
