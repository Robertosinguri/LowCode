# Funciones reutilizables para la gestion del catalogo de libros.

import json
import os
import sys
from contextlib import suppress
from datetime import date
from typing import Any

ARCHIVO_DATOS = "datos.json"
ARCHIVO_GRAFICO = "libros_por_genero.png"
CAMPOS = ["título", "autor", "género", "año", "precio", "calificación", "páginas", "stock"]
CAMPOS_ENTEROS = {"año", "páginas", "stock"}
CAMPOS_DECIMALES = {"precio", "calificación"}

# Fuerza UTF-8 para que los acentos se lean y muestren bien en la consola.
def configurar_utf8() -> None:
    
    if os.name == "nt":
        os.system("chcp 65001 > nul")
    for flujo in (sys.stdin, sys.stdout, sys.stderr):
        with suppress(AttributeError, ValueError):
            flujo.reconfigure(encoding="utf-8")

# Lee el catalogo desde un JSON y devuelve una lista de diccionarios.
def cargar_catalogo(archivo: str) -> list[dict[str, Any]]:

    try:
        with open(archivo, encoding="utf-8") as archivo_json:
            datos = json.load(archivo_json)
        if not isinstance(datos, list):
            print(f"Error: '{archivo}' no contiene una lista de libros.")
            return []
        return _completar_ids(datos)
    except FileNotFoundError:
        print(f"Aviso: no se encontro '{archivo}', se inicia con catalogo vacio.")
    except json.JSONDecodeError as error:
        print(f"Error al leer '{archivo}': JSON invalido ({error}).")
    return []

# Asigna ids unicos a los libros que no los tengan.
def _completar_ids(datos: list[Any]) -> list[dict[str, Any]]:

    catalogo: list[dict[str, Any]] = []

    for libro in datos:
        if not isinstance(libro, dict):
            continue
        catalogo.append(libro)
    # Se renumera siempre para que la lista quede correlativa (1, 2, 3...),
    # incluso si el archivo tenia ids faltantes o con huecos.
    renumerar(catalogo)
    return catalogo

# Guarda el catalogo en un archivo JSON con formato legible.
def guardar_catalogo(catalogo: list[dict[str, Any]], archivo: str) -> None:

    try:
        with open(archivo, "w", encoding="utf-8") as archivo_json:
            json.dump(catalogo, archivo_json, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"Error al guardar en '{archivo}': {error}")

# Valida los datos de un libro, devuelve una version limpia y lanza ValueError si algo no es correcto.
def validar_libro(libro: dict[str, Any]) -> dict[str, Any]:

    año_actual = date.today().year
    libro_limpio: dict[str, Any] = {}

    for campo in ("título", "autor", "género"):
        valor = str(libro.get(campo, "")).strip()
        if not valor:
            raise ValueError(f"El {campo} no puede estar vacio.")
        libro_limpio[campo] = valor

    try:
        año = int(libro["año"])
    except (ValueError, TypeError, KeyError):
        raise ValueError("El año debe ser un numero entero.")
    if año < 1000 or año > año_actual:
        raise ValueError(f"El año debe estar entre 1000 y {año_actual}.")
    libro_limpio["año"] = año

    try:
        precio = float(libro["precio"])
    except (ValueError, TypeError, KeyError):
        raise ValueError("El precio debe ser un numero.")
    if precio < 0:
        raise ValueError("El precio no puede ser negativo.")
    libro_limpio["precio"] = precio

    try:
        calificación = float(libro["calificación"])
    except (ValueError, TypeError, KeyError):
        raise ValueError("La calificación debe ser un numero.")
    if not 0 <= calificación <= 5:
        raise ValueError("La calificación debe estar entre 0 y 5.")
    libro_limpio["calificación"] = calificación

    try:
        páginas = int(libro["páginas"])
    except (ValueError, TypeError, KeyError):
        raise ValueError("Las páginas deben ser un numero entero.")
    if páginas <= 0:
        raise ValueError("Las páginas deben ser un numero positivo.")
    libro_limpio["páginas"] = páginas

    try:
        stock = int(libro["stock"])
    except (ValueError, TypeError, KeyError):
        raise ValueError("El stock debe ser un numero entero.")
    if stock < 0:
        raise ValueError("El stock no puede ser negativo.")
    libro_limpio["stock"] = stock

    return libro_limpio

# Reasigna los ids del catalogo como 1, 2, 3... segun el orden de la lista.
# Se usa cada vez que el catalogo cambia (agregar o eliminar) para que la
# numeracion quede siempre correlativa y sin huecos.
def renumerar(catalogo: list[dict[str, Any]]) -> None:
    for posicion, libro in enumerate(catalogo, start=1):
        libro["id"] = posicion

# Devuelve el proximo id disponible para un nuevo libro.
def siguiente_id(catalogo: list[dict[str, Any]]) -> int:
    return len(catalogo) + 1

# Valida y agrega un libro al catalogo, asignandole un id unico.
def agregar_libro(catalogo: list[dict[str, Any]], libro: dict[str, Any]) -> None:
    try:
        libro_limpio = validar_libro(libro)
    except ValueError as error:
        print(f"Libro no agregado: {error}")
        return

    libro_limpio["id"] = siguiente_id(catalogo)
    catalogo.append(libro_limpio)
    renumerar(catalogo)
    print(f"Libro '{libro_limpio['título']}' agregado con id {libro_limpio['id']}.")

