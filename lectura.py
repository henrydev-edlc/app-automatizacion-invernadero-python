import serial
import time
import re   # para extraer números

# Cambia COM3 por el puerto real en tu PC:
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Espera que el puerto se estabilice

while True:
    linea = arduino.readline().decode().strip()  # lee línea de Arduino
    
    if linea:  # si la línea no viene vacía
        print("Raw recibido:", linea)

        # Buscamos los números usando regex
        datos = re.findall(r'\d+', linea)

        if len(datos) >= 2:
            temperatura = int(datos[0])
            humedad = int(datos[1])
            
            print(f"Temperatura = {temperatura} °C  |  Humedad = {humedad} %\n")
        else:
            print("⚠ No se detectaron valores válidos.\n")
