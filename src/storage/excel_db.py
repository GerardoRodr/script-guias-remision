from openpyxl import load_workbook
from datetime import datetime
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
            # Intentamos convertir la fecha a objeto date para que Excel la reconozca
            fecha_val = guia.fecha
            try:
                # El regex extrae dd/mm/yyyy, intentamos parsearlo
                fecha_val = datetime.strptime(guia.fecha, "%d/%m/%Y").date()
            except (ValueError, TypeError):
                pass # Si falla, se queda como string original

            hoja.append([
                guia.cod_remitente,     # Columna A
                guia.cod_transportista, # Columna B
                fecha_val,              # Columna C
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
            
            # Formato específico para la FECHA (columna 3)
            # 'dd/mm/yyyy' permite que Excel lo reconozca como fecha corta
            hoja.cell(row=ultima_fila, column=3).number_format = 'dd/mm/yyyy'

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