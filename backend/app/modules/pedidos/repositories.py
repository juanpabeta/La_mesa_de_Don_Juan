"""Consultas ORM de comandas y operaciones atómicas de persistencia."""

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from app.modules.mesas.models import Mesa
from app.modules.pedidos.models import Pedido


class PedidoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_if_table_available(self, pedido: Pedido) -> Pedido | None:
        """Persiste una comanda y ocupa su mesa en una sola transacción."""
        try:
            result = self.db.execute(
                update(Mesa)
                .where(Mesa.id == pedido.mesa_id, Mesa.estado == "LIBRE")
                .values(estado="OCUPADA")
            )
            if result.rowcount != 1:
                self.db.rollback()
                return None
            self.db.add(pedido)
            self.db.commit()
            self.db.refresh(pedido)
            return pedido
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, pedido_id: int) -> Pedido | None:
        return self.db.scalar(
            select(Pedido)
                .where(Pedido.id == pedido_id, Pedido.eliminado_en.is_(None))
            .options(selectinload(Pedido.detalles), selectinload(Pedido.mesa))
        )

    def list_for_tickets(self, states: tuple[str, ...]) -> list[Pedido]:
        return list(
            self.db.scalars(
                select(Pedido)
                .where(Pedido.estado.in_(states), Pedido.eliminado_en.is_(None))
                .options(selectinload(Pedido.detalles), selectinload(Pedido.mesa))
                .order_by(Pedido.creado_en)
                .limit(1_000)
            )
        )

    def save(self, pedido: Pedido) -> Pedido:
        self.db.add(pedido)
        self.db.commit()
        self.db.refresh(pedido)
        return pedido

    def mark_deleted(self, pedido: Pedido, *, deleted_by_id: int, deleted_at: datetime) -> None:
        pedido.eliminado_por_id = deleted_by_id
        pedido.eliminado_en = deleted_at
        self.db.add(pedido)
        self.db.commit()

    def has_active_for_table(self, mesa_id: int, active_states: tuple[str, ...]) -> bool:
        statement = select(Pedido.id).where(
            Pedido.mesa_id == mesa_id,
            Pedido.estado.in_(active_states),
            Pedido.eliminado_en.is_(None),
        ).limit(1)
        return self.db.scalar(statement) is not None

    def mark_delayed(
        self,
        pedido_ids: list[int],
        active_states: tuple[str, ...],
        marked_at: datetime,
    ) -> int:
        if not pedido_ids:
            return 0
        result = self.db.execute(
            update(Pedido)
            .where(
                Pedido.id.in_(pedido_ids),
                Pedido.estado.in_(active_states),
                Pedido.retrasado.is_(False),
            )
            .values(retrasado=True, retraso_marcado_en=marked_at)
        )
        self.db.commit()
        return result.rowcount or 0
