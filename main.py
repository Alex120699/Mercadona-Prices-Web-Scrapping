# main.py
import datetime
from scripts.api_utils import main

if __name__ == "__main__":
    # Ejecutar la lógica principal para actualizar los datos
    main()

    # Guardar la fecha y hora de la última actualización
    with open("last_refresh.txt", "w") as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))