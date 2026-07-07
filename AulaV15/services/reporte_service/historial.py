"""services/reporte_service/historial.py

Persistencia del historial de reportes generados (SRP: esta clase no
construye reportes, solo registra que uno fue generado).
"""

from __future__ import annotations

from typing import List

from models import Reporte, RegistroReporte
from repositories.repositorio_academico import RepositorioAcademico


class ReporteService:
    """Persiste un `RegistroReporte` cada vez que se genera un reporte,
    para que otros roles (Administrador) puedan consultar el historial.

    No participa en la construcción del reporte: solo la complementa.
    El flujo típico en la UI es:

        director = DirectorReportes(repo)
        reporte  = director.construir_reporte_coordinador()
        render_reporte(contenido, reporte, ...)
        ReporteService(repo).registrar_generacion(
            reporte, tipo="coordinador",
            generado_por=usuario.email, rol_generador=usuario.obtener_rol(),
        )
    """

    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def registrar_generacion(self, reporte: Reporte, tipo: str,
                             generado_por: str, rol_generador: str) -> RegistroReporte:
        nid = self._repo.siguiente_id(self._repo.reportes_generados)
        registro = RegistroReporte(
            id=nid, tipo=tipo, titulo=reporte.titulo, subtitulo=reporte.subtitulo,
            generado_por=generado_por, rol_generador=rol_generador,
            totales=list(reporte.totales), num_secciones=len(reporte.secciones),
        )
        self._repo.reportes_generados.append(registro)
        self._repo.guardar_reportes_generados()
        return registro

    def historial(self) -> List[RegistroReporte]:
        """Lista de reportes generados, más recientes primero."""
        return sorted(self._repo.reportes_generados, key=lambda r: r.fecha, reverse=True)

    def historial_de(self, rol: str) -> List[RegistroReporte]:
        return [r for r in self.historial() if r.rol_generador == rol]
