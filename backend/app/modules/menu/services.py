"""Reglas de negocio de catálogo, tiempos base y disponibilidad comercial."""

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.modules.menu.models import Plato
from app.modules.menu.repositories import PlatoRepository


class PlatoService:
    def __init__(self, repository: PlatoRepository):
        self.repository = repository

    def list_dishes(self, *, only_available: bool) -> list[Plato]:
        return self.repository.list(only_available=only_available)

    def create_dish(self, values: dict[str, object]) -> Plato:
        name = str(values["nombre"]).strip()
        if self.repository.get_by_name(name) is not None:
            raise ConflictError("Ya existe un plato con ese nombre")
        if int(values["tiempo_preparacion_minutos"]) <= 0:
            raise BusinessRuleError("El tiempo de preparación debe ser positivo")
        values["nombre"] = name
        return self.repository.create(Plato(**values))

    def update_dish(self, dish_id: int, changes: dict[str, object]) -> Plato:
        dish = self.repository.get_by_id(dish_id)
        if dish is None:
            raise NotFoundError("No se encontró el plato")
        if not changes:
            raise BusinessRuleError("Debes indicar al menos un campo para actualizar")
        if "nombre" in changes and changes["nombre"] is not None:
            name = str(changes["nombre"]).strip()
            other = self.repository.get_by_name(name)
            if other is not None and other.id != dish.id:
                raise ConflictError("Ya existe un plato con ese nombre")
            changes["nombre"] = name
        return self.repository.update(dish, changes)

    def delete_dish(self, dish_id: int) -> Plato:
        dish = self.repository.get_by_id(dish_id)
        if dish is None:
            raise NotFoundError("No se encontró el plato")
        if not dish.disponible:
            raise BusinessRuleError("El plato ya está desactivado")
        return self.repository.deactivate(dish)
