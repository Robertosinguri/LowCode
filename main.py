# Ejecucion principal de la aplicacion de catalogo de libros.

from typing import Any, Callable, TypeVar

from funciones import (
    ARCHIVO_DATOS,
    ARCHIVO_GRAFICO,
    CAMPOS,
    CAMPOS_DECIMALES,
    CAMPOS_ENTEROS,
    agregar_libro,
    buscar_por_autor,
    buscar_por_género,
    buscar_por_id,
    calcular_indicadores,
    cargar_catalogo,
    configurar_utf8,
    eliminar_libro,
    filtrar_por_año,
    generar_grafico,
    guardar_catalogo,
    modificar_libro,
    mostrar_catalogo,
)

T = TypeVar("T", int, float)

# Palabra que el usuario escribe para abortar una carga de datos.
PALABRA_CANCELAR = "cancelar"

# Sufijo que se agrega a los mensajes para indicar como cancelar.
SUFIJO_CANCELAR = f" (o escriba '{PALABRA_CANCELAR}')"

# Se lanza cuando el usuario decide abortar una carga en curso.
class CargaCancelada(Exception):
    pass

# Confirma con el usuario si realmente quiere abortar una carga.
def confirmar_cancelacion(
    mensaje: str = "¿Cancelar la carga? Se perderán los datos ingresados. (s/n): ",
) -> bool:
    return input(mensaje).strip().lower() == "s"

# Pide un numero al usuario, repitiendo hasta que sea valido.
def pedir_numero(
    mensaje: str,
    tipo: type[T],
    opcional: bool = False,
    mensaje_confirmacion: str | None = None,
) -> T | None:

    if tipo is int:
        aviso = "Entrada inválida: ingrese un número entero."
    else:
        aviso = "Entrada inválida: ingrese un número."
    while True:
        entrada = input(mensaje).strip()
        if entrada.lower() == PALABRA_CANCELAR:
            if mensaje_confirmacion is None:
                confirmado = confirmar_cancelacion()
            else:
                confirmado = confirmar_cancelacion(mensaje_confirmacion)
            if confirmado:
                raise CargaCancelada
            continue
        if opcional and entrada == "":
            return None
        try:
            return tipo(entrada)
        except ValueError:
            print(aviso)

# Pide un texto; la palabra de cancelacion aborta la carga (lanza CargaCancelada).
def pedir_texto(
    mensaje: str,
    opcional: bool = False,
    mensaje_confirmacion: str | None = None,
) -> str | None:
    while True:
        valor = input(mensaje).strip()
        if valor.lower() == PALABRA_CANCELAR:
            if mensaje_confirmacion is None:
                confirmado = confirmar_cancelacion()
            else:
                confirmado = confirmar_cancelacion(mensaje_confirmacion)
            if confirmado:
                raise CargaCancelada
            continue
        if opcional and valor == "":
            return None
        return valor

# Recopila los datos de un nuevo libro y lo agrega al catalogo.
def menu_agregar(catalogo: list[dict[str, Any]]) -> None:

    print("\n--- Agregar libro ---")
    try:
        título = pedir_texto(f"Título{SUFIJO_CANCELAR}: ")
        autor = pedir_texto(f"Autor{SUFIJO_CANCELAR}: ")
        género = pedir_texto(f"Género{SUFIJO_CANCELAR}: ")
        año = pedir_numero(f"Año de publicación{SUFIJO_CANCELAR}: ", int)
        precio = pedir_numero(f"Precio{SUFIJO_CANCELAR}: ", float)
        calificación = pedir_numero(f"Calificación (0 a 5){SUFIJO_CANCELAR}: ", float)
        páginas = pedir_numero(f"Cantidad de páginas{SUFIJO_CANCELAR}: ", int)
        stock = pedir_numero(f"Stock{SUFIJO_CANCELAR}: ", int)
    except CargaCancelada:
        print("Carga cancelada. No se agregó ningún libro.")
        return
    libro = {
        "título": título,
        "autor": autor,
        "género": género,
        "año": año,
        "precio": precio,
        "calificación": calificación,
        "páginas": páginas,
        "stock": stock,
    }
    agregar_libro(catalogo, libro)

