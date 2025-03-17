# scripts/db_utils.py
import sqlite3
import json

def create_database():
    """Crea la base de datos SQLite y la tabla de productos."""
    conn = sqlite3.connect("data/productos.db")
    cursor = conn.cursor()

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
        imagen TEXT
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

if __name__ == "__main__":
    create_database()
    save_json_to_db("data/productos.json")
    print("Base de datos creada y datos guardados.")