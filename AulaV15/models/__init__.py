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

# Planificación académica
from .cronograma import Cronograma

# Retiro de materias
from .retiro import SolicitudRetiro

# Reportes (producto de services/reporte_service/ + historial persistido)
from .reporte import SeccionReporte, Reporte, RegistroReporte


__all__ = [
    # Interfaces
    "IAutenticable", "ICalificable", "IRepositorio", "INotificable",

    # Personas y roles
    "Persona", "Estudiante", "Docente", "Coordinador", "Administrador",

    # Entidades académicas
    "Asignatura", "Horario", "Modalidad", "Curso", "Matricula",
    "Tarea", "Calificacion", "Notas",

    # Evaluaciones
    "Evaluacion", "Examen", "TrabajoPractico",

    # Planificación académica
    "Cronograma",

    # Retiro de materias
    "SolicitudRetiro",

    # Reportes
    "SeccionReporte", "Reporte", "RegistroReporte",
]