# Pide un género y muestra los libros que coinciden.
def menu_buscar_genero(catalogo: list[dict[str, Any]]) -> None:
    género = input("Género a buscar: ")
    mostrar_catalogo(buscar_por_género(catalogo, género))

# Pide un autor y muestra los libros que coinciden.
def menu_buscar_autor(catalogo: list[dict[str, Any]]) -> None:
    autor = input("Autor a buscar: ")
    mostrar_catalogo(buscar_por_autor(catalogo, autor))

# Pide un rango de años y muestra los libros publicados dentro de el.
def menu_filtrar_año(catalogo: list[dict[str, Any]]) -> None:
    año_min = pedir_numero(f"Año mínimo (Enter o '{PALABRA_CANCELAR}'): ", int, opcional=True)

    if año_min is None:
        print("Filtro cancelado.")
        return
    año_max = pedir_numero(f"Año máximo (Enter o '{PALABRA_CANCELAR}'): ", int, opcional=True)

    if año_max is None:
        print("Filtro cancelado.")
        return
    mostrar_catalogo(filtrar_por_año(catalogo, año_min, año_max))

# Muestra los indicadores calculados sobre el catalogo.
def menu_indicadores(catalogo: list[dict[str, Any]]) -> None:
    indicadores = calcular_indicadores(catalogo)

    if not indicadores:
        print("El catalogo esta vacío, no hay indicadores para calcular.")
        return
    print("\n--- Indicadores ---")
    print(f"Total de libros: {indicadores['total_libros']}")
    print(f"Calificación promedio: {indicadores['promedio_calificación']}")
    print(f"Año promedio de publicación: {indicadores['promedio_año']}")
    print(f"Valor total del stock: ${indicadores['valor_total_stock']:,.0f}")
    print(f"Libro mejor calificado: {indicadores['mas_calificado']}")
    print("Libros por género:")

    for género, cantidad in indicadores["libros_por_género"].items():
        print(f"  - {género}: {cantidad}")

# Genera el grafico de libros por género.
def menu_generar_grafico(catalogo: list[dict[str, Any]]) -> None:
    generar_grafico(catalogo, ARCHIVO_GRAFICO)

# Pide un id y elimina el libro correspondiente, mostrando cual es y confirmando.
def menu_eliminar(catalogo: list[dict[str, Any]]) -> None:
    id_libro = pedir_numero(f"Id del libro a eliminar (Enter o '{PALABRA_CANCELAR}'): ", int, opcional=True)

    if id_libro is None:
        print("Eliminación cancelada.")
        return
    libro = buscar_por_id(catalogo, id_libro)

    if libro is None:
        print(f"No se encontró un libro con id {id_libro}.")
        return
    while True:
        confirmar = input(f"Eliminar '{libro['título']}' (id {id_libro})? (s/n): ").strip().lower()
        if confirmar == "s":
            break
        if confirmar == "n":
            print("No se eliminó el libro.")
            return
        if confirmar == PALABRA_CANCELAR:
            if confirmar_cancelacion("¿Abortar la eliminación? (s/n): "):
                print("Eliminación cancelada.")
                return
            continue
        print("Responda 's' para eliminar, 'n' para no eliminar.")
    eliminar_libro(catalogo, id_libro)

