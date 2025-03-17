import requests
import pandas as pd
import json

# URL base de la API
CATEGORIES_URL = "https://tienda.mercadona.es/api/categories/"

# Obtener todas las categorías
response = requests.get(CATEGORIES_URL)
categories_data = response.json()["results"] if response.status_code == 200 else []

productos = []

# Recorrer las categorías y subcategorías
for category in categories_data:
    category_L1 = category["name"]
    
    for subcategory in category["categories"]:
        category_L2 = subcategory["name"]
        subcategory_id = subcategory["id"]

        # URL de productos para la subcategoría actual
        PRODUCTS_URL = f"https://tienda.mercadona.es/api/categories/{subcategory_id}"
        
        response_products = requests.get(PRODUCTS_URL)
        if response_products.status_code == 200:
            products_data = response_products.json().get("categories", [])
            
            for subcat in products_data:
                for product in subcat.get("products", []):
                    productos.append({
                    "id": product["id"],
                    "nombre": product["display_name"],
                    "categoria_L1": category_L1,
                    "categoria_L2": category_L2,
                    "categoria_L3": product["categories"][0]["name"] if product.get("categories") else None,
                    "precio_con_descuento": float(product["price_instructions"]["unit_price"]),
                    "precio_sin_descuento": float(product["price_instructions"]["previous_unit_price"].strip()) 
                                            if isinstance(product["price_instructions"].get("previous_unit_price"), str) else None,
                    "packaging": product.get("packaging"),
                    "bulk_price": float(product["price_instructions"]["bulk_price"]) if product["price_instructions"].get("bulk_price") else None,
                    "unit_size": product["price_instructions"].get("unit_size"),
                    "size_format": product["price_instructions"].get("size_format"),
                    "iva": product["price_instructions"].get("iva"),
                    "selling_method": product["price_instructions"].get("selling_method"),
                    "is_pack": product["price_instructions"].get("is_pack"),
                    "is_new": product["price_instructions"].get("is_new"),
                    "price_decreased": product["price_instructions"].get("price_decreased"),
                    "unavailable_from": product.get("unavailable_from"),
                    "url": product["share_url"],
                    "imagen": product["thumbnail"]
                })


# Convertir a DataFrame
df = pd.DataFrame(productos)

# Guardar los datos
df.to_json("productos.json", orient="records", indent=4)
df.to_csv("productos.csv", index=False)

# Mostrar las primeras filas
print(df.head())
