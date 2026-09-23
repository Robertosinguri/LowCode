# Catalogo de libros

Aplicacion en Python que permite gestionar un catalogo de libros: cargar,
agregar, validar, buscar, filtrar, calcular indicadores y generar un grafico.
Los datos se persisten en un archivo JSON.

## Objetivo

Resolver el problema de registrar, consultar y analizar un catalogo de libros,
cumpliendo la consigna del TP1 (Elementos de Programacion IA y Low Code).

## Requisitos

- Python 3.10 o superior.
- Dependencias listadas en `requirements.txt` (pandas y matplotlib).

## Instalacion

Crear y activar un entorno virtual e instalar dependencias:

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

## Ejecucion

```bash
python main.py
```

El menu permite:

1. Ver el catalogo.
2. Agregar un libro (con validacion de datos).
3. Buscar por genero.
4. Buscar por autor.
5. Filtrar por anio.
6. Ver indicadores.
7. Generar un grafico (se guarda como `libros_por_genero.png`).
8. Eliminar un libro.
9. Modificar un libro.
10. Guardar y salir.

## Analisis

La notebook `analisis.ipynb` explora los datos con pandas y produce graficos.

## Estructura del proyecto

| Archivo      | Contenido                                    |
|--------------|----------------------------------------------|
| `main.py`    | Flujo principal y menu interactivo.          |
| `funciones.py` | Funciones reutilizables (carga, validacion, busqueda, indicadores, grafico). |
| `datos.json` | Catalogo de libros inicial.                  |
| `analisis.ipynb` | Exploracion con pandas y graficos.        |
| `requirements.txt` | Dependencias externas.                |

## Decisiones principales

- Persistencia en **JSON** (formato legible y orientado a datos no relacionales).
- El nucleo de la app usa **listas y diccionarios**; **pandas** se usa en el
  analisis (notebook), como pide la consigna.
- Validacion de cada campo con `try`/`except` y `ValueError` para datos invalidos.
- El grafico principal muestra la cantidad de libros por genero.
