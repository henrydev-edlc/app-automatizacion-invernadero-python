import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime, timedelta
import json

class SistemaInvernadero:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control de Invernadero")
        self.root.geometry("600x500")
        self.root.configure(bg='#2c3e50')
        
        # Variables de estado del invernadero
        self.temperatura = 22.0
        self.humedad = 65.0
        
        # Estado de la ventana
        self.ventana_abierta = False
        self.temperatura_objetivo = 22.0
        
        # Historial de datos
        self.historial_completo = []  # Lista de diccionarios con todos los datos
        self.filtro_actual = "hora"  # hora, dia, semana, mes
        
        self.crear_interfaz()
        self.actualizar_sensores()
        
    def crear_interfaz(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        titulo = tk.Label(main_frame, text="🌿 SISTEMA DE CONTROL DE INVERNADERO", 
                         font=('Arial', 16, 'bold'), bg='#2c3e50', fg='white')
        titulo.pack(pady=(0, 20))
        
        # Frame para datos de sensores
        frame_sensores = tk.LabelFrame(main_frame, text="📊 SENSORES", 
                                      font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        frame_sensores.pack(fill='x', pady=(0, 15))
        
        self.crear_panel_sensores(frame_sensores)
        
        # Frame para estado de ventana
        frame_ventana = tk.LabelFrame(main_frame, text="🚪 CONTROL DE VENTANA", 
                                     font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        frame_ventana.pack(fill='x', pady=(0, 15))
        
        self.crear_panel_ventana(frame_ventana)
        
        # Frame para configuración
        frame_config = tk.LabelFrame(main_frame, text="⚡ CONFIGURACIÓN", 
                                    font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        frame_config.pack(fill='x', pady=(0, 15))
        
        self.crear_panel_configuracion(frame_config)
        
        # Frame para historial
        frame_historial = tk.LabelFrame(main_frame, text="📈 HISTORIAL", 
                                       font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        frame_historial.pack(fill='both', expand=True)
        
        self.crear_panel_historial(frame_historial)
        
    def crear_panel_sensores(self, parent):
        # Crear frame para los sensores
        grid_frame = tk.Frame(parent, bg='#34495e')
        grid_frame.pack(padx=15, pady=15, fill='x')
        
        # Sensor de temperatura
        tk.Label(grid_frame, text="Temperatura Actual:", bg='#34495e', fg='white', 
                font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=8)
        self.temp_label = tk.Label(grid_frame, text="22.0°C", bg='#34495e', fg='#e74c3c',
                                  font=('Arial', 14, 'bold'))
        self.temp_label.grid(row=0, column=1, sticky='w', padx=10, pady=8)
        
        # Sensor de humedad
        tk.Label(grid_frame, text="Humedad Ambiente:", bg='#34495e', fg='white',
                font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=8)
        self.hum_label = tk.Label(grid_frame, text="65.0%", bg='#34495e', fg='#3498db',
                                 font=('Arial', 14, 'bold'))
        self.hum_label.grid(row=1, column=1, sticky='w', padx=10, pady=8)
        
    def crear_panel_ventana(self, parent):
        grid_frame = tk.Frame(parent, bg='#34495e')
        grid_frame.pack(padx=15, pady=15, fill='x')
        
        # Estado de la ventana
        tk.Label(grid_frame, text="Estado Ventana:", bg='#34495e', fg='white',
                font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=8)
        
        self.ventana_label = tk.Label(grid_frame, text="CERRADA", bg='#e74c3c', fg='white',
                                     font=('Arial', 12, 'bold'), width=15)
        self.ventana_label.grid(row=0, column=1, padx=10, pady=8)
        
        # Temperatura objetivo
        tk.Label(grid_frame, text="Temperatura Objetivo:", bg='#34495e', fg='white',
                font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=8)
        
        self.objetivo_label = tk.Label(grid_frame, text="22.0°C", bg='#34495e', fg='#2ecc71',
                                      font=('Arial', 14, 'bold'))
        self.objetivo_label.grid(row=1, column=1, sticky='w', padx=10, pady=8)
        
    def crear_panel_configuracion(self, parent):
        grid_frame = tk.Frame(parent, bg='#34495e')
        grid_frame.pack(padx=15, pady=15, fill='x')
        
        # Configurar temperatura objetivo
        tk.Label(grid_frame, text="Temperatura Objetivo (°C):", bg='#34495e', fg='white',
                font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5)
        
        self.objetivo_entry = tk.Entry(grid_frame, width=10, font=('Arial', 10))
        self.objetivo_entry.insert(0, "22.0")
        self.objetivo_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Botón aplicar configuración
        aplicar_btn = tk.Button(grid_frame, text="Aplicar Configuración", 
                               command=self.aplicar_configuracion,
                               bg='#27ae60', fg='white', font=('Arial', 10))
        aplicar_btn.grid(row=0, column=2, padx=10, pady=5)
        
    def crear_panel_historial(self, parent):
        # Frame para controles de filtro
        frame_filtros = tk.Frame(parent, bg='#34495e')
        frame_filtros.pack(fill='x', padx=10, pady=5)
        
        # Botones de filtro
        tk.Label(frame_filtros, text="Filtrar por:", bg='#34495e', fg='white',
                font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        self.filtro_hora = tk.Button(frame_filtros, text="Última Hora", 
                                    command=lambda: self.cambiar_filtro("hora"),
                                    bg='#3498db', fg='white', font=('Arial', 8))
        self.filtro_hora.pack(side=tk.LEFT, padx=2)
        
        self.filtro_dia = tk.Button(frame_filtros, text="Último Día", 
                                   command=lambda: self.cambiar_filtro("dia"),
                                   bg='#34495e', fg='white', font=('Arial', 8))
        self.filtro_dia.pack(side=tk.LEFT, padx=2)
        
        self.filtro_semana = tk.Button(frame_filtros, text="Última Semana", 
                                      command=lambda: self.cambiar_filtro("semana"),
                                      bg='#34495e', fg='white', font=('Arial', 8))
        self.filtro_semana.pack(side=tk.LEFT, padx=2)
        
        self.filtro_mes = tk.Button(frame_filtros, text="Último Mes", 
                                   command=lambda: self.cambiar_filtro("mes"),
                                   bg='#34495e', fg='white', font=('Arial', 8))
        self.filtro_mes.pack(side=tk.LEFT, padx=2)
        
        # Botón exportar
        exportar_btn = tk.Button(frame_filtros, text="Exportar Historial", 
                                command=self.exportar_historial,
                                bg='#e67e22', fg='white', font=('Arial', 8))
        exportar_btn.pack(side=tk.RIGHT, padx=5)
        
        # Text widget para mostrar historial
        self.historial_text = tk.Text(parent, height=8, bg='#1c2833', fg='white',
                                     font=('Courier New', 9))
        self.historial_text.pack(padx=10, pady=5, fill='both', expand=True)
        
        # Scrollbar para el historial
        scrollbar = tk.Scrollbar(self.historial_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.historial_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.historial_text.yview)
        
    def cambiar_filtro(self, filtro):
        self.filtro_actual = filtro
        
        # Actualizar colores de botones
        botones = {
            "hora": self.filtro_hora,
            "dia": self.filtro_dia,
            "semana": self.filtro_semana,
            "mes": self.filtro_mes
        }
        
        for key, boton in botones.items():
            if key == filtro:
                boton.config(bg='#3498db')
            else:
                boton.config(bg='#34495e')
        
        self.actualizar_historial()
        
    def aplicar_configuracion(self):
        try:
            nueva_temperatura = float(self.objetivo_entry.get())
            self.temperatura_objetivo = nueva_temperatura
            self.objetivo_label.config(text=f"{nueva_temperatura}°C")
            messagebox.showinfo("Configuración", f"Temperatura objetivo actualizada a {nueva_temperatura}°C")
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un valor numérico válido")
            
    def controlar_ventana(self):
        # Lógica de control automático
        if self.temperatura > self.temperatura_objetivo and not self.ventana_abierta:
            # Abrir ventana si la temperatura es mayor al objetivo
            self.ventana_abierta = True
            self.ventana_label.config(text="ABIERTA", bg='#27ae60')
            
        elif self.temperatura <= self.temperatura_objetivo and self.ventana_abierta:
            # Cerrar ventana si la temperatura es menor o igual al objetivo
            self.ventana_abierta = False
            self.ventana_label.config(text="CERRADA", bg='#e74c3c')
            
    def actualizar_sensores(self):
        # Simular lectura de sensores con variación aleatoria
        self.temperatura += random.uniform(-0.8, 0.8)
        self.humedad += random.uniform(-3, 3)
        
        # Mantener valores dentro de rangos razonables
        self.temperatura = max(15, min(35, self.temperatura))
        self.humedad = max(30, min(90, self.humedad))
        
        # Actualizar labels
        self.temp_label.config(text=f"{self.temperatura:.1f}°C")
        self.hum_label.config(text=f"{self.humedad:.1f}%")
        
        # Control automático de ventana
        self.controlar_ventana()
        
        # Guardar en historial
        self.guardar_dato_historial()
        
        # Actualizar visualización del historial
        self.actualizar_historial()
        
        # Programar próxima actualización
        self.root.after(3000, self.actualizar_sensores)  # Actualizar cada 3 segundos
        
    def guardar_dato_historial(self):
        """Guarda un nuevo dato en el historial completo"""
        dato = {
            'timestamp': datetime.now(),
            'temperatura': self.temperatura,
            'humedad': self.humedad,
            'ventana_abierta': self.ventana_abierta
        }
        self.historial_completo.append(dato)
        
        # Mantener máximo 1000 registros para no consumir mucha memoria
        if len(self.historial_completo) > 1000:
            self.historial_completo = self.historial_completo[-1000:]
    
    def filtrar_historial(self):
        """Filtra el historial según el filtro actual"""
        ahora = datetime.now()
        historial_filtrado = []
        
        for dato in self.historial_completo:
            diferencia = ahora - dato['timestamp']
            
            if self.filtro_actual == "hora" and diferencia <= timedelta(hours=1):
                historial_filtrado.append(dato)
            elif self.filtro_actual == "dia" and diferencia <= timedelta(days=1):
                historial_filtrado.append(dato)
            elif self.filtro_actual == "semana" and diferencia <= timedelta(weeks=1):
                historial_filtrado.append(dato)
            elif self.filtro_actual == "mes" and diferencia <= timedelta(days=30):
                historial_filtrado.append(dato)
        
        return historial_filtrado
    
    def actualizar_historial(self):
        """Actualiza la visualización del historial con los datos filtrados"""
        historial_filtrado = self.filtrar_historial()
        
        # Actualizar texto del historial
        self.historial_text.delete(1.0, tk.END)
        
        # Encabezado
        self.historial_text.insert(tk.END, "Fecha y Hora       | Temp  | Hum  | Ventana\n")
        self.historial_text.insert(tk.END, "-------------------|-------|------|---------\n")
        
        # Mostrar datos (máximo 50 registros para no saturar)
        for dato in historial_filtrado[-50:]:
            fecha_str = dato['timestamp'].strftime("%m/%d %H:%M:%S")
            estado_ventana = "ABIERTA" if dato['ventana_abierta'] else "CERRADA"
            line = f"{fecha_str} | " \
                   f"{dato['temperatura']:.1f}°C | " \
                   f"{dato['humedad']:.1f}% | " \
                   f"{estado_ventana}\n"
            self.historial_text.insert(tk.END, line)
            
        # Mostrar estadísticas
        if historial_filtrado:
            temp_promedio = sum(d['temperatura'] for d in historial_filtrado) / len(historial_filtrado)
            hum_promedio = sum(d['humedad'] for d in historial_filtrado) / len(historial_filtrado)
            
            self.historial_text.insert(tk.END, f"\n--- ESTADÍSTICAS ({self.filtro_actual.upper()}) ---\n")
            self.historial_text.insert(tk.END, f"Registros: {len(historial_filtrado)}\n")
            self.historial_text.insert(tk.END, f"Temp promedio: {temp_promedio:.1f}°C\n")
            self.historial_text.insert(tk.END, f"Hum promedio: {hum_promedio:.1f}%\n")
        
    def exportar_historial(self):
        """Exporta el historial completo a un archivo JSON"""
        try:
            filename = f"historial_invernadero_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Convertir datetime a string para JSON
            historial_exportable = []
            for dato in self.historial_completo:
                dato_exportable = dato.copy()
                dato_exportable['timestamp'] = dato['timestamp'].isoformat()
                historial_exportable.append(dato_exportable)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(historial_exportable, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Exportación Exitosa", f"Historial exportado a: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el historial: {str(e)}")

def main():
    root = tk.Tk()
    app = SistemaInvernadero(root)
    root.mainloop()

if __name__ == "__main__":
    main()