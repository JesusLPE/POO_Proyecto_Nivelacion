from __future__ import annotations
from typing import Optional, List
from models.interfaces import ICalificable


# ── Asignatura ────────────────────────────────────────────────────────────────
class Asignatura:
    """SRP – solo describe una asignatura."""
    def __init__(self, id: int, nombre: str, horas: int, creditos: int, estado: str):
        self.__id = id
        self.__nombre = nombre
        self.__horas = horas
        self.__creditos = creditos
        self.__estado = estado

    @property
    def id(self) -> int: return self.__id
    @property
    def nombre(self) -> str: return self.__nombre
    @property
    def horas(self) -> int: return self.__horas
    @property
    def creditos(self) -> int: return self.__creditos
    @property
    def estado(self) -> str: return self.__estado
    @estado.setter
    def estado(self, v: str): self.__estado = v

    def __repr__(self) -> str: return f"Asignatura({self.__nombre})"


# ── Horario ────────────────────────────────────────────────────────────────────
class Horario:
    """SRP – solo encapsula un bloque horario."""
    def __init__(self, id: int, dia: str, hora_inicio: str, hora_fin: str, aula: str = ""):
        self._id = id
        self._dia = dia
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin
        self._aula = aula

    @property
    def id(self) -> int: return self._id
    @property
    def dia(self) -> str: return self._dia
    @property
    def hora_inicio(self) -> str: return self._hora_inicio
    @property
    def hora_fin(self) -> str: return self._hora_fin
    @property
    def aula(self) -> str: return self._aula

    def __str__(self) -> str:
        return f"{self._dia} {self._hora_inicio}–{self._hora_fin}"


# ── Modalidad ──────────────────────────────────────────────────────────────────
class Modalidad:
    """SRP – solo encapsula la modalidad de un curso."""
    def __init__(self, id: int, nombre: str, descripcion: str, estado: bool, plataforma: str = ""):
        self._id = id
        self._nombre = nombre
        self._descripcion = descripcion
        self._estado = estado
        self._plataforma = plataforma

    @property
    def id(self) -> int: return self._id
    @property
    def nombre(self) -> str: return self._nombre
    @property
    def plataforma(self) -> str: return self._plataforma

    def __str__(self) -> str: return self._nombre


# ── Curso ──────────────────────────────────────────────────────────────────────
class Curso:
    """SRP – representa un curso con su horario, modalidad y docente."""
    def __init__(self, id: int, nombre: str, duracion_semanas: int,
                 total_horas: int, carrera: str = ""):
        self._id = id
        self._nombre = nombre
        self._duracion_semanas = duracion_semanas
        self._total_horas = total_horas
        self._horario: Optional[Horario] = None
        self._modalidad: Optional[Modalidad] = None
        self.docente_email: Optional[str] = None
        self.carrera: str = carrera

    @property
    def id(self) -> int: return self._id
    @property
    def nombre(self) -> str: return self._nombre
    @property
    def horario(self) -> Optional[Horario]: return self._horario
    @property
    def modalidad(self) -> Optional[Modalidad]: return self._modalidad

    def asignar_horario(self, horario: Horario) -> None: self._horario = horario
    def asignar_modalidad(self, modalidad: Modalidad) -> None: self._modalidad = modalidad
    def asignar_docente(self, email: str) -> None: self.docente_email = email

    def __repr__(self) -> str: return f"Curso({self._nombre})"


# ── Matricula ──────────────────────────────────────────────────────────────────
class Matricula:
    """SRP – vincula un estudiante a una asignatura en un estado dado."""
    def __init__(self, id: int, fecha: str, tipo: str, estado: str,
                 es_segunda: bool, estudiante=None, asignatura: Optional[Asignatura] = None):
        self.__id = id
        self.__fecha = fecha
        self.__tipo = tipo
        self.__estado = estado
        self.__es_segunda = es_segunda
        self.estudiante = estudiante
        self.asignatura = asignatura

    @property
    def id(self) -> int: return self.__id
    @property
    def fecha(self) -> str: return self.__fecha
    @property
    def tipo(self) -> str: return self.__tipo
    @property
    def estado(self) -> str: return self.__estado
    @estado.setter
    def estado(self, v: str): self.__estado = v
    @property
    def esSegundaMatricula(self) -> bool: return self.__es_segunda

    def anular(self) -> None: self.__estado = "Anulada"
    def activar(self) -> None: self.__estado = "Activa"
    def verificarGratuidad(self) -> bool: return not self.__es_segunda


# ── Tarea ──────────────────────────────────────────────────────────────────────
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

    def entregada_por(self, email: str) -> bool:
        return any(e["estudiante_email"] == email and e["estado"] == "Realizada"
                   for e in self.entregas)


# ── Calificacion ───────────────────────────────────────────────────────────────
class Calificacion(ICalificable):
    """SRP+LSP – extiende ICalificable con lógica real."""
    def __init__(self, estudiante, asignatura_nombre: str,
                 nota: float, observacion: str = ""):
        self.estudiante = estudiante
        self.asignatura = asignatura_nombre
        self.nota = nota
        self.observacion = observacion

    def calcularPromedio(self, notas: list) -> float:
        return sum(notas) / len(notas) if notas else 0.0

    def esta_aprobado(self) -> bool:
        return self.nota is not None and self.nota >= 7.0

    def modificar_nota(self, nueva: float) -> None: self.nota = nueva


# ── Notas (sobrecarga de promedio) ─────────────────────────────────────────────
class Notas:
    """Demuestra sobrecarga de método con parámetro opcional."""
    @staticmethod
    def calcularPromedio(nota1: float, nota2: float, nota3: float = 0.0) -> float:
        if nota3 == 0.0:
            return round((nota1 + nota2) / 2, 2)
        return round((nota1 + nota2 + nota3) / 3, 2)

    @staticmethod
    def estado(promedio: float) -> str:
        if promedio >= 9.0:  return "Sobresaliente"
        if promedio >= 7.0:  return "Aprobado"
        if promedio >= 5.0:  return "En recuperación"
        return "Reprobado"


# ── Evaluacion abstracta (polimorfismo) ────────────────────────────────────────
from abc import ABC, abstractmethod
from datetime import date

class Evaluacion(ABC):
    """OCP – nueva modalidad de evaluación = nueva subclase, sin tocar las existentes."""
    def __init__(self, id: int, tipo: str, fecha: date, ponderacion: float):
        self._id = id
        self._tipo = tipo
        self._fecha = fecha
        self._ponderacion = ponderacion

    @abstractmethod
    def calcular_promedio(self, notas: list) -> float: pass

    @property
    def tipo(self) -> str: return self._tipo
    @property
    def ponderacion(self) -> float: return self._ponderacion


class Examen(Evaluacion):
    def __init__(self, id: int, fecha: date, ponderacion: float = 0.6):
        super().__init__(id, "Examen", fecha, ponderacion)

    def calcular_promedio(self, notas: list) -> float:
        return round(sum(notas) / len(notas) * self._ponderacion, 2) if notas else 0.0


class TrabajoPractico(Evaluacion):
    def __init__(self, id: int, fecha: date, ponderacion: float = 0.4):
        super().__init__(id, "Trabajo Práctico", fecha, ponderacion)

    def calcular_promedio(self, notas: list) -> float:
        return round(sum(notas) / len(notas) * self._ponderacion, 2) if notas else 0.0