# Elimina del catalogo el libro con el id indicado.
def eliminar_libro(catalogo: list[dict[str, Any]], id_libro: int) -> None:

    for i, libro in enumerate(catalogo):
        if libro.get("id") == id_libro:
            eliminado = catalogo.pop(i)
            print(f"Libro '{eliminado['título']}' (id {eliminado['id']}) eliminado.")
            renumerar(catalogo)
            return
    print(f"No se encontro un libro con id {id_libro}.")

# Modifica un campo del libro indicado, validando que el resultado siga siendo valido.
def modificar_libro(catalogo: list[dict[str, Any]], id_libro: int, campo: str, valor: Any) -> None:
    if campo not in CAMPOS:
        print(f"Campo invalido. Campos disponibles: {', '.join(CAMPOS)}.")
        return

    for libro in catalogo:
        if libro.get("id") == id_libro:
            copia = dict(libro)
            copia[campo] = valor
            try:
                copia_limpia = validar_libro(copia)
            except ValueError as error:
                print(f"No se modifico: {error}")
                return
            libro[campo] = copia_limpia[campo]
            print(f"Libro '{libro['título']}' (id {libro['id']}) actualizado ({campo} = {valor}).")
            return
    print(f"No se encontro un libro con id {id_libro}.")

#Devuelve el libro con el id indicado, o None si no existe.
def buscar_por_id(catalogo: list[dict[str, Any]], id_libro: int) -> dict[str, Any] | None:

    for libro in catalogo:
        if libro.get("id") == id_libro:
            return libro
    return None

# Devuelve los libros cuyo género coincide (sin distinguir mayúsculas).
def buscar_por_género(catalogo: list[dict[str, Any]], género: str) -> list[dict[str, Any]]:
    género = género.strip().lower()
    return [libro for libro in catalogo if libro["género"].lower() == género]

# Devuelve los libros cuyo autor contiene el texto buscado.
def buscar_por_autor(catalogo: list[dict[str, Any]], autor: str) -> list[dict[str, Any]]:
    autor = autor.strip().lower()
    return [libro for libro in catalogo if autor in libro["autor"].lower()]

 # Devuelve los libros publicados dentro del rango de años.
def filtrar_por_año(catalogo: list[dict[str, Any]], año_min: int, año_max: int) -> list[dict[str, Any]]:
    return [libro for libro in catalogo if año_min <= libro["año"] <= año_max]

# Calcula indicadores utiles sobre el catalogo.
def calcular_indicadores(catalogo: list[dict[str, Any]]) -> dict[str, Any]:

    if not catalogo:
        return {}

    total = len(catalogo)
    promedio_calificación = sum(libro["calificación"] for libro in catalogo) / total
    promedio_año = sum(libro["año"] for libro in catalogo) / total
    valor_total_stock = sum(libro["precio"] * libro["stock"] for libro in catalogo)
    mas_calificado = max(catalogo, key=lambda libro: libro["calificación"])
    libros_por_género: dict[str, int] = {}
    for libro in catalogo:
        libros_por_género[libro["género"]] = libros_por_género.get(libro["género"], 0) + 1

    return {
        "total_libros": total,
        "promedio_calificación": round(promedio_calificación, 2),
        "promedio_año": round(promedio_año, 1),
        "valor_total_stock": valor_total_stock,
        "mas_calificado": mas_calificado["título"],
        "libros_por_género": libros_por_género,
    }

# Genera un grafico de barras con la cantidad de libros por genero.
def generar_grafico(catalogo: list[dict[str, Any]], archivo_salida: str) -> None:

    import matplotlib.pyplot as plt

    if not catalogo:
        print("No hay datos para graficar.")
        return

    generos: dict[str, int] = {}
    for libro in catalogo:
        generos[libro["género"]] = generos.get(libro["género"], 0) + 1

    plt.figure(figsize=(8, 5))
    plt.bar(generos.keys(), generos.values(), color="steelblue")
    plt.title("Cantidad de libros por género")
    plt.xlabel("género")
    plt.ylabel("Cantidad")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(archivo_salida)
    plt.close()
    print(f"Grafico guardado en '{archivo_salida}'.")

#Imprime el catalogo en formato de tabla simple.
def mostrar_catalogo(catalogo: list[dict[str, Any]]) -> None:

    if not catalogo:
        print("El catalogo esta vacio.")
        return
    encabezado = (
        f"{'Id':>3} {'Titulo':<28} {'Autor':<24} {'Genero':<16} "
        f"{'Año':>5} {'Precio':>8} {'Calif.':>6} {'Stock':>5}"
    )
    ancho = len(encabezado)

    print(f"\n{encabezado}")
    print("-" * ancho)

    for libro in catalogo:
        print(
            f"{libro['id']:>3} {libro['título']:<28} {libro['autor']:<24} {libro['género']:<16} "
            f"{libro['año']:>5} {libro['precio']:>8.0f} {libro['calificación']:>6.1f} {libro['stock']:>5}"
        )
    print("-" * ancho)
    print(f"Total: {len(catalogo)} libros\n")
