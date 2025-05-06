from fastapi import APIRouter
from .migration_controller import router as migration
from .authentification_controller import router as auth
from .user_controller import router as user
from .storage_controller import router as storage
from . canaux_reception_courriers_controller import router as canaux_reception
from .formes_courriers_controller import router as formes_courriers
from .nature_courriers_controller import router as nature_courriers
from .type_courriers_controller import router as type_courriers
from .externes_controller import router as receiver
api_router = APIRouter()

api_router.include_router(migration)
api_router.include_router(auth)
api_router.include_router(user)
api_router.include_router(storage)
api_router.include_router( canaux_reception)
api_router.include_router(receiver)
api_router.include_router(formes_courriers)
api_router .include_router(nature_courriers)
api_router . include_router(type_courriers)


