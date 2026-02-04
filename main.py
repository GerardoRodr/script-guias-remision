import argparse
import sys
from src.parsers.pdf_parser import PDFParser
from src.storage.excel_db import guardar_guias

def main():
    parser = argparse.ArgumentParser(description="Extraer guías de remisión de PDF y agregarlas a Excel.")
    parser.add_argument("pdf_path", help="Ruta al archivo PDF fuente")
    parser.add_argument("excel_path", help="Ruta al archivo Excel de destino (.xlsx)")
    
    args = parser.parse_args()
    
    print(f"Procesando PDF: {args.pdf_path}")
    
    # 1. Extract Data
    pdf_parser = PDFParser()
    try:
        guides = pdf_parser.extract_guides(args.pdf_path)
    except Exception as e:
        print(f"Error durante la extracción del PDF: {e}")
        sys.exit(1)
        
    if not guides:
        print("No se encontraron guías en el PDF. Verifique el contenido o los patrones regex.")
        sys.exit(0)
        
    print(f"Se encontraron {len(guides)} guías.")
    for g in guides:
        print(f" - Remitente: {g.cod_remitente}, Transportista: {g.cod_transportista}, Fecha: {g.fecha}, Peso: {g.peso}, Placa: {g.placa}")

    # 2. Store Data
    print(f"Agregando al Excel: {args.excel_path}")
    try:
        guardar_guias(args.excel_path, guides)
    except Exception as e:
        print(f"Error actualizando el Excel: {e}")
        sys.exit(1)

    print("¡Listo!")

if __name__ == "__main__":
    main()
