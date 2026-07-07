from services.academico import AuthService, validar_cedula_ecuatoriana


class ValidadorEstudianteMasivo:
    """Valida estructura, obligatorios y duplicados de estudiantes importados."""

    COLUMNAS_REQUERIDAS = {"nombre", "apellido", "cedula", "email", "password", "matricula", "carrera", "curso_id", "horario_id"}

    def __init__(self, repo):
        self._repo = repo
        self._auth = AuthService(repo)

    def normalizar(self, fila: dict) -> dict:
        return {str(k).strip().lower(): "" if v is None else str(v).strip() for k, v in fila.items()}

    def validar_columnas(self, filas: list[dict]) -> list[str]:
        if not filas:
            return ["El archivo está vacío"]
        columnas = {str(c).strip().lower() for c in filas[0].keys()}
        faltantes = sorted(self.COLUMNAS_REQUERIDAS - columnas)
        return [f"Falta la columna obligatoria: {c}" for c in faltantes]

    def validar_fila(self, datos: dict, cedulas_archivo: set[str], emails_archivo: set[str]) -> list[tuple[str, str]]:
        errores: list[tuple[str, str]] = []
        for campo in self.COLUMNAS_REQUERIDAS:
            if not datos.get(campo):
                errores.append((campo, "Campo obligatorio"))

        cedula = datos.get("cedula", "")
        email = datos.get("email", "")
        if cedula and not validar_cedula_ecuatoriana(cedula):
            errores.append(("cedula", "Cédula ecuatoriana inválida"))
        if cedula in cedulas_archivo:
            errores.append(("cedula", "Cédula duplicada dentro del archivo"))
        if any(getattr(e, "cedula", "") == cedula for e in self._repo.estudiantes):
            errores.append(("cedula", "Cédula ya registrada en el sistema"))

        if email and not self._auth.validar_email(email):
            errores.append(("email", "Correo inválido"))
        if email in emails_archivo:
            errores.append(("email", "Correo duplicado dentro del archivo"))
        if email and not self._auth.email_disponible(email):
            errores.append(("email", "Correo ya registrado en el sistema"))

        try:
            curso_id = int(datos.get("curso_id", 0))
            if not self._repo.curso_por_id(curso_id):
                errores.append(("curso_id", "Curso no existe"))
        except ValueError:
            errores.append(("curso_id", "Curso debe ser numérico"))

        try:
            horario_id = int(datos.get("horario_id", 0))
            if not self._repo.horario_por_id(horario_id):
                errores.append(("horario_id", "Horario no existe"))
        except ValueError:
            errores.append(("horario_id", "Horario debe ser numérico"))

        return errores
