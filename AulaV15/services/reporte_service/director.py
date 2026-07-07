"""services/reporte_service/director.py

`DirectorReportes` es una Facade: la UI solo conoce esta clase y sus
nueve métodos `construir_reporte_*`. Cada método delega en el módulo
que sabe construir ESE reporte (`reporte_docente.py`,
`reporte_coordinador.py`, etc.) — este archivo no contiene lógica de
negocio propia, solo enrutamiento, por lo que se mantiene corto sin
importar cuántos tipos de reporte existan.
"""

from __future__ import annotations

from models import Reporte
from repositories.repositorio_academico import RepositorioAcademico

from . import (
    reporte_docente,
    reporte_coordinador,
    reporte_estudiante,
    reporte_administrador,
    reporte_calificaciones,
    reporte_matriculas,
    reporte_tareas,
    reporte_promedios,
    reporte_carga,
)


class DirectorReportes:
    """Punto único de entrada para generar cualquier reporte del sistema.

    La UI nunca arma un `Reporte` a mano ni conoce cómo se calculan sus
    secciones o totales; solo instancia `DirectorReportes(repo)` y llama
    al método correspondiente a su rol.
    """

    def __init__(self, repo: RepositorioAcademico):
        self._repo = repo

    def construir_reporte_docente(self, docente_email: str) -> Reporte:
        return reporte_docente.construir(self._repo, docente_email)

    def construir_reporte_coordinador(self) -> Reporte:
        return reporte_coordinador.construir(self._repo)

    def construir_reporte_estudiante(self, estudiante_email: str) -> Reporte:
        return reporte_estudiante.construir(self._repo, estudiante_email)

    def construir_reporte_administrador(self) -> Reporte:
        return reporte_administrador.construir(self._repo)

    def construir_reporte_calificaciones_por_asignatura(self) -> Reporte:
        return reporte_calificaciones.construir(self._repo)

    def construir_reporte_estado_matriculas(self) -> Reporte:
        return reporte_matriculas.construir(self._repo)

    def construir_reporte_tareas(self) -> Reporte:
        return reporte_tareas.construir(self._repo)

    def construir_reporte_promedios_estudiantes(self) -> Reporte:
        return reporte_promedios.construir(self._repo)

    def construir_reporte_carga_asignaturas(self) -> Reporte:
        return reporte_carga.construir(self._repo)
