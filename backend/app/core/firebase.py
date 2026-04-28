"""
Firebase Admin SDK initialization and Firestore client management.
Provides singleton access to Firebase Auth and Firestore database.
"""
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore_v1 import AsyncClient
import structlog
from .config import get_settings

logger = structlog.get_logger(__name__)

_firebase_app = None
_firestore_client = None


def initialize_firebase():
    """Initialize Firebase Admin SDK with service account or ADC."""
    global _firebase_app
    if _firebase_app:
        return _firebase_app

    settings = get_settings()
    try:
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
            _firebase_app = firebase_admin.initialize_app(cred, {
                "projectId": settings.GCP_PROJECT_ID,
            })
        else:
            # Use Application Default Credentials (Cloud Run / local gcloud auth)
            _firebase_app = firebase_admin.initialize_app(options={
                "projectId": settings.GCP_PROJECT_ID,
            })
        logger.info("firebase_initialized", project_id=settings.GCP_PROJECT_ID)
        return _firebase_app
    except Exception as e:
        logger.error("firebase_init_failed", error=str(e))
        raise


def get_firestore_client():
    """Get or create Firestore client singleton."""
    global _firestore_client
    if _firestore_client is None:
        initialize_firebase()
        _firestore_client = firestore.client()
    return _firestore_client


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify Firebase ID token and return decoded claims.
    Used for authenticating incoming requests.
    """
    initialize_firebase()
    try:
        decoded_token = auth.verify_id_token(id_token)
        logger.info("token_verified", uid=decoded_token.get("uid"))
        return decoded_token
    except auth.InvalidIdTokenError:
        logger.warning("invalid_token_attempted")
        raise ValueError("Invalid authentication token")
    except auth.ExpiredIdTokenError:
        logger.warning("expired_token_attempted")
        raise ValueError("Authentication token has expired")
