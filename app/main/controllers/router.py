from fastapi import APIRouter
from .migration_controller import router as migration
from .authentification_controller import router as auth
from .user_controller import router as user
from .storage_controller import router as storage
from . canaux_reception_courriers_controller import router as canaux_reception

api_router = APIRouter()

api_router.include_router(migration)
api_router.include_router(auth)
api_router.include_router(user)
api_router.include_router(storage)
api_router.include_router( canaux_reception)

# api_router. include_router(renouvellement)

