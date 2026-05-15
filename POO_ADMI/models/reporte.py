from datetime import datetime

class Reporte:
    def __init__(self, tipo: str, formato: str = "PDF"):
        self._fecha_generacion = datetime.now()
        self._tipo = tipo
        self._formato = formato
        self._datos = []

    def generar(self, datos):
        self._datos = datos
        return f"[SIMULACIÓN] Reporte {self._tipo} generado con {len(datos)} registros"

    def exportar_archivo(self, nombre_archivo: str):
        print(f"[SIMULACIÓN] Exportando reporte a {nombre_archivo}")

    def enviar_por_correo(self, destinatario):
        print(f"[SIMULACIÓN] Enviando reporte por correo a {destinatario.email}")