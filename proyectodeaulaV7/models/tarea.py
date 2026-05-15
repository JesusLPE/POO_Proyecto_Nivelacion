class Tarea:
    def __init__(self, titulo, descripcion, fecha_limite, creador_email):
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_limite = fecha_limite
        self.creador_email = creador_email
        self.entregas = []   # en fase 2 se llenará

    def agregar_entrega(self, estudiante_email, archivo, fecha):
        print(f"[SIMULACIÓN] Entrega de tarea '{self.titulo}' por {estudiante_email}")
        # self.entregas.append({...})  # comentado para fase 1