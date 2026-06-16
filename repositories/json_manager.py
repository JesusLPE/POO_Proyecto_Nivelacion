import json, os
from models.interfaces import IRepositorio


class JsonManager(IRepositorio):
    """DIP – implementación concreta de IRepositorio usando JSON."""

    def cargar(self, ruta: str) -> list:
        if not os.path.exists(ruta):
            return []
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)

    def guardar(self, ruta: str, datos: list) -> None:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
