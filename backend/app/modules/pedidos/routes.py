"""Rutas de pedidos."""
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.modules.mesas.models import Mesa
from app.modules.menu.models import Plato
from app.modules.pedidos.models import DetallePedido, Pedido
from app.modules.pedidos.schemas import PedidoCreate, PedidoEstado, PedidoRead, PedidoUpdate, PropinaUpdate
from app.modules.usuarios.models import Usuario
from app.modules.incidencias.models import IncidenciaPedido
from app.core.realtime import realtime
from app.core.printer import print_ticket

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


async def serialize_pedido(db: AsyncSession, pedido: Pedido) -> dict[str, object]:
    """Construye el contrato completo sin consultas N+1 por cada detalle."""
    mesa = await db.get(Mesa, pedido.id_mesa)
    usuario = await db.get(Usuario, pedido.id_usuario)
    ids_platos = list({detalle.id_plato for detalle in pedido.detalles})
    platos = {}
    if ids_platos:
        platos = {
            plato.id_plato: plato
            for plato in (await db.scalars(select(Plato).where(Plato.id_plato.in_(ids_platos)))).all()
        }
    return {
        "id_pedido": pedido.id_pedido,
        "id_mesa": pedido.id_mesa,
        "numero_mesa": mesa.numero_mesa if mesa else pedido.id_mesa,
        "id_usuario": pedido.id_usuario,
        "mesero": f"{usuario.nombres} {usuario.apellidos}" if usuario else None,
        "estado": pedido.estado,
        "fecha_hora_creacion": pedido.fecha_hora_creacion,
        "fecha_hora_entrega": pedido.fecha_hora_entrega,
        "es_retrasado": pedido.es_retrasado,
        "propina": pedido.propina,
        "detalles": [
            {
                "id_detalle": detalle.id_detalle,
                "id_plato": detalle.id_plato,
                "nombre": platos[detalle.id_plato].nombre if detalle.id_plato in platos else "Producto",
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "observaciones": detalle.observaciones,
            }
            for detalle in pedido.detalles
        ],
    }


