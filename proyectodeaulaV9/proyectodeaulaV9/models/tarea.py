class Tarea:
    """Modelo que representa una tarea creada por un docente."""

    def __init__(self, titulo, descripcion, fecha_limite, creador_email):
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_limite = fecha_limite
        self.creador_email = creador_email
        self.entregas = []   # Lista de entregas que se completará en la fase 2.

    def agregar_entrega(self, estudiante_email, archivo, fecha):
        # Simulación de la entrega de tarea.
        print(f"[SIMULACIÓN] Entrega de tarea '{self.titulo}' por {estudiante_email}")
        # En fases posteriores se guardaría la entrega en self.entregas.
