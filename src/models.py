from dataclasses import dataclass

@dataclass
class RemisionGuide:
    """Clase que representa una guía de remisión."""
    cod_remitente: str      # Columna A (ej: EG07-...)
    cod_transportista: str  # Columna B (ej: EG03-...)
    fecha: str              # Columna C
    peso: float             # Columna D
    placa: str              # Columna F (Saltamos la E "Sacos" pq no se usa)
    ruta_archivo: str       # Columna G (ruta del archivo PDF)

    def to_row(self):
        """Retorna la fila como lista para insertar en Excel."""
        return [self.cod_remitente, self.cod_transportista, self.fecha, self.peso, self.placa, self.ruta_archivo]
