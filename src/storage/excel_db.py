from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Side
from src.models import RemisionGuide
from typing import List

def guardar_guias(ruta_excel: str, lista_guias: List[RemisionGuide]):
    try:
        libro = load_workbook(ruta_excel)
        hoja = libro.active
        
        for guia in lista_guias:
            # Insertamos en el orden exacto de tu imagen:
            # 1. Remitente | 2. Transportista | 3. Fecha | 4. Peso | 5. Sacos (VACÍO) | 6. Placa | 7. Ruta del archivo PDF
            hoja.append([
                guia.cod_remitente,     # Columna A
                guia.cod_transportista, # Columna B
                guia.fecha,             # Columna C
                guia.peso,              # Columna D
                "",                     # Columna E (Sacos - Lo dejamos vacío)
                guia.placa,             # Columna F
                guia.ruta_archivo       # Columna G (ruta del archivo PDF)
            ])

            # 2. Convertimos esa celda de texto en un HIPERVÍNCULO real
            ultima_fila = hoja.max_row
            
            # Centramos el contenido y añadimos bordes
            alineacion_centro = Alignment(horizontal='center', vertical='center')
            borde_delgado = Border(left=Side(style='thin'), 
                                   right=Side(style='thin'), 
                                   top=Side(style='thin'), 
                                   bottom=Side(style='thin'))

            for i in range(1, 8):
                celda = hoja.cell(row=ultima_fila, column=i)
                celda.alignment = alineacion_centro
                celda.border = borde_delgado

            celda_link = hoja.cell(row=ultima_fila, column=7)
            
            # Asignamos el destino del link (el archivo) y el estilo visual
            celda_link.hyperlink = guia.ruta_archivo
            celda_link.style = "Hyperlink"  # Esto lo pone azul y subrayado automáticamente
            celda_link.alignment = alineacion_centro
            celda_link.border = borde_delgado
            
        libro.save(ruta_excel)
        print(f"Fila insertada: {guia.cod_remitente} / {guia.cod_transportista}")
        
    except FileNotFoundError:
        print(f"Error: No existe el archivo {ruta_excel}")
    except PermissionError:
        print(f"Error: Cierra el Excel antes de ejecutar el script.")