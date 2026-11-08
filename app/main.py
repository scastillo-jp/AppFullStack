from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import create_tables
from app.controllers.producto_controller import router as producto_router
from app.controllers.auth_controller import router as auth_router
from app.controllers.categoria_controller import router as categoria_router
from app.controllers.carrito_controller import router as carrito_router
from app.controllers.pedido_controller import router as pedido_router
from app.controllers.usuario_controller import router as usuario_router

app = FastAPI(lifespan=create_tables)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_headers=["*"],
    allow_methods=["*"]
)

app.include_router(producto_router)
app.include_router(auth_router)
app.include_router(categoria_router)
app.include_router(carrito_router)
app.include_router(pedido_router)
app.include_router(usuario_router)
