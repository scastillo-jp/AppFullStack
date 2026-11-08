from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import create_tables
from app.controllers.producto_controller import router as producto_router
from app.controllers.auth_controller import router as auth_router

app = FastAPI(lifespan=create_tables)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_headers="*"
)

app.include_router(producto_router)
app.include_router(auth_router)
