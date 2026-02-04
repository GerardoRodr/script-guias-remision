import re
import pdfplumber
from typing import List
from src.models import RemisionGuide

class PDFParser:
    def __init__(self):
        # 1. Regex para el CÓDIGO (Remitente y Transportista)
        # Explicación del patrón r"(N°\s*[A-Z0-9]+\s*-\s*[0-9]+)":
        #  N°       -> Busca literalmente el símbolo de grados
        #  \s* -> Acepta CUALQUIER cantidad de espacios (0, 1 o muchos)
        #  [A-Z0-9]+ -> Busca las letras y números del código (ej: EG07)
        #  \s*-\s* -> Acepta el guion con espacios a los lados (ej: " - ") <--- CORRECCIÓN CLAVE
        #  [0-9]+   -> Busca los números finales
        self.code_pattern = re.compile(r"(N°\s*[A-Z0-9]+\s*-\s*[0-9]+)")
        
        # 2. Regex para FECHA (31/01/2026)
        self.date_pattern = re.compile(r"Fecha.*?:\s*(\d{2}/\d{2}/\d{4})")
        
        # 3. Regex para PESO (32.5)
        self.weight_pattern = re.compile(r"Peso Bruto.*?:\s*([\d\.]+)")
        
        # 4. Regex para PLACA (T6A826)
        self.plate_pattern = re.compile(r"Número de placa\s*:\s*([A-Z0-9]+)")

    def extract_guides(self, file_path: str) -> List[RemisionGuide]:
        temp_data = {
            "remitente": "No encontrado",
            "transportista": "No encontrado",
            "fecha": "No encontrado",
            "peso": 0.0,
            "placa": "No encontrado"
        }

        with pdfplumber.open(file_path) as pdf:
            # Leemos las páginas 0 y 1 (las dos primeras)
            for i in range(min(2, len(pdf.pages))):
                text = pdf.pages[i].extract_text()
                if not text: continue
                
                # --- LÓGICA DE EXTRACCIÓN ---

                # Detectar si es la página del REMITENTE o TRANSPORTISTA
                # Buscamos el código ESPECÍFICO que aparece en esa página
                match_codigo = self.code_pattern.search(text)
                
                if match_codigo:
                    codigo_encontrado = match_codigo.group(1) # Captura "N° EG07 - 00000120" completo
                    
                    if "REMITENTE" in text:
                        temp_data["remitente"] = codigo_encontrado
                        print(f"✅ Remitente encontrado: {codigo_encontrado}")
                    elif "TRANSPORTISTA" in text:
                        temp_data["transportista"] = codigo_encontrado
                        print(f"✅ Transportista encontrado: {codigo_encontrado}")

                # Buscar Datos Comunes (Fecha, Peso, Placa) solo si aún no los tenemos
                if temp_data["fecha"] == "No encontrado":
                    m_fecha = self.date_pattern.search(text)
                    if m_fecha: temp_data["fecha"] = m_fecha.group(1)

                if temp_data["peso"] == 0.0:
                    m_peso = self.weight_pattern.search(text)
                    if m_peso:
                        try:
                            temp_data["peso"] = float(m_peso.group(1))
                        except:
                            temp_data["peso"] = 0.0

                if temp_data["placa"] == "No encontrado":
                    m_placa = self.plate_pattern.search(text)
                    if m_placa: temp_data["placa"] = m_placa.group(1)

        # Crear el objeto con los datos recolectados
        guia_completa = RemisionGuide(
            cod_remitente=temp_data["remitente"],
            cod_transportista=temp_data["transportista"],
            fecha=temp_data["fecha"],
            peso=temp_data["peso"],
            placa=temp_data["placa"],
            ruta_archivo=file_path
        )

        return [guia_completa]