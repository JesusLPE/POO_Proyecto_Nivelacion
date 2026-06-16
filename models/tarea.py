from typing import Optional, List


class Tarea:
    """SRP – representa una tarea con sus entregas."""

    def __init__(self, id: int, titulo: str, descripcion: str,
                 fecha_limite: str, creador_email: str,
                 asignatura_id: Optional[int] = None,
                 entregas: Optional[List[dict]] = None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_limite = fecha_limite
        self.creador_email = creador_email
        self.asignatura_id = asignatura_id   # None = visible a todos
        self.entregas: List[dict] = entregas or []

    def agregar_entrega(self, estudiante_email: str, descripcion: str,
                        archivo: str, fecha: str) -> dict:
        entrega = {"estudiante_email": estudiante_email, "descripcion": descripcion,
                   "archivo": archivo, "fecha": fecha, "estado": "Realizada"}
        self.entregas.append(entrega)
        return entrega

    def entregada_por(self, email):
        return any(e["estudiante_email"] == email and e["estado"] == "Realizada"
                   for e in self.entregas)
