# Extractor de Guías de Remisión

Este proyecto automatiza la extracción de datos de guías de remisión en formato PDF y su registro en un archivo Excel. Ahora incluye una **interfaz gráfica moderna** para facilitar el procesamiento masivo de archivos.

## 📋 Descripción

El software escanea las dos primeras páginas de archivos PDF de guías de remisión para extraer información clave:

- Código del remitente
- Código del transportista
- Fecha de emisión
- Peso Bruto
- Número de Placa

Los datos extraídos se insertan en una nueva fila de un archivo Excel existente, aplicando formato específico (centrado, bordes) y creando un enlace directo al archivo fuente.

## ✨ Características

- **Interfaz Gráfica (GUI) Nueva**:
  - Diseño intuitivo y minimalista.
  - Selección de múltiples archivos PDF simultáneamente.
  - Área de carga interactiva.
  - Visualización de estado y reporte de errores.
- **Configuración Persistente**: El sistema recuerda automáticamente la ubicación de tu archivo Excel de destino.
- **Extracción de Datos Robusta**: Identificación precisa de campos mediante expresiones regulares.
- **Integración con Excel**:
  - Escritura en la primera hoja activa.
  - **Estilizado Automático**: Centrado de celdas y bordes.
  - **Hipervínculos**: Acceso rápido al PDF original desde el Excel.
- **Modularidad**: Arquitectura organizada (`gui`, `parsers`, `storage`, `config`).

## 🛠️ Requisitos del Sistema

- Windows
- Python 3.8+

## 📦 Instalación

### Opción A: Configuración Automática (Recomendada)

Simplemente ejecuta el script de configuración:

```bash
setup_env.bat
```

Esto creará el entorno virtual e instalará todas las dependencias necesarias.

### Opción B: Configuración Manual

1.  **Clonar el repositorio**:

    ```bash
    git clone https://github.com/GerardoRodr/script-guias-remision.git
    cd script-guias-remision
    ```

2.  **Crear y activar un entorno virtual**:

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Uso

### Opción 1: Interfaz Gráfica (Recomendado)

Ideal para procesar múltiples documentos de una vez.

**Método Rápido:**
Haz doble clic en el archivo `run.bat`.

**Método Manual:**

1.  Activa el entorno virtual si no lo está.
2.  Ejecuta la aplicación:
    ```bash
    python gui_main.py
    ```

**Pasos en la App:**

1.  **Configura el Excel**: Selecciona tu archivo `.xlsx` de destino (solo es necesario la primera vez).
2.  **Carga PDFs**: Haz clic en el área central o en "Seleccionar Archivos" para elegir uno o varios PDFs.
3.  **Procesa**: Presiona el botón "Procesar Archivos" y espera la confirmación.

### Opción 2: Línea de Comandos (CLI)

Útil para automatizaciones o scripts batch de un solo archivo.

Puedes usar `run.bat` pasando argumentos directos:

```bash
run.bat "ruta/al/archivo.pdf" "ruta/al/archivo.xlsx"
```

O hacerlo manualmente con Python:

```bash
python main.py "ruta/al/archivo.pdf" "ruta/al/archivo.xlsx"
```

**Ejemplo:**

```bash
python main.py "C:\Docs\Guia_001.pdf" "C:\Reportes\Guias2024.xlsx"
```

## 📂 Estructura del Proyecto

```
.
├── gui_main.py                 # Punto de entrada de la Aplicación Gráfica
├── main.py                     # Punto de entrada para Línea de Comandos
├── setup_env.bat               # Script de instalación automática
├── run.bat                     # Lanzador inteligente (GUI o CLI)
├── config.json                 # Archivo de configuración (generado automáticamente)
├── requirements.txt            # Dependencias del proyecto
├── src/
│   ├── config/                 # Módulo de configuración y persistencia
│   │   └── settings.py
│   ├── gui/                    # Componentes de la Interfaz Gráfica
│   │   ├── main_window.py
│   │   └── styles.py
│   ├── models.py               # Definición de datos (RemisionGuide)
│   ├── parsers/                # Lógica de extracción (PDFParser)
│   └── storage/                # Lógica de Excel
└── venv/                       # Entorno virtual
```

## ⚠️ Notas Importantes

- El script requiere que el archivo Excel de destino exista previamente.
- Estructura de columnas esperada en Excel: remitente, transportista, fecha, peso, (vacío), placa, link al archivo.
- Se escanean únicamente las primeras 2 páginas de cada PDF.
