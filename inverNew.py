import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import mysql.connector
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import sys
import io

# Configurar la salida para usar UTF-8 (Solución al error de codificación)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class VentanaControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control de Ventana Automática - MySQL")
        self.root.geometry("1600x950")
        
        # Variables
        self.serial_port = None
        self.arduino = None
        self.conectado = False
        self.temp_actual = 0.0
        self.hum_actual = 0.0
        self.estado_ventana = 0
        self.temp_abrir = 22.0
        self.temp_cerrar = 22.0
        
        # Configuración de MySQL
        self.setup_mysql_database()
        
        # Frame principal
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # Crear widgets
        self.create_widgets()
        
        # Iniciar hilo de lectura serial
        self.leer_serial_thread = None
        self.detener_thread = False
        
    def setup_mysql_database(self):
        """Configurar conexión a MySQL y crear tablas si no existen"""
        try:
            # Configuración de conexión a MySQL
            self.db_config = {
                'host': 'localhost',
                'user': 'root',
                'password': '123456',
                'database': 'ventana_control_db',
                'port': 3306
            }
            
            # Intentar conectar
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            
            # Crear base de datos si no existe
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS ventana_control_db")
            self.cursor.execute("USE ventana_control_db")
            
            # Crear tabla de lecturas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS lecturas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fecha_hora DATETIME,
                    temperatura DECIMAL(5,2),
                    humedad DECIMAL(5,2),
                    estado_ventana INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear tabla de configuraciones
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuraciones (
                    id INT PRIMARY KEY DEFAULT 1,
                    temp_abrir DECIMAL(5,2),
                    temp_cerrar DECIMAL(5,2),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')
            
            # Verificar si existe configuración
            self.cursor.execute('SELECT COUNT(*) FROM configuraciones WHERE id = 1')
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute('''
                    INSERT INTO configuraciones (id, temp_abrir, temp_cerrar) 
                    VALUES (1, 22.0, 22.0)
                ''')
            
            self.conn.commit()
            
            # Cargar configuración
            self.cursor.execute('SELECT temp_abrir, temp_cerrar FROM configuraciones WHERE id = 1')
            config = self.cursor.fetchone()
            if config:
                self.temp_abrir, self.temp_cerrar = config
                
            print("Conexión a MySQL establecida correctamente")
            
        except mysql.connector.Error as err:
            messagebox.showerror("Error MySQL", 
                f"No se pudo conectar a MySQL:\n\n"
                f"Código de error: {err.errno}\n"
                f"Mensaje: {err.msg}\n\n"
                f"Por favor, asegúrate de que:\n"
                f"1. MySQL esté instalado y ejecutándose\n"
                f"2. La base de datos 'ventana_control_db' exista\n"
                f"3. Las credenciales sean correctas\n\n"
                f"Configuración actual:\n"
                f"Host: {self.db_config.get('host')}\n"
                f"Usuario: {self.db_config.get('user')}"
            )
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
            self.root.destroy()
            
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        
        # Título
        title_label = ttk.Label(self.main_frame, text="SISTEMA DE CONTROL DE VENTANA AUTOMÁTICA (MySQL)", 
                               font=('Arial', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 30))
        
        # Frame de conexión serial
        frame_conexion = ttk.LabelFrame(self.main_frame, text="CONEXIÓN SERIAL", padding="15")
        frame_conexion.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Puerto COM
        ttk.Label(frame_conexion, text="Puerto COM:", font=('Arial', 14)).grid(row=0, column=0, padx=(0, 10), pady=5)
        self.com_combobox = ttk.Combobox(frame_conexion, width=25, font=('Arial', 14))
        self.com_combobox.grid(row=0, column=1, padx=(0, 20), pady=5)
        self.refresh_ports()
        
        # Botón conectar/desconectar
        self.btn_conectar = ttk.Button(frame_conexion, text="CONECTAR", 
                                      command=self.toggle_conexion, style='Large.TButton')
        self.btn_conectar.grid(row=0, column=2, padx=(0, 15))
        
        # Botón actualizar puertos
        ttk.Button(frame_conexion, text="ACTUALIZAR PUERTOS", 
                  command=self.refresh_ports, style='Medium.TButton').grid(row=0, column=3)
        
        # Frame de datos actuales
        frame_datos = ttk.LabelFrame(self.main_frame, text="DATOS ACTUALES", padding="20")
        frame_datos.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=(0, 15), pady=(0, 20))
        
        # Temperatura actual
        ttk.Label(frame_datos, text="TEMPERATURA:", font=('Arial', 16)).grid(row=0, column=0, sticky=tk.W, pady=15)
        self.lbl_temp = ttk.Label(frame_datos, text="-- °C", font=('Arial', 28, 'bold'))
        self.lbl_temp.grid(row=0, column=1, sticky=tk.W, pady=15, padx=(20, 0))
        
        # Humedad actual
        ttk.Label(frame_datos, text="HUMEDAD:", font=('Arial', 16)).grid(row=1, column=0, sticky=tk.W, pady=15)
        self.lbl_hum = ttk.Label(frame_datos, text="-- %", font=('Arial', 28, 'bold'))
        self.lbl_hum.grid(row=1, column=1, sticky=tk.W, pady=15, padx=(20, 0))
        
        # Estado ventana
        ttk.Label(frame_datos, text="ESTADO VENTANA:", font=('Arial', 16)).grid(row=2, column=0, sticky=tk.W, pady=15)
        self.lbl_estado = ttk.Label(frame_datos, text="--", font=('Arial', 28, 'bold'))
        self.lbl_estado.grid(row=2, column=1, sticky=tk.W, pady=15, padx=(20, 0))
        
        # Frame de configuración
        frame_config = ttk.LabelFrame(self.main_frame, text="CONFIGURACIÓN DE TEMPERATURA", padding="20")
        frame_config.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 15), pady=(0, 20))
        
        # Temperatura para abrir (con explicación)
        ttk.Label(frame_config, text="Abrir ventana (>):", font=('Arial', 14)).grid(row=0, column=0, sticky=tk.W, pady=10)
        ttk.Label(frame_config, text="(Temperatura > 22.9 °C)", font=('Arial', 10, 'italic')).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.temp_abrir_var = tk.DoubleVar(value=23.0)  # Cambiado a 23.0
        self.spin_abrir = ttk.Spinbox(frame_config, from_=0, to=50, increment=0.5, 
                                     textvariable=self.temp_abrir_var, width=15, font=('Arial', 14))
        self.spin_abrir.grid(row=0, column=1, padx=(15, 5), pady=10, rowspan=2)
        ttk.Label(frame_config, text="°C", font=('Arial', 16)).grid(row=0, column=2, padx=(0, 20), pady=10, rowspan=2)
        
        # Temperatura para cerrar (con explicación)
        ttk.Label(frame_config, text="Cerrar ventana (<):", font=('Arial', 14)).grid(row=2, column=0, sticky=tk.W, pady=10)
        ttk.Label(frame_config, text="(Temperatura < 22.0 °C)", font=('Arial', 10, 'italic')).grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.temp_cerrar_var = tk.DoubleVar(value=22.0)
        self.spin_cerrar = ttk.Spinbox(frame_config, from_=0, to=50, increment=0.5, 
                                      textvariable=self.temp_cerrar_var, width=15, font=('Arial', 14))
        self.spin_cerrar.grid(row=2, column=1, padx=(15, 5), pady=10, rowspan=2)
        ttk.Label(frame_config, text="°C", font=('Arial', 16)).grid(row=2, column=2, padx=(0, 20), pady=10, rowspan=2)
        
        # Nota explicativa
        ttk.Label(frame_config, text="NOTA: El rango normal es 22.0°C a 22.9°C", 
                 font=('Arial', 11, 'italic'), foreground='blue').grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        # Botón aplicar configuración
        ttk.Button(frame_config, text="APLICAR CONFIGURACIÓN", 
                  command=self.aplicar_configuracion, style='Large.TButton').grid(row=5, column=0, columnspan=3, pady=(20, 0))
        
        # Frame de control manual
        frame_control = ttk.LabelFrame(self.main_frame, text="CONTROL MANUAL", padding="20")
        frame_control.grid(row=2, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Botones más grandes
        btn_style = {'style': 'Large.TButton', 'padding': (20, 15)}
        ttk.Button(frame_control, text="ABRIR VENTANA", 
                  command=lambda: self.enviar_comando('ABRIR'), **btn_style).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Button(frame_control, text="CERRAR VENTANA", 
                  command=lambda: self.enviar_comando('CERRAR'), **btn_style).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Button(frame_control, text="DETENER MOTORES", 
                  command=lambda: self.enviar_comando('PARAR'), **btn_style).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de historial
        frame_historial = ttk.LabelFrame(self.main_frame, text="HISTORIAL DE TEMPERATURA", padding="20")
        frame_historial.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Configurar expansión del frame de historial
        self.main_frame.rowconfigure(3, weight=1)
        frame_historial.columnconfigure(0, weight=1)
        frame_historial.rowconfigure(1, weight=1)
        
        # Controles de historial
        frame_controles = ttk.Frame(frame_historial)
        frame_controles.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(frame_controles, text="PERÍODO:", font=('Arial', 14)).grid(row=0, column=0, padx=(0, 10), pady=5)
        self.periodo_var = tk.StringVar(value="24 horas")
        periodos = ["1 hora", "6 horas", "12 horas", "24 horas", "1 semana", "1 mes", "Todo el historial"]
        self.combo_periodo = ttk.Combobox(frame_controles, textvariable=self.periodo_var, 
                                         values=periodos, width=15, font=('Arial', 14))
        self.combo_periodo.grid(row=0, column=1, padx=(0, 20), pady=5)
        
        ttk.Button(frame_controles, text="ACTUALIZAR GRÁFICO", 
                  command=self.actualizar_grafico, style='Medium.TButton').grid(row=0, column=2, padx=(0, 20), pady=5)
        
        ttk.Button(frame_controles, text="EXPORTAR DATOS", 
                  command=self.exportar_datos, style='Medium.TButton').grid(row=0, column=3, pady=5)
        
        # Botón para ver estadísticas
        ttk.Button(frame_controles, text="ESTADÍSTICAS", 
                  command=self.mostrar_estadisticas, style='Medium.TButton').grid(row=0, column=4, padx=(10, 0), pady=5)
        
        # Gráfico
        self.fig, self.ax = plt.subplots(figsize=(14, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_historial)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Barra de estado
        self.status_bar = ttk.Label(self.main_frame, text="DESCONECTADO | MySQL: Conectado", relief=tk.SUNKEN, 
                                   padding=10, font=('Arial', 12))
        self.status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configurar estilos para botones grandes
        self.configure_styles()
        
    def configure_styles(self):
        """Configurar estilos para botones grandes"""
        style = ttk.Style()
        style.configure('Large.TButton', font=('Arial', 16, 'bold'), padding=15)
        style.configure('Medium.TButton', font=('Arial', 14, 'bold'), padding=10)
        style.configure('TLabelframe', font=('Arial', 16, 'bold'))
        style.configure('TLabelframe.Label', font=('Arial', 16, 'bold'))
        
    def refresh_ports(self):
        """Actualizar lista de puertos COM disponibles"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_combobox['values'] = ports
        if ports:
            self.com_combobox.set(ports[0])
            
    def toggle_conexion(self):
        """Conectar o desconectar del Arduino"""
        if not self.conectado:
            port = self.com_combobox.get()
            if not port:
                messagebox.showerror("Error", "Seleccione un puerto COM")
                return
                
            try:
                self.arduino = serial.Serial(port, 9600, timeout=1)
                time.sleep(2)
                self.conectado = True
                self.btn_conectar.config(text="DESCONECTAR")
                self.status_bar.config(text=f"CONECTADO A {port} | MySQL: Conectado")
                
                self.enviar_configuracion_arduino()
                
                self.detener_thread = False
                self.leer_serial_thread = threading.Thread(target=self.leer_serial, daemon=True)
                self.leer_serial_thread.start()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo conectar: {str(e)}")
        else:
            self.desconectar()
            
    def desconectar(self):
        """Desconectar del Arduino"""
        self.detener_thread = True
        if self.leer_serial_thread:
            self.leer_serial_thread.join(timeout=2)
            
        if self.arduino:
            self.arduino.close()
            
        self.conectado = False
        self.btn_conectar.config(text="CONECTAR")
        self.status_bar.config(text="DESCONECTADO | MySQL: Conectado")
        
        self.lbl_temp.config(text="-- °C")
        self.lbl_hum.config(text="-- %")
        self.lbl_estado.config(text="--")
        
    def leer_serial(self):
        """Leer datos del Arduino en un hilo separado"""
        while not self.detener_thread and self.arduino:
            try:
                if self.arduino.in_waiting > 0:
                    linea = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                    
                    if linea:
                        print(f"Recibido: {linea}")
                        self.procesar_datos(linea)
                        
            except Exception as e:
                print(f"Error leyendo serial: {e}")
                
            time.sleep(0.1)
            
    def procesar_datos(self, linea):
        """Procesar datos recibidos del Arduino"""
        try:
            if "Temperatura:" in linea and "Humedad:" in linea:
                temp_start = linea.find("Temperatura:") + len("Temperatura:")
                temp_end = linea.find("°C")
                temp_str = linea[temp_start:temp_end].strip()
                
                hum_start = linea.find("Humedad:") + len("Humedad:")
                hum_end = linea.find("%")
                hum_str = linea[hum_start:hum_end].strip()
                
                self.temp_actual = float(temp_str)
                self.hum_actual = float(hum_str)
                
                # Determinar estado de la ventana con mejor información
                if "Ventana ABIERTA" in linea:
                    self.estado_ventana = 1
                    estado_texto = "ABIERTA"
                elif "Ventana CERRADA" in linea:
                    self.estado_ventana = 0
                    estado_texto = "CERRADA"
                elif "Abriendo" in linea:
                    self.estado_ventana = 2
                    estado_texto = "ABRIENDO"
                elif "Cerrando" in linea:
                    self.estado_ventana = 3
                    estado_texto = "CERRANDO"
                else:
                    estado_texto = "DESCONOCIDO"
                
                # Imprimir estado detallado en consola
                print(f"Estado ventana: {estado_texto} | Temp: {self.temp_actual}°C | Hum: {self.hum_actual}%")
                
                # Análisis del estado de temperatura
                self.analizar_temperatura()
                    
                self.root.after(0, self.actualizar_ui)
                
                self.guardar_datos_mysql()
                
        except Exception as e:
            print(f"Error procesando datos: {e}")
            
    def analizar_temperatura(self):
        """Analizar la temperatura actual y determinar si está en rango normal"""
        # Temperatura normal: 22.0°C hasta 22.9°C
        # Abrir ventana: > 22.9°C (configurable, por defecto 23.0°C)
        # Cerrar ventana: < 22.0°C (configurable)
        
        if self.temp_actual >= 22.0 and self.temp_actual <= 22.9:
            print(f"Temperatura NORMAL: {self.temp_actual}°C (rango: 22.0°C - 22.9°C)")
        elif self.temp_actual > self.temp_abrir:
            print(f"Temperatura ALTA: {self.temp_actual}°C > {self.temp_abrir}°C → Debería ABRIR ventana")
        elif self.temp_actual < self.temp_cerrar:
            print(f"Temperatura BAJA: {self.temp_actual}°C < {self.temp_cerrar}°C → Debería CERRAR ventana")
            
    def actualizar_ui(self):
        """Actualizar la interfaz de usuario con los datos actuales"""
        # Temperatura normal: 22.0°C hasta 22.9°C
        # Abrir ventana: > 22.9°C
        # Cerrar ventana: < 22.0°C
        
        if self.temp_actual >= 22.0 and self.temp_actual <= 22.9:
            color_temp = "green"  # Temperatura normal
        elif self.temp_actual > self.temp_abrir:
            color_temp = "red"  # Temperatura alta, abrir ventana
        elif self.temp_actual < self.temp_cerrar:
            color_temp = "blue"  # Temperatura baja, cerrar ventana
        else:
            color_temp = "orange"  # En transición
            
        self.lbl_temp.config(text=f"{self.temp_actual:.1f} °C", foreground=color_temp)
        self.lbl_hum.config(text=f"{self.hum_actual:.1f} %")
        
        estados = {
            0: ("CERRADA", "red"),
            1: ("ABIERTA", "green"),
            2: ("ABRIENDO...", "orange"),
            3: ("CERRANDO...", "orange")
        }
        estado_text, estado_color = estados.get(self.estado_ventana, ("DESCONOCIDO", "black"))
        self.lbl_estado.config(text=estado_text, foreground=estado_color)
        
        # Imprimir en consola el análisis de temperatura
        print(f"UI Actualizada - Temp: {self.temp_actual:.1f}°C ({color_temp}) | Hum: {self.hum_actual:.1f}% | Estado: {estado_text}")
        
    def guardar_datos_mysql(self):
        """Guardar datos en MySQL"""
        try:
            fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Verificar si la conexión sigue activa
            if not self.conn.is_connected():
                print("Reconectando a MySQL...")
                self.conn.reconnect(attempts=3, delay=1)
            
            query = '''
                INSERT INTO lecturas (fecha_hora, temperatura, humedad, estado_ventana)
                VALUES (%s, %s, %s, %s)
            '''
            valores = (fecha_hora, self.temp_actual, self.hum_actual, self.estado_ventana)
            
            self.cursor.execute(query, valores)
            self.conn.commit()
            
            # Obtener texto del estado para mostrar en consola
            estado_texto = {0: "CERRADA", 1: "ABIERTA", 2: "ABRIENDO", 3: "CERRANDO"}.get(self.estado_ventana, "DESCONOCIDO")
            
            # Mostrar en consola el registro guardado (sin emojis para evitar error de codificación)
            print(f"Datos guardados en MySQL: {fecha_hora} - Temp: {self.temp_actual}°C, Hum: {self.hum_actual}%, Estado: {estado_texto}")
            
        except mysql.connector.Error as err:
            print(f"Error MySQL al guardar datos: {err}")
            # Intentar reconectar
            try:
                self.conn = mysql.connector.connect(**self.db_config)
                self.cursor = self.conn.cursor()
                print("Reconexión a MySQL exitosa")
            except:
                print("No se pudo reconectar a MySQL")
        except Exception as e:
            print(f"Error guardando datos en MySQL: {e}")
            
    def aplicar_configuracion(self):
        """Aplicar nueva configuración de temperatura"""
        try:
            self.temp_abrir = self.temp_abrir_var.get()
            self.temp_cerrar = self.temp_cerrar_var.get()
            
            if self.temp_abrir <= self.temp_cerrar:
                messagebox.showerror("Error", 
                    f"La temperatura para abrir ({self.temp_abrir}°C) debe ser MAYOR que para cerrar ({self.temp_cerrar}°C)\n\n"
                    f"Configuración recomendada:\n"
                    f"- Abrir: 23.0°C (para temperaturas > 22.9°C)\n"
                    f"- Cerrar: 22.0°C (para temperaturas < 22.0°C)")
                return
            
            # Verificar rango recomendado
            if self.temp_cerrar != 22.0 or self.temp_abrir < 23.0:
                respuesta = messagebox.askyesno("Confirmar configuración",
                    f"Configuración actual:\n"
                    f"- Abrir ventana: > {self.temp_abrir}°C\n"
                    f"- Cerrar ventana: < {self.temp_cerrar}°C\n\n"
                    f"¿Está seguro? El rango normal recomendado es 22.0°C a 22.9°C")
                if not respuesta:
                    return
            
            # Actualizar en MySQL
            query = '''
                UPDATE configuraciones 
                SET temp_abrir = %s, temp_cerrar = %s
                WHERE id = 1
            '''
            valores = (self.temp_abrir, self.temp_cerrar)
            
            self.cursor.execute(query, valores)
            self.conn.commit()
            
            if self.conectado:
                self.enviar_configuracion_arduino()
                
            messagebox.showinfo("Éxito", 
                f"Configuración aplicada correctamente:\n"
                f"- Abrir ventana: > {self.temp_abrir}°C\n"
                f"- Cerrar ventana: < {self.temp_cerrar}°C\n"
                f"- Rango normal: {self.temp_cerrar}°C a {self.temp_abrir - 0.1}°C")
            
            self.actualizar_ui()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar configuración: {e}")
            
    def enviar_configuracion_arduino(self):
        """Enviar configuración al Arduino"""
        if self.arduino:
            try:
                # Enviar temperatura para abrir (debe ser > 22.9°C) y cerrar (< 22.0°C)
                comando = f"CONFIG:ABRIR={self.temp_abrir},CERRAR={self.temp_cerrar}\n"
                self.arduino.write(comando.encode())
                print(f"Enviado al Arduino: {comando.strip()}")
                print(f"Configuración Arduino: Abrir cuando temperatura > {self.temp_abrir}°C, Cerrar cuando < {self.temp_cerrar}°C")
            except Exception as e:
                print(f"Error enviando configuración: {e}")
                
    def enviar_comando(self, comando):
        """Enviar comando manual al Arduino"""
        if self.conectado and self.arduino:
            try:
                self.arduino.write(f"{comando}\n".encode())
                self.status_bar.config(text=f"Comando {comando} enviado")
                print(f"Comando enviado: {comando}")
                
                # Actualizar estado local basado en el comando
                if comando == 'ABRIR':
                    self.estado_ventana = 2  # Abriendo
                    print("Estado actualizado a: ABRIENDO")
                elif comando == 'CERRAR':
                    self.estado_ventana = 3  # Cerrando
                    print("Estado actualizado a: CERRANDO")
                elif comando == 'PARAR':
                    print("Comando PARAR enviado, manteniendo estado actual")
                    
                self.root.after(0, self.actualizar_ui)
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo enviar comando: {e}")
        else:
            messagebox.showwarning("Advertencia", "Conecte primero al Arduino")
            
    def actualizar_grafico(self):
        """Actualizar gráfico del historial desde MySQL"""
        try:
            periodo = self.combo_periodo.get()
            ahora = datetime.now()
            
            # Construir consulta según el período seleccionado
            if periodo == "1 hora":
                inicio = ahora - timedelta(hours=1)
                query = "SELECT fecha_hora, temperatura, humedad FROM lecturas WHERE fecha_hora >= %s ORDER BY fecha_hora"
                valores = (inicio.strftime('%Y-%m-%d %H:%M:%S'),)
            elif periodo == "6 horas":
                inicio = ahora - timedelta(hours=6)
                query = "SELECT fecha_hora, temperatura, humedad FROM lecturas WHERE fecha_hora >= %s ORDER BY fecha_hora"
                valores = (inicio.strftime('%Y-%m-%d %H:%M:%S'),)
            elif periodo == "12 horas":
                inicio = ahora - timedelta(hours=12)
                query = "SELECT fecha_hora, temperatura, humedad FROM lecturas WHERE fecha_hora >= %s ORDER BY fecha_hora"
                valores = (inicio.strftime('%Y-%m-%d %H:%M:%S'),)
            elif periodo == "1 semana":
                inicio = ahora - timedelta(weeks=1)
                query = "SELECT fecha_hora, temperatura, humedad FROM lecturas WHERE fecha_hora >= %s ORDER BY fecha_hora"
                valores = (inicio.strftime('%Y-%m-%d %H:%M:%S'),)
            elif periodo == "1 mes":
                inicio = ahora - timedelta(days=30)
                query = "SELECT fecha_hora, temperatura, humedad FROM lecturas WHERE fecha_hora >= %s ORDER BY fecha_hora"
                valores = (inicio.strftime('%Y-%m-%d %H:%M:%S'),)
            elif periodo == "Todo el historial":
                query = "SELECT fecha_hora, temperatura, humedad FROM lecturas ORDER BY fecha_hora"
                valores = ()
            else:  # 24 horas por defecto
                inicio = ahora - timedelta(days=1)
                query = "SELECT fecha_hora, temperatura, humedad FROM lecturas WHERE fecha_hora >= %s ORDER BY fecha_hora"
                valores = (inicio.strftime('%Y-%m-%d %H:%M:%S'),)
            
            # Ejecutar consulta
            self.cursor.execute(query, valores)
            datos = self.cursor.fetchall()
            
            if not datos:
                messagebox.showinfo("Información", "No hay datos para el período seleccionado")
                return
                
            # Preparar datos para el gráfico
            fechas = [row[0] for row in datos]
            temperaturas = [float(row[1]) for row in datos]
            humedades = [float(row[2]) for row in datos]
            
            # Limpiar gráfico
            self.ax.clear()
            
            # Crear gráfico de temperatura
            color = 'tab:red'
            self.ax.set_xlabel('Hora', fontsize=12)
            self.ax.set_ylabel('Temperatura (°C)', color=color, fontsize=12)
            line1 = self.ax.plot(fechas, temperaturas, color=color, label='Temperatura', linewidth=2)
            self.ax.tick_params(axis='y', labelcolor=color, labelsize=10)
            
            # Crear segundo eje Y para humedad
            ax2 = self.ax.twinx()
            color = 'tab:blue'
            ax2.set_ylabel('Humedad (%)', color=color, fontsize=12)
            line2 = ax2.plot(fechas, humedades, color=color, label='Humedad', alpha=0.7, linewidth=1.5)
            ax2.tick_params(axis='y', labelcolor=color, labelsize=10)
            
            # Formatear eje X
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%d/%m'))
            self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            self.ax.tick_params(axis='x', labelsize=10)
            self.fig.autofmt_xdate()
            
            # Añadir líneas de referencia
            temp_abrir_entero = int(self.temp_abrir)
            temp_cerrar_entero = int(self.temp_cerrar)
            
            # Línea para temperatura de abrir
            self.ax.axhline(y=temp_abrir_entero, color='green', linestyle='--', alpha=0.5, 
                           linewidth=2, label=f'Abrir: {self.temp_abrir}°C')
            
            # Línea para temperatura de cerrar
            self.ax.axhline(y=temp_cerrar_entero, color='red', linestyle='--', alpha=0.5, 
                           linewidth=2, label=f'Cerrar: {self.temp_cerrar}°C')
            
            # Área de temperatura normal (22.0°C a 22.9°C)
            self.ax.axhspan(22.0, 22.9, alpha=0.1, color='green', label='Rango normal (22.0°C - 22.9°C)')
            
            # Título y leyenda
            self.ax.set_title(f'Historial - {periodo} | Total de registros: {len(datos)}', fontsize=14, pad=20)
            
            # Combinar leyendas
            lines1, labels1 = self.ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            self.ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)
            
            # Ajustar layout
            self.fig.tight_layout()
            
            # Actualizar canvas
            self.canvas.draw()
            
            print(f"Gráfico actualizado con {len(datos)} registros del período: {periodo}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar gráfico: {e}")
            print(f"Error detallado: {e}")
            
    def exportar_datos(self):
        """Exportar datos desde MySQL a CSV"""
        try:
            from tkinter import filedialog
            import csv
            
            archivo = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if archivo:
                # Consultar todos los datos
                self.cursor.execute('''
                    SELECT fecha_hora, temperatura, humedad, estado_ventana
                    FROM lecturas
                    ORDER BY fecha_hora
                ''')
                
                datos = self.cursor.fetchall()
                
                if archivo.endswith('.xlsx'):
                    try:
                        import pandas as pd
                        df = pd.DataFrame(datos, columns=['Fecha y Hora', 'Temperatura (°C)', 'Humedad (%)', 'Estado Ventana'])
                        df['Estado Ventana'] = df['Estado Ventana'].map({
                            0: 'CERRADA',
                            1: 'ABIERTA',
                            2: 'ABRIENDO',
                            3: 'CERRANDO'
                        })
                        df.to_excel(archivo, index=False)
                        mensaje = f"{len(datos)} registros exportados a Excel\n{archivo}"
                    except ImportError:
                        # Si no tiene pandas, guardar como CSV
                        with open(archivo.replace('.xlsx', '.csv'), 'w', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow(['Fecha y Hora', 'Temperatura (°C)', 'Parte Entera', 'Humedad (%)', 'Estado Ventana', 'Análisis'])
                            for fila in datos:
                                estado = "ABIERTA" if fila[3] == 1 else "CERRADA" if fila[3] == 0 else "DESCONOCIDO"
                                parte_entera = int(fila[1])
                                # Análisis de temperatura
                                if fila[1] >= 22.0 and fila[1] <= 22.9:
                                    analisis = "TEMP NORMAL"
                                elif fila[1] > 22.9:
                                    analisis = "TEMP ALTA (ABRIR)"
                                elif fila[1] < 22.0:
                                    analisis = "TEMP BAJA (CERRAR)"
                                else:
                                    analisis = "FUERA DE RANGO"
                                writer.writerow([fila[0], f"{fila[1]:.2f}", parte_entera, f"{fila[2]:.2f}", estado, analisis])
                        mensaje = f"{len(datos)} registros exportados a CSV\n{archivo.replace('.xlsx', '.csv')}"
                else:
                    # Guardar como CSV
                    with open(archivo, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Fecha y Hora', 'Temperatura (°C)', 'Parte Entera', 'Humedad (%)', 'Estado Ventana', 'Análisis'])
                        for fila in datos:
                            estado = "ABIERTA" if fila[3] == 1 else "CERRADA" if fila[3] == 0 else "DESCONOCIDO"
                            parte_entera = int(fila[1])
                            # Análisis de temperatura
                            if fila[1] >= 22.0 and fila[1] <= 22.9:
                                analisis = "TEMP NORMAL"
                            elif fila[1] > 22.9:
                                analisis = "TEMP ALTA (ABRIR)"
                            elif fila[1] < 22.0:
                                analisis = "TEMP BAJA (CERRAR)"
                            else:
                                analisis = "FUERA DE RANGO"
                            writer.writerow([fila[0], f"{fila[1]:.2f}", parte_entera, f"{fila[2]:.2f}", estado, analisis])
                    mensaje = f"{len(datos)} registros exportados a CSV\n{archivo}"
                
                messagebox.showinfo("Éxito", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}")
            
    def mostrar_estadisticas(self):
        """Mostrar estadísticas de los datos en MySQL"""
        try:
            # Consultas para estadísticas
            consultas = {
                "Total de registros": "SELECT COUNT(*) FROM lecturas",
                "Temperatura máxima": "SELECT MAX(temperatura) FROM lecturas",
                "Temperatura mínima": "SELECT MIN(temperatura) FROM lecturas",
                "Temperatura promedio": "SELECT AVG(temperatura) FROM lecturas",
                "Humedad promedio": "SELECT AVG(humedad) FROM lecturas",
                "Registros hoy": "SELECT COUNT(*) FROM lecturas WHERE DATE(fecha_hora) = CURDATE()",
                "Registros con temp normal (22.0-22.9°C)": "SELECT COUNT(*) FROM lecturas WHERE temperatura >= 22.0 AND temperatura <= 22.9",
                "Registros con temp alta (>22.9°C)": "SELECT COUNT(*) FROM lecturas WHERE temperatura > 22.9",
                "Registros con temp baja (<22.0°C)": "SELECT COUNT(*) FROM lecturas WHERE temperatura < 22.0",
                "Estado actual ventana": "SELECT estado_ventana FROM lecturas ORDER BY fecha_hora DESC LIMIT 1"
            }
            
            resultados = []
            for nombre, consulta in consultas.items():
                self.cursor.execute(consulta)
                resultado = self.cursor.fetchone()[0]
                
                if nombre == "Estado actual ventana":
                    estado_text = {
                        0: "CERRADA",
                        1: "ABIERTA",
                        2: "ABRIENDO",
                        3: "CERRANDO"
                    }.get(resultado, "DESCONOCIDO")
                    resultados.append(f"{nombre}: {estado_text}")
                else:
                    resultados.append(f"{nombre}: {resultado}")
            
            # Crear ventana de estadísticas
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Estadísticas de la Base de Datos")
            stats_window.geometry("450x400")
            
            tk.Label(stats_window, text="ESTADÍSTICAS MYSQL - ANÁLISIS DE TEMPERATURA", 
                    font=('Arial', 14, 'bold')).pack(pady=10)
            
            # Frame para resultados
            frame_resultados = tk.Frame(stats_window)
            frame_resultados.pack(fill='both', expand=True, padx=20, pady=10)
            
            # Mostrar cada estadística
            for resultado in resultados:
                tk.Label(frame_resultados, text=resultado, 
                        font=('Arial', 11), anchor='w', justify='left').pack(fill='x', pady=2)
            
            # Información sobre rango normal
            tk.Label(frame_resultados, text="\nRango de temperatura normal: 22.0°C - 22.9°C", 
                    font=('Arial', 11, 'italic'), foreground='blue', anchor='w').pack(fill='x', pady=(10, 2))
            
            # Botón para cerrar
            tk.Button(stats_window, text="CERRAR", 
                     command=stats_window.destroy, font=('Arial', 12)).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener estadísticas: {e}")
            
    def on_closing(self):
        """Manejar cierre de la aplicación"""
        self.desconectar()
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("Conexión a MySQL cerrada correctamente")
        self.root.destroy()

def main():
    root = tk.Tk()
    app = VentanaControlApp(root)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    style = ttk.Style()
    style.theme_use('clam')
    
    root.mainloop()

if __name__ == "__main__":
    main()