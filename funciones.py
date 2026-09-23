"""Funciones reutilizables para la gestion del catalogo de libros.

Este modulo separa la logica de negocio (carga, validacion, busqueda,
indicadores y graficos) de la ejecucion principal que vive en main.py.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

ARCHIVO_DATOS = "datos.json"
ARCHIVO_GRAFICO = "libros_por_genero.png"

CAMPOS = ["titulo", "autor", "genero", "anio", "precio", "calificacion", "paginas", "stock"]


def cargar_catalogo(archivo: str) -> list[dict[str, Any]]:
    """Lee el catalogo desde un JSON y devuelve una lista de diccionarios.

    Si algun libro no tiene id, se le asigna uno automaticamente. Si el
    archivo no existe o no es valido, devuelve una lista vacia.
    """
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


def _completar_ids(datos: list[Any]) -> list[dict[str, Any]]:
    """Asigna ids unicos a los libros que no los tengan."""
    catalogo: list[dict[str, Any]] = []
    ids_presentes = [
        libro["id"] for libro in datos
        if isinstance(libro, dict) and isinstance(libro.get("id"), int)
    ]
    siguiente = (max(ids_presentes) + 1) if ids_presentes else 1
    for libro in datos:
        if not isinstance(libro, dict):
            continue
        if not isinstance(libro.get("id"), int):
            libro["id"] = siguiente
            siguiente += 1
        catalogo.append(libro)
    return catalogo


def guardar_catalogo(catalogo: list[dict[str, Any]], archivo: str) -> None:
    """Guarda el catalogo en un archivo JSON con formato legible."""
    try:
        with open(archivo, "w", encoding="utf-8") as archivo_json:
            json.dump(catalogo, archivo_json, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"Error al guardar en '{archivo}': {error}")


def validar_libro(libro: dict[str, Any]) -> None:
    """Valida los datos de un libro y lanza ValueError si algo no es correcto."""
    anio_actual = datetime.now().year

    if not str(libro["titulo"]).strip():
        raise ValueError("El titulo no puede estar vacio.")
    if not str(libro["autor"]).strip():
        raise ValueError("El autor no puede estar vacio.")
    if not str(libro["genero"]).strip():
        raise ValueError("El genero no puede estar vacio.")

    try:
        anio = int(libro["anio"])
    except (ValueError, TypeError):
        raise ValueError("El anio debe ser un numero entero.")
    if anio < 1000 or anio > anio_actual:
        raise ValueError(f"El anio debe estar entre 1000 y {anio_actual}.")

    try:
        precio = float(libro["precio"])
    except (ValueError, TypeError):
        raise ValueError("El precio debe ser un numero.")
    if precio < 0:
        raise ValueError("El precio no puede ser negativo.")

    try:
        calificacion = float(libro["calificacion"])
    except (ValueError, TypeError):
        raise ValueError("La calificacion debe ser un numero.")
    if not 0 <= calificacion <= 5:
        raise ValueError("La calificacion debe estar entre 0 y 5.")

    try:
        paginas = int(libro["paginas"])
    except (ValueError, TypeError):
        raise ValueError("Las paginas deben ser un numero entero.")
    if paginas <= 0:
        raise ValueError("Las paginas deben ser un numero positivo.")

    try:
        stock = int(libro["stock"])
    except (ValueError, TypeError):
        raise ValueError("El stock debe ser un numero entero.")
    if stock < 0:
        raise ValueError("El stock no puede ser negativo.")


def siguiente_id(catalogo: list[dict[str, Any]]) -> int:
    """Devuelve el proximo id disponible para un nuevo libro."""
    if not catalogo:
        return 1
    return max(libro.get("id", 0) for libro in catalogo) + 1


def agregar_libro(catalogo: list[dict[str, Any]], libro: dict[str, Any]) -> None:
    """Valida y agrega un libro al catalogo, asignandole un id unico."""
    libro_limpio = {
        "id": siguiente_id(catalogo),
        "titulo": str(libro["titulo"]).strip(),
        "autor": str(libro["autor"]).strip(),
        "genero": str(libro["genero"]).strip(),
        "anio": int(libro["anio"]),
        "precio": float(libro["precio"]),
        "calificacion": float(libro["calificacion"]),
        "paginas": int(libro["paginas"]),
        "stock": int(libro["stock"]),
    }
    try:
        validar_libro(libro_limpio)
    except ValueError as error:
        print(f"Libro no agregado: {error}")
        return
    catalogo.append(libro_limpio)
    print(f"Libro '{libro_limpio['titulo']}' agregado con id {libro_limpio['id']}.")


def eliminar_libro(catalogo: list[dict[str, Any]], id_libro: int) -> None:
    """Elimina del catalogo el libro con el id indicado."""
    for i, libro in enumerate(catalogo):
        if libro.get("id") == id_libro:
            eliminado = catalogo.pop(i)
            print(f"Libro '{eliminado['titulo']}' (id {eliminado['id']}) eliminado.")
            return
    print(f"No se encontro un libro con id {id_libro}.")


def modificar_libro(catalogo: list[dict[str, Any]], id_libro: int, campo: str, valor: Any) -> None:
    """Modifica un campo del libro indicado, validando que el resultado siga siendo valido."""
    if campo not in CAMPOS:
        print(f"Campo invalido. Campos disponibles: {', '.join(CAMPOS)}.")
        return

    for libro in catalogo:
        if libro.get("id") == id_libro:
            copia = dict(libro)
            copia[campo] = valor
            try:
                validar_libro(copia)
            except ValueError as error:
                print(f"No se modifico: {error}")
                return
            libro[campo] = valor
            print(f"Libro '{libro['titulo']}' (id {libro['id']}) actualizado ({campo} = {valor}).")
            return
    print(f"No se encontro un libro con id {id_libro}.")


def buscar_por_id(catalogo: list[dict[str, Any]], id_libro: int) -> dict[str, Any] | None:
    """Devuelve el libro con el id indicado, o None si no existe."""
    for libro in catalogo:
        if libro.get("id") == id_libro:
            return libro
    return None


def buscar_por_genero(catalogo: list[dict[str, Any]], genero: str) -> list[dict[str, Any]]:
    """Devuelve los libros cuyo genero coincide (sin distinguir mayusculas)."""
    genero = genero.strip().lower()
    return [libro for libro in catalogo if libro["genero"].lower() == genero]


def buscar_por_autor(catalogo: list[dict[str, Any]], autor: str) -> list[dict[str, Any]]:
    """Devuelve los libros cuyo autor contiene el texto buscado."""
    autor = autor.strip().lower()
    return [libro for libro in catalogo if autor in libro["autor"].lower()]


def filtrar_por_anio(catalogo: list[dict[str, Any]], anio_min: int, anio_max: int) -> list[dict[str, Any]]:
    """Devuelve los libros publicados dentro del rango de anios."""
    return [libro for libro in catalogo if anio_min <= libro["anio"] <= anio_max]


def calcular_indicadores(catalogo: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcula indicadores utiles sobre el catalogo."""
    if not catalogo:
        return {}

    total = len(catalogo)
    promedio_calificacion = sum(libro["calificacion"] for libro in catalogo) / total
    promedio_anio = sum(libro["anio"] for libro in catalogo) / total
    valor_total_stock = sum(libro["precio"] * libro["stock"] for libro in catalogo)
    mas_calificado = max(catalogo, key=lambda libro: libro["calificacion"])
    libros_por_genero: dict[str, int] = {}
    for libro in catalogo:
        libros_por_genero[libro["genero"]] = libros_por_genero.get(libro["genero"], 0) + 1

    return {
        "total_libros": total,
        "promedio_calificacion": round(promedio_calificacion, 2),
        "promedio_anio": round(promedio_anio, 1),
        "valor_total_stock": valor_total_stock,
        "mas_calificado": mas_calificado["titulo"],
        "libros_por_genero": libros_por_genero,
    }


