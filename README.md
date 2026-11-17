# Biblioteca ORM — Proyecto Integrador UD3

Aplicación de consola para la gestión integral de una biblioteca (libros, autores, socios, ejemplares y préstamos) utilizando **SQLAlchemy 2.x**, **PostgreSQL**, **Alembic** y **pytest** bajo una arquitectura por capas con patrón **Repositorio**, **Unit of Work** y **DTO**.

---

## Integrantes y reparto de tareas

- **Integrante 1 (Modelos y repositorios):** Entidades ORM, relaciones bidireccionales, consultas dinámicas, repositorios y estrategias de carga (`selectinload`, `joinedload`).
- **Integrante 2 (Servicios y transacciones):** Reglas de negocio, Unit of Work, registro y devolución de préstamos, excepciones de dominio y control transaccional (`commit` / `rollback`).
- **Integrante 3 (Pruebas, migraciones y documentación):** Suite `pytest`, fixtures unitarias y de integración, diagnóstico N+1, migraciones con Alembic, `README.md` y evidencias.

*(Proyecto desarrollado e integrado de forma individual para la entrega de UD3: Antonio Segovia).*

---

## Requisitos

- Python 3.12+
- PostgreSQL 16+
- Dependencias Python listadas en `requirements.txt`:
  - `SQLAlchemy>=2.0.30`
  - `psycopg[binary]>=3.1.18`
  - `alembic>=1.13.1`
  - `pytest>=8.0.0`

---

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Variables de entorno necesarias

Configurar mediante variables de entorno (sin incluir contraseñas ni archivos `.env` en el repositorio):

```bash
export DATABASE_URL="postgresql+psycopg://localhost:5432/biblioteca_orm"
export TEST_DATABASE_URL="postgresql+psycopg://localhost:5432/biblioteca_test"
export SQL_ECHO="false"
```

---

## Creación de bases de datos (`biblioteca_orm` y `biblioteca_test`)

```bash
psql -h 127.0.0.1 -d postgres -c "CREATE DATABASE biblioteca_orm;"
psql -h 127.0.0.1 -d postgres -c "CREATE DATABASE biblioteca_test;"
```

---

## Aplicación de migraciones (Alembic)

```bash
PYTHONPATH=. alembic upgrade head
```

Para comprobar la revisión actual y probar reversión/reaplicación:

```bash
PYTHONPATH=. alembic current
PYTHONPATH=. alembic downgrade -1
PYTHONPATH=. alembic upgrade head
```

---

## Ejecución de la aplicación

```bash
python main.py
```

---

## Ejecución de las pruebas

```bash
pytest -q
```

Las pruebas unitarias emplean repositorios falsos y una `UnidadTrabajoFalsa` en memoria; las pruebas de integración se ejecutan contra `biblioteca_test` dentro de una transacción que se revierte automáticamente (`rollback()`) al finalizar cada caso.

---

## Estructura del proyecto

```text
biblioteca_orm/
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── modelos/
│   │   ├── base.py
│   │   ├── autor.py
│   │   ├── libro.py
│   │   ├── socio.py
│   │   ├── ejemplar.py
│   │   └── prestamo.py
│   ├── repositorios/
│   │   ├── autores.py
│   │   ├── libros.py
│   │   ├── socios.py
│   │   ├── ejemplares.py
│   │   └── prestamos.py
│   ├── servicios/
│   │   ├── catalogo.py
│   │   └── prestamos.py
│   ├── dto/
│   │   ├── libros.py
│   │   └── prestamos.py
│   ├── configuracion.py
│   ├── conexion.py
│   ├── excepciones.py
│   └── unidad_trabajo.py
├── tests/
│   ├── conftest.py
│   ├── test_catalogo_servicio.py
│   ├── test_prestamo_servicio.py
│   └── test_repositorios.py
├── capturas/
├── main.py
├── alembic.ini
├── requirements.txt
├── respuestas.pdf
├── README.md
└── .gitignore
```

---

## Arquitectura utilizada

```text
Interfaz de consola (main.py)
        ↓
Servicios (CatalogoServicio, PrestamoServicio)
        ↓
Unit of Work (UnidadTrabajo)
        ↓
Repositorios ORM (Autor, Libro, Socio, Ejemplar, Prestamo)
        ↓
SQLAlchemy 2.x
        ↓
PostgreSQL
```

---

## Decisiones principales

1. **SQLAlchemy 2.x tipado:** Uso de `DeclarativeBase`, `Mapped` y `mapped_column`, `Decimal` (`Numeric(8, 2)`) para precios y relaciones bidireccionales con `back_populates`.
2. **Separación estricta de responsabilidades:** Los repositorios solo construyen consultas y manipulan la `Session` sin ejecutar `commit()`, `print()` ni `input()`. Cada caso de uso en los servicios abre una única `UnidadTrabajo`, ejecuta sus validaciones de negocio y confirma atómicamente con un único `commit()`.
3. **Consultas dinámicas y DTO:** `FiltroLibros` añade únicamente condiciones activas; los servicios devuelven DTOs inmutables (`LibroResumen`, `PrestamoResumen`) para desacoplar la presentación del modelo ORM.
4. **Control de rendimiento (N+1):**
   - `LibroRepositorio`: `joinedload(Libro.autor)` para evitar consultas adicionales al acceder a `libro.autor`.
   - `AutorRepositorio`: `selectinload(Autor.libros)` para cargar todos los libros de los autores en una única consulta agrupada.
   - `PrestamoRepositorio`: `joinedload(Prestamo.socio)` y `selectinload(Prestamo.ejemplares).joinedload(Ejemplar.libro)`.

### Evidencia de optimización N+1 (verificada con `before_cursor_execute` en `tests/test_repositorios.py`)

Para 5 autores con libros asociados:

- **Sin `selectinload` (carga perezosa):** `6` consultas SQL (`1` consulta de autores + `5` consultas individuales de libros).
- **Con `selectinload(Autor.libros)`:** `2` consultas SQL (`1` consulta de autores + `1` consulta agrupada con `IN` para todos los libros).

---

## Errores conocidos o limitaciones

- La interfaz de consola es monousuario y no gestiona concurrencia optimista/pesimista entre múltiples terminales simultáneas.
- No incluye gestión de reservas anticipadas ni cálculo automático de sanciones por retraso (más allá del registro de `fecha_limite` y `fecha_devolucion`).