# Pide un id, muestra el libro y pide confirmacion antes de modificar. Se puede cancelar.
def menu_modificar(catalogo: list[dict[str, Any]]) -> None:
    id_libro = pedir_numero(f"Id del libro a modificar (Enter o '{PALABRA_CANCELAR}'): ", int, opcional=True)

    if id_libro is None:
        print("Modificación cancelada.")
        return
    libro = buscar_por_id(catalogo, id_libro)

    if libro is None:
        print(f"No se encontró un libro con id {id_libro}.")
        return
    print(f"Libro: '{libro['título']}' - {libro['autor']} ({libro['género']}, {libro['año']})")
    while True:
        confirmar = input("Es este el libro? (s/n): ").strip().lower()
        if confirmar == "s":
            break
        if confirmar == "n":
            print("No se modificó el libro.")
            return
        if confirmar == PALABRA_CANCELAR:
            if confirmar_cancelacion("¿Abortar la modificación? (s/n): "):
                print("Modificación cancelada.")
                return
            continue
        print("Responda 's' para continuar, 'n' para no modificar.")
    print(f"Campos disponibles: {', '.join(CAMPOS)}")
    while True:
        campo = input(f"Campo a modificar (Enter o '{PALABRA_CANCELAR}'): ").strip().lower()
        if campo == "":
            print("Modificación cancelada.")
            return
        if campo == PALABRA_CANCELAR:
            if confirmar_cancelacion("¿Abortar la modificación? (s/n): "):
                print("Modificación cancelada.")
                return
            continue
        if campo not in CAMPOS:
            print(f"Campo invalido. Elija uno de: {', '.join(CAMPOS)}.")
            continue
        break
    mensaje = f"Nuevo valor para {campo} (Enter o '{PALABRA_CANCELAR}'): "
    confirmacion = f"¿Cancelar el cambio de '{campo}'? (s/n): "

    try:
        if campo in CAMPOS_ENTEROS:
            valor: Any = pedir_numero(mensaje, int, opcional=True, mensaje_confirmacion=confirmacion)
        elif campo in CAMPOS_DECIMALES:
            valor = pedir_numero(mensaje, float, opcional=True, mensaje_confirmacion=confirmacion)
        else:
            valor = pedir_texto(mensaje, opcional=True, mensaje_confirmacion=confirmacion)
    except CargaCancelada:
        print(f"No se modificó '{campo}'.")
        return
    if valor is None:
        print(f"No se modificó '{campo}'.")
        return
    modificar_libro(catalogo, id_libro, campo, valor)

# Guarda el catalogo en disco.
def menu_guardar(catalogo: list[dict[str, Any]]) -> None:

    guardar_catalogo(catalogo, ARCHIVO_DATOS)
    print("Catalogo guardado. Hasta luego.")


# Menú de ejecucion principal
OPCIONES: dict[str, tuple[str, Callable[[list[dict[str, Any]]], None]]] = {
    "1": ("Ver catalogo", mostrar_catalogo),
    "2": ("Agregar libro", menu_agregar),
    "3": ("Buscar por género", menu_buscar_genero),
    "4": ("Buscar por autor", menu_buscar_autor),
    "5": ("Filtrar por año", menu_filtrar_año),
    "6": ("Ver indicadores", menu_indicadores),
    "7": ("Generar grafico", menu_generar_grafico),
    "8": ("Eliminar libro", menu_eliminar),
    "9": ("Modificar libro", menu_modificar),
    "10": ("Guardar y salir", menu_guardar),
}

# Imprime las opciones del menu a partir de la tabla OPCIONES.
def mostrar_menu() -> None:
    print("\n=== Catalogo de libros ===")

    for clave, (descripcion, _) in OPCIONES.items():
        print(f"{clave}. {descripcion}")

# Bucle principal del menu de la aplicación.
def main() -> None:
    configurar_utf8()
    catalogo = cargar_catalogo(ARCHIVO_DATOS)

    while True:
        mostrar_menu()
        opcion = input("Elegir opción: ").strip()
        if opcion not in OPCIONES:
            print("Opción inválida. Intente de nuevo.")
            continue

        _, accion = OPCIONES[opcion]
        if opcion == "10":
            accion(catalogo)
            break
        try:
            accion(catalogo)
        except CargaCancelada:
            print("Operación cancelada.")


if __name__ == "__main__":
    main()
