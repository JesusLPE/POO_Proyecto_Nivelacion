from .interfaces import IEstrategiaImportacion
from .resultado import ResultadoImportacion
from .validadores import ValidadorEstudianteMasivo
from services.academico import UsuarioService


class EstrategiaImportacionEstudiantes(IEstrategiaImportacion):
    """Strategy concreta para importar estudiantes."""

    def __init__(self, repo):
        self._repo = repo
        self._usuario_service = UsuarioService(repo)
        self._validador = ValidadorEstudianteMasivo(repo)

    def importar(self, filas: list[dict]) -> ResultadoImportacion:
        resultado = ResultadoImportacion(total=len(filas))
        errores_columnas = self._validador.validar_columnas(filas)
        if errores_columnas:
            for err in errores_columnas:
                resultado.agregar_error(0, "estructura", err)
            return resultado

        cedulas_archivo: set[str] = set()
        emails_archivo: set[str] = set()
        filas_validas: list[dict] = []

        for numero_fila, fila in enumerate(filas, start=2):
            datos = self._validador.normalizar(fila)
            errores = self._validador.validar_fila(datos, cedulas_archivo, emails_archivo)
            if errores:
                for campo, mensaje in errores:
                    resultado.agregar_error(numero_fila, campo, mensaje, datos)
                continue
            cedulas_archivo.add(datos["cedula"])
            emails_archivo.add(datos["email"])
            filas_validas.append(datos)

        resultado.validos = len(filas_validas)
        for datos in filas_validas:
            ok, msg = self._usuario_service.crear_estudiante(
                datos["nombre"], datos["apellido"], datos["email"], datos["password"],
                datos["cedula"], datos["matricula"], datos["carrera"],
                curso_id=int(datos["curso_id"]), horario_id=int(datos["horario_id"]),
            )
            if ok:
                resultado.creados += 1
            else:
                resultado.agregar_error(0, "persistencia", msg, datos)
        return resultado
