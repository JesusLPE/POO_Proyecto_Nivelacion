import json, os
from models.interfaces import IRepositorio


# POO: Clase | Herencia: implementa IRepositorio
# POO: Polimorfismo con interfaces -> puede sustituirse por cualquier otra
# implementación de IRepositorio (ej. una futura versión con base de datos)
# SOLID -> DIP – implementación concreta de IRepositorio usando JSON.
class JsonManager(IRepositorio):
    """DIP – implementación concreta de IRepositorio usando JSON."""

    # POO: Método (implementación concreta del contrato IRepositorio)
    def cargar(self, ruta: str) -> list:
        # Soporta rutas relativas respecto al paquete `AulaV13` cuando el
        # proceso se ejecuta desde otro directorio (por ejemplo VSCode root).
        ruta_abs = ruta
        if not os.path.isabs(ruta):
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            ruta_abs = os.path.normpath(os.path.join(base, ruta))
        if not os.path.exists(ruta_abs):
            return []
        with open(ruta_abs, "r", encoding="utf-8") as f:
            return json.load(f)

    def guardar(self, ruta: str, datos: list) -> None:
        ruta_abs = ruta
        if not os.path.isabs(ruta):
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            ruta_abs = os.path.normpath(os.path.join(base, ruta))
        os.makedirs(os.path.dirname(ruta_abs), exist_ok=True)
        with open(ruta_abs, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