@router.post("", response_model=PedidoRead)
async def create_pedido(data: PedidoCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Mesero", "Administrador"]))):
    """Crea una comanda y ocupa atómicamente la mesa."""
    mesa = await db.scalar(select(Mesa).where(Mesa.id_mesa == data.id_mesa, Mesa.activa.is_(True)).with_for_update())
    if not mesa or mesa.estado != "Disponible":
        raise HTTPException(409, "La mesa no está disponible")
    platos = {p.id_plato: p for p in (await db.scalars(select(Plato).where(Plato.id_plato.in_([d.id_plato for d in data.detalles]), Plato.activo.is_(True), Plato.agotado.is_(False)))).all()}
    if len(platos) != len({d.id_plato for d in data.detalles}):
        raise HTTPException(400, "Uno o más platos no existen o están inactivos")
    pedido = Pedido(id_mesa=mesa.id_mesa, id_usuario=current_user.id_usuario)
    pedido.detalles = [DetallePedido(id_plato=d.id_plato, cantidad=d.cantidad, precio_unitario=platos[d.id_plato].precio, observaciones=d.observaciones) for d in data.detalles]
    mesa.estado = "Ocupada"
    db.add(pedido)
    await db.commit()
    await db.refresh(pedido)
    await realtime.broadcast("order.created", {"id_pedido": pedido.id_pedido, "id_mesa": pedido.id_mesa})
    try:
        lines = [f"LA MESA DE DON JUAN  #{pedido.id_pedido}", f"Mesa {mesa.numero_mesa}"]
        lines.extend(f"{detalle.cantidad}x {platos[detalle.id_plato].nombre}" for detalle in pedido.detalles)
        await print_ticket(lines)
    except Exception:
        db.add(IncidenciaPedido(id_pedido=pedido.id_pedido, id_usuario=current_user.id_usuario, tipo_error="Falla de impresora", descripcion="No fue posible imprimir el ticket inicial"))
        await db.commit()
    return await serialize_pedido(db, pedido)


@router.get("", response_model=list[PedidoRead])
async def list_pedidos(db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """Lista las comandas con su detalle completo."""
    pedidos = list((await db.scalars(select(Pedido).order_by(Pedido.fecha_hora_creacion.desc()))).all())
    return [await serialize_pedido(db, pedido) for pedido in pedidos]


@router.put("/{pedido_id}", response_model=PedidoRead)
async def update_pedido(pedido_id: int, data: PedidoUpdate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Mesero", "Administrador"]))):
    """Reemplaza los detalles de un pedido pendiente y valida sus platos."""
    pedido = await db.scalar(
        select(Pedido)
        .where(Pedido.id_pedido == pedido_id)
        .with_for_update()
    )
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.estado != "PENDIENTE":
        raise HTTPException(
            status_code=409,
            detail="Solo se pueden actualizar pedidos pendientes",
        )

    ids_platos = {detalle.id_plato for detalle in data.detalles}
    platos = {
        plato.id_plato: plato
        for plato in (
            await db.scalars(
                select(Plato).where(
                    Plato.id_plato.in_(ids_platos),
                    Plato.activo.is_(True),
                    Plato.agotado.is_(False),
                )
            )
        ).all()
    }
    if len(platos) != len(ids_platos):
        raise HTTPException(
            status_code=400,
            detail="Uno o más platos no existen o están inactivos",
        )

    pedido.detalles = [
        DetallePedido(
            id_plato=detalle.id_plato,
            cantidad=detalle.cantidad,
            precio_unitario=platos[detalle.id_plato].precio,
            observaciones=detalle.observaciones,
        )
        for detalle in data.detalles
    ]
    await db.commit()
    await db.refresh(pedido)
    await realtime.broadcast("order.updated", {"id_pedido": pedido.id_pedido})
    return await serialize_pedido(db, pedido)


@router.get("/tickets", response_model=list[PedidoRead])
async def impresion_tickets(db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Cocina", "Cocinero", "Administrador"]))):
    """Lista todas las columnas activas del KDS."""
    pedidos = list((await db.scalars(select(Pedido).where(Pedido.estado.in_(["PENDIENTE", "EN_PREPARACION", "LISTO"])).order_by(Pedido.fecha_hora_creacion))).all())
    return [await serialize_pedido(db, pedido) for pedido in pedidos]


@router.patch("/{pedido_id}/propina", response_model=PedidoRead)
async def update_propina(pedido_id: int, data: PropinaUpdate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador", "Mesero", "Cajero"]))):
    """Persiste la propina en pesos colombianos sin decimales."""
    pedido = await db.scalar(select(Pedido).where(Pedido.id_pedido == pedido_id).with_for_update())
    if pedido is None:
        raise HTTPException(404, "Pedido no encontrado")
    pedido.propina = data.propina.quantize(Decimal("1"))
    await db.commit()
    await db.refresh(pedido)
    await realtime.broadcast("order.updated", {"id_pedido": pedido.id_pedido})
    return await serialize_pedido(db, pedido)


@router.patch("/{pedido_id}/estado", response_model=PedidoRead)
async def update_estado(pedido_id: int, data: PedidoEstado, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador", "Mesero", "Cocina", "Cocinero"]))):
    """Aplica transiciones válidas de estado."""
    pedido = await db.scalar(select(Pedido).where(Pedido.id_pedido == pedido_id).with_for_update())
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    allowed = {"PENDIENTE": {"EN_PREPARACION", "CANCELADO"}, "EN_PREPARACION": {"LISTO", "CANCELADO"}, "LISTO": {"ENTREGADO"}, "ENTREGADO": set(), "CANCELADO": set()}
    if data.estado not in allowed.get(pedido.estado, set()):
        raise HTTPException(409, "Transición de estado no permitida")
    if data.estado == "CANCELADO" and ("Administrador" not in {r.nombre for r in current_user.roles} or not data.causa):
        raise HTTPException(403, "Cancelar requiere rol Administrador y causa")
    if data.estado == "CANCELADO":
        db.add(IncidenciaPedido(id_pedido=pedido.id_pedido, id_usuario=current_user.id_usuario, tipo_error="Anulacion autorizada", descripcion=data.causa or ""))
    pedido.estado = data.estado
    if data.estado in {"ENTREGADO", "CANCELADO"}:
        pedido.fecha_hora_entrega = datetime.now(timezone.utc)
        mesa = await db.get(Mesa, pedido.id_mesa)
        if mesa:
            mesa.estado = "Disponible"
    await db.commit()
    await db.refresh(pedido)
    await realtime.broadcast("order.updated", {"id_pedido": pedido.id_pedido, "estado": pedido.estado})
    return await serialize_pedido(db, pedido)


@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pedido(pedido_id: int, causa: str | None = None, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_roles(["Administrador"]))):
    """Cancela un pedido y conserva la auditoría de la operación."""
    pedido = await db.scalar(select(Pedido).where(Pedido.id_pedido == pedido_id))
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.estado in {"ENTREGADO", "CANCELADO"}:
        raise HTTPException(status_code=409, detail="El pedido ya no se puede cancelar")
    if not causa or not causa.strip():
        raise HTTPException(status_code=400, detail="La causa es obligatoria")

    pedido = await db.scalar(select(Pedido).where(Pedido.id_pedido == pedido_id).with_for_update())
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    pedido.estado = "CANCELADO"
    mesa = await db.get(Mesa, pedido.id_mesa)
    if mesa:
        mesa.estado = "Disponible"
    db.add(IncidenciaPedido(
        id_pedido=pedido.id_pedido,
        id_usuario=current_user.id_usuario,
        tipo_error="Cancelación administrativa",
        descripcion=causa.strip(),
    ))
    await db.commit()
    await realtime.broadcast("order.updated", {"id_pedido": pedido.id_pedido, "estado": "CANCELADO"})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{pedido_id}/reimprimir", response_model=PedidoRead)
async def reimprimir_pedido(pedido_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """Reimprime sin revertir el pedido si la impresora falla."""
    pedido = await db.get(Pedido, pedido_id)
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    mesa = await db.get(Mesa, pedido.id_mesa)
    try:
        lines = [f"LA MESA DE DON JUAN  #{pedido.id_pedido}", f"Mesa {mesa.numero_mesa if mesa else pedido.id_mesa}"]
        for detalle in pedido.detalles:
            plato = await db.get(Plato, detalle.id_plato)
            lines.append(f"{detalle.cantidad}x {plato.nombre if plato else 'Producto'}")
        await print_ticket(lines)
    except Exception:
        db.add(IncidenciaPedido(id_pedido=pedido.id_pedido, id_usuario=current_user.id_usuario, tipo_error="Falla de impresora", descripcion="No fue posible reimprimir el ticket"))
        await db.commit()
        raise HTTPException(status_code=503, detail="La impresora no está disponible; la incidencia quedó registrada")
    return await serialize_pedido(db, pedido)

