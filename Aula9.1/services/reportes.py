"""Servicio para exportar reportes generados por la interfaz."""
import json
import os
import re
from datetime import datetime


class ReporteService:
    """Crea archivos de reporte y registra un historial simple en JSON."""

    def __init__(self, carpeta_reportes="reportes", historial="data/reportes_generados.json"):
        self.carpeta_reportes = carpeta_reportes
        self.historial = historial

    def guardar(self, rol, usuario, tipo, secciones):
        os.makedirs(self.carpeta_reportes, exist_ok=True)
        os.makedirs(os.path.dirname(self.historial), exist_ok=True)

        fecha = datetime.now()
        nombre = self._nombre_archivo(rol, tipo, fecha)
        ruta = os.path.join(self.carpeta_reportes, nombre)

        with open(ruta, "w", encoding="utf-8") as f:
            f.write(f"Reporte: {tipo}\n")
            f.write(f"Rol: {rol}\n")
            f.write(f"Generado por: {usuario}\n")
            f.write(f"Fecha: {fecha.strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            for seccion in secciones:
                self._escribir_seccion(f, seccion)

        self._registrar_historial(rol, usuario, tipo, ruta, fecha)
        return ruta

    def _escribir_seccion(self, archivo, seccion):
        titulo = seccion.get("titulo", "")
        columnas = [str(c) for c in seccion.get("columnas", [])]
        filas = seccion.get("filas", [])

        if titulo:
            archivo.write(f"{titulo}\n")
            archivo.write("-" * len(titulo) + "\n")

        if columnas:
            archivo.write(" | ".join(columnas) + "\n")
            archivo.write("-" * 80 + "\n")

        if filas:
            for fila in filas:
                archivo.write(" | ".join(str(v) for v in fila) + "\n")
        else:
            archivo.write("Sin datos para este reporte.\n")
        archivo.write("\n")

    def _registrar_historial(self, rol, usuario, tipo, ruta, fecha):
        datos = []
        if os.path.exists(self.historial):
            try:
                with open(self.historial, "r", encoding="utf-8") as f:
                    datos = json.load(f)
            except (json.JSONDecodeError, OSError):
                datos = []

        datos.append({
            "rol": rol,
            "usuario": usuario,
            "tipo": tipo,
            "archivo": ruta.replace("\\", "/"),
            "fecha": fecha.strftime("%Y-%m-%d %H:%M:%S"),
        })
        with open(self.historial, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def _nombre_archivo(self, rol, tipo, fecha):
        base = f"{rol}_{tipo}_{fecha.strftime('%Y%m%d_%H%M%S')}".lower()
        base = re.sub(r"[^a-z0-9]+", "_", base).strip("_")
        return f"{base}.txt"
