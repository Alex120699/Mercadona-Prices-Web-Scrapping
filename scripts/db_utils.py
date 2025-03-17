# scripts/db_utils.py
import sqlite3
import json
from datetime import datetime

def get_db_connection():
    """Conecta a la base de datos SQLite."""
    conn = sqlite3.connect("data/productos.db")
    conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
    return conn

# scripts/db_utils.py
def create_database():
    """Crea las tablas en la base de datos si no existen."""
    conn = sqlite3.connect("data/productos.db")
    cursor = conn.cursor()

    # Crear la tabla productos si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id TEXT PRIMARY KEY,
        nombre TEXT,
        categoria_L1 TEXT,
        categoria_L2 TEXT,
        categoria_L3 TEXT,
        precio_con_descuento REAL,
        precio_sin_descuento REAL,
        packaging TEXT,
        bulk_price REAL,
        unit_size REAL,
        size_format TEXT,
        iva INTEGER,
        selling_method INTEGER,
        is_pack INTEGER,
        is_new INTEGER,
        price_decreased INTEGER,
        unavailable_from TEXT,
        url TEXT,
        imagen TEXT,
        last_updated TEXT
    )
    """)

    # Crear la tabla precios_historicos si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS precios_historicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id TEXT,
        precio_con_descuento REAL,
        fecha_actualizacion TEXT,
        UNIQUE(producto_id, fecha_actualizacion)  -- Restricción única
    )
    """)

    conn.commit()
    conn.close()

def save_json_to_db(json_file):
    """Guarda los datos del JSON en la base de datos."""
    conn = sqlite3.connect("data/productos.db")
    cursor = conn.cursor()

    with open(json_file, "r", encoding="utf-8") as file:
        productos = json.load(file)

    for producto in productos:
        cursor.execute("""
        INSERT OR REPLACE INTO productos VALUES (
            :id, :nombre, :categoria_L1, :categoria_L2, :categoria_L3,
            :precio_con_descuento, :precio_sin_descuento, :packaging, :bulk_price,
            :unit_size, :size_format, :iva, :selling_method, :is_pack, :is_new,
            :price_decreased, :unavailable_from, :url, :imagen
        )
        """, producto)

    conn.commit()
    conn.close()

# scripts/db_utils.py
def update_product_prices(productos):
    """Actualiza los precios de los productos y guarda el histórico."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener la fecha actual
    fecha_actualizacion = datetime.now().strftime("%Y-%m-%d")

    for producto in productos:
        producto_id = producto["id"]
        precio_con_descuento = producto["precio_con_descuento"]

        # Insertar o actualizar el histórico de precios
        cursor.execute("""
        INSERT INTO precios_historicos (producto_id, precio_con_descuento, fecha_actualizacion)
        VALUES (?, ?, ?)
        ON CONFLICT(producto_id, fecha_actualizacion) DO UPDATE SET
            precio_con_descuento = excluded.precio_con_descuento
        """, (producto_id, precio_con_descuento, fecha_actualizacion))

        # Actualizar la tabla productos
        cursor.execute("""
        UPDATE productos
        SET precio_con_descuento = ?, last_updated = ?
        WHERE id = ?
        """, (precio_con_descuento, fecha_actualizacion, producto_id))

    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()




if __name__ == "__main__":
    create_database()
    save_json_to_db("data/productos.json")
    print("Base de datos creada y datos guardados.")