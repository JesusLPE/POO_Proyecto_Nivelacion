from datetime import datetime

class Reporte:
    def __init__(self, tipo: str, formato: str = "PDF"):
        self._fecha_generacion = datetime.now()
        self._tipo = tipo
        self._formato = formato
        self._datos = []

    def generar(self, datos):
        self._datos = datos
        return f"Reporte {self._tipo} generado con {len(datos)} registros"

    def exportar_archivo(self, nombre_archivo: str):
        with open(nombre_archivo, "w") as f:
            f.write(f"Reporte: {self._tipo}\nFecha: {self._fecha_generacion}\n")
            for d in self._datos:
                f.write(str(d) + "\n")

    def enviar_por_correo(self, destinatario):
        print(f"Enviando reporte {self._tipo} a {destinatario.email}")