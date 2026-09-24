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

CAMPOS = ["título", "autor", "género", "año", "precio", "calificación", "páginas", "stock"]


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
    año_actual = datetime.now().year

    if not str(libro["título"]).strip():
        raise ValueError("El título no puede estar vacio.")
    if not str(libro["autor"]).strip():
        raise ValueError("El autor no puede estar vacio.")
    if not str(libro["género"]).strip():
        raise ValueError("El género no puede estar vacio.")

    try:
        año = int(libro["año"])
    except (ValueError, TypeError):
        raise ValueError("El año debe ser un numero entero.")
    if año < 1000 or año > año_actual:
        raise ValueError(f"El año debe estar entre 1000 y {año_actual}.")

    try:
        precio = float(libro["precio"])
    except (ValueError, TypeError):
        raise ValueError("El precio debe ser un numero.")
    if precio < 0:
        raise ValueError("El precio no puede ser negativo.")

    try:
        calificación = float(libro["calificación"])
    except (ValueError, TypeError):
        raise ValueError("La calificación debe ser un numero.")
    if not 0 <= calificación <= 5:
        raise ValueError("La calificación debe estar entre 0 y 5.")

    try:
        páginas = int(libro["páginas"])
    except (ValueError, TypeError):
        raise ValueError("Las páginas deben ser un numero entero.")
    if páginas <= 0:
        raise ValueError("Las páginas deben ser un numero positivo.")

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
        "título": str(libro["título"]).strip(),
        "autor": str(libro["autor"]).strip(),
        "género": str(libro["género"]).strip(),
        "año": int(libro["año"]),
        "precio": float(libro["precio"]),
        "calificación": float(libro["calificación"]),
        "páginas": int(libro["páginas"]),
        "stock": int(libro["stock"]),
    }
    try:
        validar_libro(libro_limpio)
    except ValueError as error:
        print(f"Libro no agregado: {error}")
        return
    catalogo.append(libro_limpio)
    print(f"Libro '{libro_limpio['título']}' agregado con id {libro_limpio['id']}.")


def eliminar_libro(catalogo: list[dict[str, Any]], id_libro: int) -> None:
    """Elimina del catalogo el libro con el id indicado."""
    for i, libro in enumerate(catalogo):
        if libro.get("id") == id_libro:
            eliminado = catalogo.pop(i)
            print(f"Libro '{eliminado['título']}' (id {eliminado['id']}) eliminado.")
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
            print(f"Libro '{libro['título']}' (id {libro['id']}) actualizado ({campo} = {valor}).")
            return
    print(f"No se encontro un libro con id {id_libro}.")


def buscar_por_id(catalogo: list[dict[str, Any]], id_libro: int) -> dict[str, Any] | None:
    """Devuelve el libro con el id indicado, o None si no existe."""
    for libro in catalogo:
        if libro.get("id") == id_libro:
            return libro
    return None


def buscar_por_género(catalogo: list[dict[str, Any]], género: str) -> list[dict[str, Any]]:
    """Devuelve los libros cuyo género coincide (sin distinguir mayúsculas)."""
    género = género.strip().lower()
    return [libro for libro in catalogo if libro["género"].lower() == género]


def buscar_por_autor(catalogo: list[dict[str, Any]], autor: str) -> list[dict[str, Any]]:
    """Devuelve los libros cuyo autor contiene el texto buscado."""
    autor = autor.strip().lower()
    return [libro for libro in catalogo if autor in libro["autor"].lower()]


def filtrar_por_año(catalogo: list[dict[str, Any]], año_min: int, año_max: int) -> list[dict[str, Any]]:
    """Devuelve los libros publicados dentro del rango de años."""
    return [libro for libro in catalogo if año_min <= libro["año"] <= año_max]


def calcular_indicadores(catalogo: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcula indicadores utiles sobre el catalogo."""
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


def generar_grafico(catalogo: list[dict[str, Any]], archivo_salida: str) -> None:
    """Genera un grafico de barras con la cantidad de libros por genero."""
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


def mostrar_catalogo(catalogo: list[dict[str, Any]]) -> None:
    """Imprime el catalogo en formato de tabla simple."""
    if not catalogo:
        print("El catalogo esta vacio.")
        return
    print(f"\n{'Id':>3} {'Titulo':<28} {'Autor':<24} {'Genero':<16} {'Año':>5} {'Precio':>8} {'Calif.':>6} {'Stock':>5}")
    print("-" * 108)
    for libro in catalogo:
        print(
            f"{libro['id']:>3} {libro['título']:<28} {libro['autor']:<24} {libro['género']:<16} "
            f"{libro['año']:>5} {libro['precio']:>8.0f} {libro['calificación']:>6.1f} {libro['stock']:>5}"
        )
    print("-" * 108)
    print(f"Total: {len(catalogo)} libros\n")
