class Tarea:
    def __init__(self, titulo, descripcion, fecha_limite, creador_email,
                 id=None, entregas=None, asignatura_id=None):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_limite = fecha_limite
        self.creador_email = creador_email
        self.entregas = entregas or []
        self.asignatura_id = asignatura_id  # vincula tarea a asignatura específica

    def agregar_entrega(self, estudiante_email, archivo, fecha, descripcion=""):
        entrega = {"estudiante_email": estudiante_email, "archivo": archivo,
                   "fecha": fecha, "descripcion": descripcion, "estado": "Realizada"}
        self.entregas.append(entrega)
        return entrega
