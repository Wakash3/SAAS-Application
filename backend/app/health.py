from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "jwt_available": True,
        "service": "Msingi Backend API"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    import jwt
    return {
        "status": "healthy",
        "jwt_version": jwt.__version__,
        "service": "Msingi Backend API"
    }