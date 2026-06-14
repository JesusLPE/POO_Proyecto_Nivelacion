"""models – Capa de dominio puro.

Cada clase vive en su propio archivo (SRP). Este __init__ las expone
todas para que repositories, services y ui puedan seguir importando
desde 'models' sin conocer la ubicación interna de cada clase.
"""

# Interfaces (ISP)
from .interfaces import IAutenticable, ICalificable, IRepositorio, INotificable

# Personas y roles (Herencia / LSP)
from .persona import Persona
from .usuarios import Estudiante, Docente, Coordinador, Administrador

# Entidades académicas
from .asignatura import Asignatura
from .horario import Horario
from .modalidad import Modalidad
from .curso import Curso
from .matricula import Matricula
from .tarea import Tarea
from .calificacion import Calificacion
from .notas import Notas

# Evaluaciones (OCP / Polimorfismo)
from .evaluacion import Evaluacion, Examen, TrabajoPractico

__all__ = [
    "IAutenticable", "ICalificable", "IRepositorio", "INotificable",
    "Persona", "Estudiante", "Docente", "Coordinador", "Administrador",
    "Asignatura", "Horario", "Modalidad", "Curso", "Matricula",
    "Tarea", "Calificacion", "Notas",
    "Evaluacion", "Examen", "TrabajoPractico",
]
