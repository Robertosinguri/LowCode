"""Ejecucion principal de la aplicacion de catalogo de libros.

Presenta un menu interactivo que permite cargar, agregar, buscar, filtrar,
consultar indicadores y generar un grafico sobre el catalogo guardado en JSON.
"""

import os
import sys

from funciones import (
    ARCHIVO_DATOS,
    ARCHIVO_GRAFICO,
    CAMPOS,
    agregar_libro,
    buscar_por_autor,
    buscar_por_genero,
    buscar_por_id,
    calcular_indicadores,
    cargar_catalogo,
    eliminar_libro,
    filtrar_por_anio,
    generar_grafico,
    guardar_catalogo,
    modificar_libro,
    mostrar_catalogo,
)


def configurar_utf8() -> None:
    """Fuerza UTF-8 en la consola de Windows para que los acentos se lean y muestren bien."""
    if os.name == "nt":
        os.system("chcp 65001 > nul")
    for flujo in (sys.stdin, sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


configurar_utf8()


def pedir_entero(mensaje: str) -> int:
    """Pide un numero entero al usuario manejando entradas invalidas."""
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("Entrada invalida: ingrese un numero entero.")


def pedir_decimal(mensaje: str) -> float:
    """Pide un numero decimal al usuario manejando entradas invalidas."""
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("Entrada invalida: ingrese un numero.")


def pedir_entero_opcional(mensaje: str) -> int | None:
    """Pide un entero; devuelve None si el usuario deja la entrada vacia (cancelar)."""
    while True:
        entrada = input(mensaje).strip()
        if entrada == "":
            return None
        try:
            return int(entrada)
        except ValueError:
            print("Entrada invalida: ingrese un numero entero.")


def pedir_decimal_opcional(mensaje: str) -> float | None:
    """Pide un decimal; devuelve None si el usuario deja la entrada vacia (cancelar)."""
    while True:
        entrada = input(mensaje).strip()
        if entrada == "":
            return None
        try:
            return float(entrada)
        except ValueError:
            print("Entrada invalida: ingrese un numero.")


def menu_agregar(catalogo: list) -> None:
    """Recopila los datos de un nuevo libro y lo agrega al catalogo."""
    print("\n--- Agregar libro ---")
    libro = {
        "titulo": input("Titulo: "),
        "autor": input("Autor: "),
        "genero": input("Genero: "),
        "anio": pedir_entero("Anio de publicacion: "),
        "precio": pedir_decimal("Precio: "),
        "calificacion": pedir_decimal("Calificacion (0 a 5): "),
        "paginas": pedir_entero("Cantidad de paginas: "),
        "stock": pedir_entero("Stock: "),
    }
    agregar_libro(catalogo, libro)


def menu_indicadores(catalogo: list) -> None:
    """Muestra los indicadores calculados sobre el catalogo."""
    indicadores = calcular_indicadores(catalogo)
    if not indicadores:
        print("El catalogo esta vacio, no hay indicadores para calcular.")
        return
    print("\n--- Indicadores ---")
    print(f"Total de libros: {indicadores['total_libros']}")
    print(f"Calificacion promedio: {indicadores['promedio_calificacion']}")
    print(f"Anio promedio de publicacion: {indicadores['promedio_anio']}")
    print(f"Valor total del stock: ${indicadores['valor_total_stock']:,.0f}")
    print(f"Libro mejor calificado: {indicadores['mas_calificado']}")
    print("Libros por genero:")
    for genero, cantidad in indicadores["libros_por_genero"].items():
        print(f"  - {genero}: {cantidad}")


def menu_eliminar(catalogo: list) -> None:
    """Pide un id y elimina el libro correspondiente, mostrando cual es y confirmando."""
    id_libro = pedir_entero_opcional("Id del libro a eliminar (Enter para cancelar): ")
    if id_libro is None:
        print("Eliminacion cancelada.")
        return
    libro = buscar_por_id(catalogo, id_libro)
    if libro is None:
        print(f"No se encontro un libro con id {id_libro}.")
        return
    confirmar = input(f"Eliminar '{libro['titulo']}' (id {id_libro})? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Eliminacion cancelada.")
        return
    eliminar_libro(catalogo, id_libro)


def menu_modificar(catalogo: list) -> None:
    """Pide un id, muestra el libro y pide confirmacion antes de modificar. Se puede cancelar."""
    id_libro = pedir_entero_opcional("Id del libro a modificar (Enter para cancelar): ")
    if id_libro is None:
        print("Modificacion cancelada.")
        return
    libro = buscar_por_id(catalogo, id_libro)
    if libro is None:
        print(f"No se encontro un libro con id {id_libro}.")
        return
    print(f"Libro: '{libro['titulo']}' - {libro['autor']} ({libro['genero']}, {libro['anio']})")
    confirmar = input("Es este el libro? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Modificacion cancelada.")
        return
    print(f"Campos disponibles: {', '.join(CAMPOS)}")
    campo = input("Campo a modificar (Enter para cancelar): ").strip().lower()
    if campo == "":
        print("Modificacion cancelada.")
        return
    if campo not in CAMPOS:
        print("Campo invalido.")
        return
    if campo in ("anio", "paginas", "stock"):
        valor = pedir_entero_opcional(f"Nuevo valor para {campo} (Enter para cancelar): ")
    elif campo in ("precio", "calificacion"):
        valor = pedir_decimal_opcional(f"Nuevo valor para {campo} (Enter para cancelar): ")
    else:
        valor = input(f"Nuevo valor para {campo} (Enter para cancelar): ")
        if valor == "":
            print("Modificacion cancelada.")
            return
    if valor is None:
        print("Modificacion cancelada.")
        return
    modificar_libro(catalogo, id_libro, campo, valor)


def main() -> None:
    """Bucle principal del menu de la aplicacion."""
    catalogo = cargar_catalogo(ARCHIVO_DATOS)

    while True:
        print("\n=== Catalogo de libros ===")
        print("1. Ver catalogo")
        print("2. Agregar libro")
        print("3. Buscar por genero")
        print("4. Buscar por autor")
        print("5. Filtrar por anio")
        print("6. Ver indicadores")
        print("7. Generar grafico")
        print("8. Eliminar libro")
        print("9. Modificar libro")
        print("10. Guardar y salir")

        opcion = input("Elegir opcion: ").strip()

        if opcion == "1":
            mostrar_catalogo(catalogo)
        elif opcion == "2":
            menu_agregar(catalogo)
        elif opcion == "3":
            genero = input("Genero a buscar: ")
            mostrar_catalogo(buscar_por_genero(catalogo, genero))
        elif opcion == "4":
            autor = input("Autor a buscar: ")
            mostrar_catalogo(buscar_por_autor(catalogo, autor))
        elif opcion == "5":
            anio_min = pedir_entero("Anio minimo: ")
            anio_max = pedir_entero("Anio maximo: ")
            mostrar_catalogo(filtrar_por_anio(catalogo, anio_min, anio_max))
        elif opcion == "6":
            menu_indicadores(catalogo)
        elif opcion == "7":
            generar_grafico(catalogo, ARCHIVO_GRAFICO)
        elif opcion == "8":
            menu_eliminar(catalogo)
        elif opcion == "9":
            menu_modificar(catalogo)
        elif opcion == "10":
            guardar_catalogo(catalogo, ARCHIVO_DATOS)
            print("Catalogo guardado. Hasta luego.")
            break
        else:
            print("Opcion invalida. Intente de nuevo.")


if __name__ == "__main__":
    main()
