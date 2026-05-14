class Tarea:
    def __init__(self, titulo, descripcion, fecha_limite, creador_email):
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_limite = fecha_limite
        self.creador_email = creador_email   # docente o admin que la creó
        self.entregas = []   # lista de {"estudiante_email": email, "archivo": path, "fecha": date}