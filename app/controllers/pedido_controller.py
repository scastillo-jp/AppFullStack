from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from app.db.database import SessionDep
from app.dependencies.auth import CurrentAdmin, CurrentUser
from app.models.usuario import ROL_ADMINISTRADOR
from app.schemas.pedido import PedidoEstadoUpdate, PedidoRead
from app.services import pedido_service


router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("", response_model=list[PedidoRead])
def get_my_orders(current_user: CurrentUser, session: SessionDep):
    return pedido_service.get_orders(current_user.id, session)


@router.get("/admin", response_model=list[PedidoRead])
def get_all_orders(current_admin: CurrentAdmin, session: SessionDep):
    return pedido_service.get_orders(None, session)


@router.post("", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def create_order(current_user: CurrentUser, session: SessionDep):
    try:
        return pedido_service.create_order(current_user, session)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


@router.get("/{order_id}", response_model=PedidoRead)
def get_order(
    order_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    session: SessionDep
):
    user_id = None if current_user.role == ROL_ADMINISTRADOR else current_user.id
    order = pedido_service.get_order(order_id, user_id, session)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    return order


@router.patch("/{order_id}/estado", response_model=PedidoRead)
def update_order_status(
    order_id: Annotated[int, Path(gt=0)],
    status_data: PedidoEstadoUpdate,
    current_admin: CurrentAdmin,
    session: SessionDep
):
    try:
        order = pedido_service.update_order_status(
            order_id,
            status_data,
            session
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    return order
