from fastapi import FastAPI
from app.db.database import create_tables
from app.controllers.producto_controller import router as producto_router
from app.controllers.auth_controller import router as auth_router

app = FastAPI(lifespan=create_tables)

app.include_router(producto_router)
app.include_router(auth_router)
