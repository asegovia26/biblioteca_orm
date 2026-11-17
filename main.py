"""Interfaz de consola para la administración de la biblioteca."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.conexion import crear_fabrica_sesiones
from app.dto.libros import DatosLibro, FiltroLibros
from app.dto.prestamos import DatosPrestamo
from app.excepciones import ErrorBiblioteca
from app.servicios.catalogo import CatalogoServicio
from app.servicios.prestamos import PrestamoServicio
from app.unidad_trabajo import UnidadTrabajo


def _leer_entero(mensaje: str) -> int:
    while True:
        valor = input(mensaje).strip()
        try:
            return int(valor)
        except ValueError:
            print("Por favor, introduce un número entero válido.")


def _leer_entero_opcional(mensaje: str) -> int | None:
    valor = input(mensaje).strip()
    if not valor:
        return None
    try:
        return int(valor)
    except ValueError as exc:
        raise ValueError("El valor numérico introducido no es válido.") from exc


def _leer_decimal(mensaje: str) -> Decimal:
    while True:
        valor = input(mensaje).strip().replace(",", ".")
        try:
            return Decimal(valor)
        except InvalidOperation:
            print("Por favor, introduce un importe decimal válido (ej. 19.95).")


def _leer_decimal_opcional(mensaje: str) -> Decimal | None:
    valor = input(mensaje).strip().replace(",", ".")
    if not valor:
        return None
    try:
        return Decimal(valor)
    except InvalidOperation as exc:
        raise ValueError("El importe decimal introducido no es válido.") from exc


def _mostrar_libros(libros: list) -> None:
    if not libros:
        print("No se encontraron libros con los criterios indicados.")
        return
    print(f"\n{'ID':<4} {'Título':<40} {'Autor':<28} {'Precio':>8}")
    print("-" * 84)
    for libro in libros:
        titulo = (libro.titulo[:37] + "...") if len(libro.titulo) > 40 else libro.titulo
        autor = (libro.autor[:25] + "...") if len(libro.autor) > 28 else libro.autor
        print(f"{libro.id_libro:<4} {titulo:<40} {autor:<28} {libro.precio:>7.2f}€")


def _mostrar_prestamos(prestamos: list) -> None:
    if not prestamos:
        print("No hay préstamos abiertos en este momento.")
        return
    print(f"\n{'ID':<4} {'Socio':<26} {'Préstamo':<12} {'Límite':<12} {'Ejemplares'}")
    print("-" * 88)
    for p in prestamos:
        ejemplares = ", ".join(p.ejemplares)
        print(
            f"{p.id_prestamo:<4} {p.socio:<26} "
            f"{str(p.fecha_prestamo):<12} {str(p.fecha_limite):<12} {ejemplares}"
        )


def mostrar_menu() -> None:
    """Muestra las opciones principales del menú."""
    print("\n=== BIBLIOTECA ORM ===")
    print("1. Listar libros")
    print("2. Buscar libros")
    print("3. Crear libro")
    print("4. Actualizar precio")
    print("5. Desactivar libro")
    print("6. Registrar préstamo")
    print("7. Devolver préstamo")
    print("8. Mostrar préstamos abiertos")
    print("9. Salir")


def ejecutar_consola() -> None:
    """Bucle principal de la aplicación de consola."""
    fabrica_sesiones = crear_fabrica_sesiones()

    def crear_uow() -> UnidadTrabajo:
        return UnidadTrabajo(fabrica_sesiones)

    catalogo = CatalogoServicio(crear_uow)
    prestamos = PrestamoServicio(crear_uow)

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción (1-9): ").strip()

        try:
            if opcion == "1":
                pagina = _leer_entero_opcional("Página [1]: ") or 1
                tamano = _leer_entero_opcional("Tamaño de página [10]: ") or 10
                resultado = catalogo.listar_libros(
                    FiltroLibros(pagina=pagina, tamano=tamano)
                )
                _mostrar_libros(resultado)

            elif opcion == "2":
                texto = input("Texto en título (Enter para omitir): ").strip() or None
                id_autor = _leer_entero_opcional("ID de autor (Enter para omitir): ")
                p_min = _leer_decimal_opcional("Precio mínimo (Enter para omitir): ")
                p_max = _leer_decimal_opcional("Precio máximo (Enter para omitir): ")
                pagina = _leer_entero_opcional("Página [1]: ") or 1
                tamano = _leer_entero_opcional("Tamaño [10]: ") or 10
                filtro = FiltroLibros(
                    texto=texto,
                    id_autor=id_autor,
                    precio_minimo=p_min,
                    precio_maximo=p_max,
                    pagina=pagina,
                    tamano=tamano,
                )
                _mostrar_libros(catalogo.listar_libros(filtro))

            elif opcion == "3":
                isbn = input("ISBN: ").strip()
                titulo = input("Título: ").strip()
                precio = _leer_decimal("Precio: ")
                id_autor = _leer_entero("ID del autor: ")
                creado = catalogo.crear_libro(
                    DatosLibro(isbn=isbn, titulo=titulo, precio=precio, id_autor=id_autor)
                )
                print(
                    f"Libro creado correctamente: [{creado.id_libro}] "
                    f"{creado.titulo} ({creado.precio:.2f}€)"
                )

            elif opcion == "4":
                id_libro = _leer_entero("ID del libro: ")
                nuevo_precio = _leer_decimal("Nuevo precio: ")
                actualizado = catalogo.actualizar_precio(id_libro, nuevo_precio)
                print(
                    f"Precio actualizado: [{actualizado.id_libro}] "
                    f"{actualizado.titulo} -> {actualizado.precio:.2f}€"
                )

            elif opcion == "5":
                id_libro = _leer_entero("ID del libro a desactivar: ")
                catalogo.desactivar_libro(id_libro)
                print(f"Libro {id_libro} desactivado correctamente.")

            elif opcion == "6":
                id_socio = _leer_entero("ID del socio: ")
                id_ejemplar = _leer_entero("ID del ejemplar: ")
                observaciones = input("Observaciones (opcional): ").strip() or None
                resumen = prestamos.registrar_prestamo(
                    DatosPrestamo(
                        id_socio=id_socio,
                        id_ejemplar=id_ejemplar,
                        observaciones=observaciones,
                    )
                )
                print(
                    f"Préstamo #{resumen.id_prestamo} registrado para {resumen.socio}. "
                    f"Fecha límite: {resumen.fecha_limite}."
                )

            elif opcion == "7":
                id_prestamo = _leer_entero("ID del préstamo a devolver: ")
                resumen = prestamos.devolver_prestamo(id_prestamo)
                print(
                    f"Préstamo #{resumen.id_prestamo} devuelto el {resumen.fecha_devolucion}."
                )

            elif opcion == "8":
                _mostrar_prestamos(prestamos.listar_prestamos_abiertos())

            elif opcion == "9":
                print("Hasta pronto.")
                break

            else:
                print("Opción no válida. Elige un número del 1 al 9.")

        except (ErrorBiblioteca, ValueError) as exc:
            print(f"[Error] {exc}")


if __name__ == "__main__":
    ejecutar_consola()
