"""Consultas ORM del catálogo de platos."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.menu.models import Plato


class PlatoRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, *, only_available: bool = False) -> list[Plato]:
        statement = select(Plato)
        if only_available:
            statement = statement.where(Plato.disponible.is_(True))
        return list(self.db.scalars(statement.order_by(Plato.categoria, Plato.nombre).limit(1_000)))

    def get_by_id(self, plato_id: int) -> Plato | None:
        return self.db.get(Plato, plato_id)

    def get_by_name(self, nombre: str) -> Plato | None:
        return self.db.scalar(select(Plato).where(Plato.nombre == nombre))

    def get_by_ids(self, ids: list[int]) -> list[Plato]:
        return list(self.db.scalars(select(Plato).where(Plato.id.in_(set(ids)))))

    def create(self, plato: Plato) -> Plato:
        self.db.add(plato)
        self.db.commit()
        self.db.refresh(plato)
        return plato

    def update(self, plato: Plato, changes: dict[str, object]) -> Plato:
        for field, value in changes.items():
            setattr(plato, field, value)
        self.db.commit()
        self.db.refresh(plato)
        return plato

    def deactivate(self, plato: Plato) -> Plato:
        plato.disponible = False
        self.db.commit()
        self.db.refresh(plato)
        return plato
