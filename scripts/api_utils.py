import requests
import pandas as pd
import json
from scripts.db_utils import get_db_connection, update_product_prices


# Constantes
CATEGORIES_URL = "https://tienda.mercadona.es/api/categories/"

def fetch_categories():
    """Obtiene las categorías de nivel 1 (L1) desde la API."""
    response = requests.get(CATEGORIES_URL)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []

def fetch_products(subcategory_id):
    """Obtiene los productos de una subcategoría (L3) desde la API."""
    products_url = f"https://tienda.mercadona.es/api/categories/{subcategory_id}"
    response = requests.get(products_url)
    if response.status_code == 200:
        return response.json().get("categories", [])
    return []

def parse_product(product, category_L1, category_L2, category_L3):
    """Parsea un producto y devuelve un diccionario con sus datos."""
    price_instructions = product.get("price_instructions", {})
    previous_price = price_instructions.get("previous_unit_price")
    
    return {
        "id": product["id"],
        "nombre": product["display_name"],
        "categoria_L1": category_L1,
        "categoria_L2": category_L2,
        "categoria_L3": category_L3,
        "precio_con_descuento": float(price_instructions["unit_price"]),
        "precio_sin_descuento": float(previous_price.strip()) 
            if isinstance(previous_price, str) else None,
        "packaging": product.get("packaging"),
        "bulk_price": float(price_instructions["bulk_price"]) 
            if price_instructions.get("bulk_price") else None,
        "unit_size": price_instructions.get("unit_size"),
        "size_format": price_instructions.get("size_format"),
        "iva": price_instructions.get("iva"),
        "selling_method": price_instructions.get("selling_method"),
        "is_pack": price_instructions.get("is_pack"),
        "is_new": price_instructions.get("is_new"),
        "price_decreased": price_instructions.get("price_decreased"),
        "unavailable_from": product.get("unavailable_from"),
        "url": product["share_url"],
        "imagen": product["thumbnail"]
    }

def get_all_products():
    """Obtiene todos los productos de Mercadona."""
    productos = []
    categories_L1 = fetch_categories()
    
    for category_L1 in categories_L1:
        nombre_L1 = category_L1["name"]
        
        for category_L2 in category_L1.get("categories", []):
            nombre_L2 = category_L2["name"]
            subcategory_id = category_L2["id"]
            
            categories_L3 = fetch_products(subcategory_id)
            for category_L3 in categories_L3:
                nombre_L3 = category_L3["name"]
                
                for product in category_L3.get("products", []):
                    productos.append(parse_product(product, nombre_L1, nombre_L2, nombre_L3))
    
    return productos

def guardar_datos_en_db(productos):
    """Guarda los datos obtenidos de la API en la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    for producto in productos:
        # Insertar o actualizar el producto en la base de datos
        cursor.execute("""
        INSERT OR REPLACE INTO productos (
            id, nombre, categoria_L1, categoria_L2, categoria_L3,
            precio_con_descuento, precio_sin_descuento, packaging,
            bulk_price, unit_size, size_format, iva, selling_method,
            is_pack, is_new, price_decreased, unavailable_from, url, imagen
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            producto["id"], producto["nombre"], producto["categoria_L1"],
            producto["categoria_L2"], producto["categoria_L3"],
            producto["precio_con_descuento"], producto["precio_sin_descuento"],
            producto["packaging"], producto["bulk_price"], producto["unit_size"],
            producto["size_format"], producto["iva"], producto["selling_method"],
            producto["is_pack"], producto["is_new"], producto["price_decreased"],
            producto["unavailable_from"], producto["url"], producto["imagen"]
        ))

    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()

def actualizar_datos():
    """Obtiene datos de la API y los guarda en la base de datos."""
    productos = get_all_products()
    if productos:
        guardar_datos_en_db(productos)
        update_product_prices(productos)  # Actualizar el histórico de precios
        print("Datos actualizados correctamente.")
    else:
        print("No se pudieron obtener datos de la API.")

def save_to_json(data, filename):
    """Guarda los datos en un archivo JSON."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def save_to_csv(data, filename):
    """Guarda los datos en un archivo CSV."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def main():
    """Función principal para ejecutar el script."""
    productos = get_all_products()
    
    # Guardar los datos
    save_to_json(productos, "data/productos.json")
    save_to_csv(productos, "data/productos.csv")
    
    print(f"Total de productos extraídos: {len(productos)}")
    #print(pd.DataFrame(productos).head())

if __name__ == "__main__":
    main()