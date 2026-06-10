
from models.usuarios import Estudiante, Docente, Coordinador, Administrador


class UsuarioFactory:


    @staticmethod
    def crear_usuario(rol: str, nombre: str, apellido: str, email: str,
                      password: str, **kwargs):
        rol = (rol or "").strip().lower()

        if rol == "estudiante":
            return Estudiante(
                nombre, apellido, email, password,
                kwargs.get("matricula", ""),
                kwargs.get("carrera", "")
            )

        if rol == "docente":
            return Docente(
                nombre, apellido, email, password,
                kwargs.get("especialidad", "")
            )

        if rol == "coordinador":
            return Coordinador(nombre, apellido, email, password)

        if rol == "administrador":
            return Administrador(nombre, apellido, email, password)

        raise ValueError(f"Rol de usuario no soportado: {rol}")
