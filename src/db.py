"""
Capa de acceso a datos para MiMargen.

Usa SQLite con aislamiento por negocio (negocio_id) para que el mismo
link publico pueda ser usado por varios negocios sin mezclar su informacion.
La base de datos vive en data/mimargen.db dentro del proyecto.
"""

import sqlite3
import os
import random
import string
from datetime import datetime
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "mimargen.db")


@contextmanager
def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Crea las tablas si no existen. Se llama una vez al iniciar la app."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS negocios (
                negocio_id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                negocio_id TEXT NOT NULL,
                nombre TEXT NOT NULL,
                costo REAL NOT NULL,
                precio_venta REAL NOT NULL,
                unidades_mes INTEGER,
                margen_pct REAL,
                precio_minimo REAL,
                ganancia_neta REAL,
                sueldo_hora REAL,
                fecha_registro TEXT NOT NULL,
                FOREIGN KEY (negocio_id) REFERENCES negocios(negocio_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                negocio_id TEXT NOT NULL,
                proveedor TEXT,
                descripcion TEXT,
                monto REAL NOT NULL,
                fuente TEXT NOT NULL DEFAULT 'manual',
                fecha TEXT NOT NULL,
                FOREIGN KEY (negocio_id) REFERENCES negocios(negocio_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                negocio_id TEXT NOT NULL,
                producto_nombre TEXT,
                cantidad REAL NOT NULL,
                precio_unitario REAL,
                fecha TEXT NOT NULL,
                FOREIGN KEY (negocio_id) REFERENCES negocios(negocio_id)
            )
        """)


# ---------- Negocios ----------

def _generar_codigo(largo=6):
    alfabeto = string.ascii_uppercase + string.digits
    return "".join(random.choices(alfabeto, k=largo))


def crear_negocio(nombre):
    """Crea un negocio nuevo y devuelve su codigo unico de acceso."""
    with get_connection() as conn:
        for _ in range(5):
            codigo = _generar_codigo()
            existe = conn.execute(
                "SELECT 1 FROM negocios WHERE negocio_id = ?", (codigo,)
            ).fetchone()
            if not existe:
                conn.execute(
                    "INSERT INTO negocios (negocio_id, nombre, fecha_creacion) VALUES (?, ?, ?)",
                    (codigo, nombre, datetime.now().isoformat())
                )
                return codigo
    raise RuntimeError("No se pudo generar un codigo unico, intenta de nuevo.")


def obtener_negocio(negocio_id):
    """Devuelve el nombre del negocio si el codigo existe, o None."""
    if not negocio_id:
        return None
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT nombre FROM negocios WHERE negocio_id = ?", (negocio_id,)
        ).fetchone()
        return fila["nombre"] if fila else None


# ---------- Productos ----------

def guardar_producto(negocio_id, nombre, costo, precio_venta, unidades_mes,
                      margen_pct, precio_minimo, ganancia_neta, sueldo_hora):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO productos
            (negocio_id, nombre, costo, precio_venta, unidades_mes,
             margen_pct, precio_minimo, ganancia_neta, sueldo_hora, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (negocio_id, nombre, costo, precio_venta, unidades_mes,
              margen_pct, precio_minimo, ganancia_neta, sueldo_hora,
              datetime.now().isoformat()))


def listar_productos(negocio_id):
    with get_connection() as conn:
        filas = conn.execute("""
            SELECT nombre, costo, precio_venta, unidades_mes, margen_pct,
                   precio_minimo, ganancia_neta, sueldo_hora, fecha_registro
            FROM productos
            WHERE negocio_id = ?
            ORDER BY fecha_registro DESC
        """, (negocio_id,)).fetchall()
        return [dict(f) for f in filas]


# ---------- Gastos ----------

def guardar_gasto(negocio_id, proveedor, descripcion, monto, fuente="manual"):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO gastos (negocio_id, proveedor, descripcion, monto, fuente, fecha)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (negocio_id, proveedor, descripcion, monto, fuente,
              datetime.now().isoformat()))


def listar_gastos(negocio_id):
    with get_connection() as conn:
        filas = conn.execute("""
            SELECT proveedor, descripcion, monto, fuente, fecha
            FROM gastos
            WHERE negocio_id = ?
            ORDER BY fecha DESC
        """, (negocio_id,)).fetchall()
        return [dict(f) for f in filas]


# ---------- Ventas (lista para la siguiente fase: registro diario) ----------

def guardar_venta(negocio_id, producto_nombre, cantidad, precio_unitario):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO ventas (negocio_id, producto_nombre, cantidad, precio_unitario, fecha)
            VALUES (?, ?, ?, ?, ?)
        """, (negocio_id, producto_nombre, cantidad, precio_unitario,
              datetime.now().isoformat()))


def listar_ventas(negocio_id):
    with get_connection() as conn:
        filas = conn.execute("""
            SELECT producto_nombre, cantidad, precio_unitario, fecha
            FROM ventas
            WHERE negocio_id = ?
            ORDER BY fecha DESC
        """, (negocio_id,)).fetchall()
        return [dict(f) for f in filas]