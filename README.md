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

La instalacion tiene tres etapas. Crear el entorno virtual se hace **una sola
vez**; activarlo se hace **cada vez** que se abre una terminal nueva para
trabajar en el proyecto.

### Etapa 1: crear el entorno virtual

Desde la carpeta del proyecto, el comando es igual en todos los sistemas:

```bash
python -m venv .venv
```

Esto crea una carpeta `.venv/` con una copia aislada de Python y sus
herramientas. No hace falta repetir este paso salvo que se borre la carpeta.

### Etapa 2: activar el entorno virtual

El comando de activacion **depende de la terminal** que se use. Hay que
ejecutar el que corresponda, siempre desde la carpeta del proyecto:

**Windows - CMD (simbolo del sistema):**

```bat
.venv\Scripts\activate.bat
```

**Windows - PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

> Si PowerShell bloquea el script con un error de "politica de ejecucion",
> ejecutar una vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**Windows - Git Bash:**

```bash
source .venv/Scripts/activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

Cuando la activacion funciona, el nombre del entorno aparece al inicio del
prompt, por ejemplo: `(.venv) C:\...\LowCode>`.

### Etapa 3: instalar las dependencias

Con el entorno ya activado (y solo entonces), instalar las dependencias:

```bash
pip install -r requirements.txt
```

Para salir del entorno virtual, ejecutar `deactivate`.

## Ejecucion

Con el entorno activado y las dependencias instaladas:

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
