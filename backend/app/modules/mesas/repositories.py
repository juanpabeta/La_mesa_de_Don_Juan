"""Consultas ORM de mesas."""

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modules.mesas.models import Mesa


class MesaRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Mesa]:
        return list(self.db.scalars(select(Mesa).order_by(Mesa.numero).limit(1_000)))

    def get_by_id(self, mesa_id: int) -> Mesa | None:
        return self.db.get(Mesa, mesa_id)

    def get_by_number(self, numero: int) -> Mesa | None:
        return self.db.scalar(select(Mesa).where(Mesa.numero == numero))

    def create(self, mesa: Mesa) -> Mesa:
        self.db.add(mesa)
        self.db.commit()
        self.db.refresh(mesa)
        return mesa

    def update_status(self, mesa: Mesa, estado: str) -> Mesa:
        mesa.estado = estado
        self.db.commit()
        self.db.refresh(mesa)
        return mesa

    def set_free_if_occupied(self, mesa_id: int) -> None:
        self.db.execute(update(Mesa).where(Mesa.id == mesa_id, Mesa.estado == "OCUPADA").values(estado="LIBRE"))
        self.db.commit()

    def deactivate(self, mesa: Mesa) -> Mesa:
        mesa.estado = "INACTIVA"
        self.db.commit()
        self.db.refresh(mesa)
        return mesa
