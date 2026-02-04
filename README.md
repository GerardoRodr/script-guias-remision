# Script de Procesamiento de Guías de Remisión

Este proyecto automatiza la extracción de datos de guías de remisión en formato PDF y su registro en un archivo Excel.

## 📋 Descripción

El script escanea las dos primeras páginas de un archivo PDF de guías de remisión para extraer información clave como el código del remitente, código del transportista, fecha, peso y número de placa. Una vez extraídos, estos datos se insertan en una nueva fila de un archivo Excel existente, aplicando formato específico (centrado, bordes y enlace al archivo fuente).

## ✨ Características

- **Extracción de Datos**: Utiliza expresiones regulares para identificar y extraer:
  - Código de Remitente (e.g., "N° EG07 - ...")
  - Código de Transportista
  - Fecha de emisión
  - Peso Bruto
  - Número de Placa
- **Integración con Excel**:
  - Inserta los datos extraídos en la primera hoja activa.
  - **Formato Automático**: Centra el contenido de las celdas y añade bordes delgados.
  - **Hipervínculo**: Crea un enlace funcional en la última columna que apunta al archivo PDF procesado.
- **Modularidad**: Código organizado en módulos para fácil mantenimiento (`parsers`, `storage`, `models`).

## 🛠️ Requisitos del Sistema

- Windows (Probado en este entorno)
- Python 3.8+

## 📦 Instalación

1.  **Clonar el repositorio**:

    ```bash
    git clone https://github.com/GerardoRodr/script-guias-remision.git
    cd script-guias-remision
    ```

2.  **Crear y activar un entorno virtual (Opcional pero recomendado)**:

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Uso

Ejecuta el script principal proporcionando la ruta del PDF a procesar y la ruta del archivo Excel donde guardar los datos.

```bash
python main.py "ruta/al/archivo.pdf" "ruta/al/archivo.xlsx"
```

### Ejemplo

```bash
python main.py "C:\Documentos\Guia_001.pdf" "C:\Reportes\Reporte_Guias.xlsx"
```

Si el archivo Excel no existe, el script mostrará un error. Asegúrate de tener una plantilla de Excel creada previamente.

## 📂 Estructura del Proyecto

```
.
├── main.py                     # Punto de entrada del script
├── requirements.txt            # Dependencias del proyecto
├── run.bat                     # Script batch para ejecución rápida
├── src/
│   ├── models.py               # Definición de la clase de datos (RemisionGuide)
│   ├── parsers/
│   │   └── pdf_parser.py       # Lógica de extracción de texto y regex sobre PDFs
│   └── storage/
│       └── excel_db.py         # Lógica para manipulación y guardado en Excel
└── venv/                       # Entorno virtual (no incluido en control de versiones)
```

## ⚠️ Notas Importantes

- El script asume que el archivo Excel ya existe y tiene una estructura compatible con las columnas esperadas (A: Remitente, B: Transportista, C: Fecha, D: Peso, E: Vacío, F: Placa, G: Archivo).
- Se escanean solo las primeras 2 páginas del PDF.