def generar_grafico(catalogo: list[dict[str, Any]], archivo_salida: str) -> None:
    """Genera un grafico de barras con la cantidad de libros por genero."""
    import matplotlib.pyplot as plt

    if not catalogo:
        print("No hay datos para graficar.")
        return

    generos: dict[str, int] = {}
    for libro in catalogo:
        generos[libro["genero"]] = generos.get(libro["genero"], 0) + 1

    plt.figure(figsize=(8, 5))
    plt.bar(generos.keys(), generos.values(), color="steelblue")
    plt.title("Cantidad de libros por genero")
    plt.xlabel("Genero")
    plt.ylabel("Cantidad")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(archivo_salida)
    plt.close()
    print(f"Grafico guardado en '{archivo_salida}'.")


def mostrar_catalogo(catalogo: list[dict[str, Any]]) -> None:
    """Imprime el catalogo en formato de tabla simple."""
    if not catalogo:
        print("El catalogo esta vacio.")
        return
    print(f"\n{'Id':>3} {'Titulo':<28} {'Autor':<24} {'Genero':<16} {'Anio':>5} {'Precio':>8} {'Calif.':>6} {'Stock':>5}")
    print("-" * 108)
    for libro in catalogo:
        print(
            f"{libro['id']:>3} {libro['titulo']:<28} {libro['autor']:<24} {libro['genero']:<16} "
            f"{libro['anio']:>5} {libro['precio']:>8.0f} {libro['calificacion']:>6.1f} {libro['stock']:>5}"
        )
    print("-" * 108)
    print(f"Total: {len(catalogo)} libros\n")
