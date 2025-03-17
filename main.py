# main.py
import datetime
from scripts.db_utils import create_database, get_db_connection
from scripts.api_utils import actualizar_datos

if __name__ == "__main__":
    # Crear las tablas si no existen
    create_database()

    # Ejecutar la lógica principal para actualizar los datos
    actualizar_datos()

    # Guardar la fecha y hora de la última actualización
    with open("last_refresh.txt", "w") as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))