import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime

class SistemaInvernadero:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control de Invernadero")
        self.root.geometry("500x400")
        self.root.configure(bg='#2c3e50')
        
        # Variables de estado del invernadero
        self.temperatura = 22.0
        self.humedad = 65.0
        
        # Estado de la ventana
        self.ventana_abierta = False
        self.temperatura_objetivo = 22.0
        
        # Historial de datos
        self.historial = {
            'temperatura': [],
            'humedad': [],
            'timestamp': []
        }
        
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
        # Text widget para mostrar historial
        self.historial_text = tk.Text(parent, height=6, bg='#1c2833', fg='white',
                                     font=('Courier New', 9))
        self.historial_text.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Scrollbar para el historial
        scrollbar = tk.Scrollbar(self.historial_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.historial_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.historial_text.yview)
        
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
        
        # Actualizar historial
        self.actualizar_historial()
        
        # Programar próxima actualización
        self.root.after(3000, self.actualizar_sensores)  # Actualizar cada 3 segundos
        
    def actualizar_historial(self):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Agregar datos al historial
        self.historial['temperatura'].append(self.temperatura)
        self.historial['humedad'].append(self.humedad)
        self.historial['timestamp'].append(timestamp)
        
        # Mantener solo los últimos 8 registros
        if len(self.historial['timestamp']) > 8:
            for key in self.historial:
                self.historial[key] = self.historial[key][-8:]
        
        # Actualizar texto del historial
        self.historial_text.delete(1.0, tk.END)
        self.historial_text.insert(tk.END, "Hora      | Temp  | Hum  | Ventana\n")
        self.historial_text.insert(tk.END, "----------|-------|------|---------\n")
        
        for i in range(len(self.historial['timestamp'])):
            estado_ventana = "ABIERTA" if self.ventana_abierta else "CERRADA"
            line = f"{self.historial['timestamp'][i]} | " \
                   f"{self.historial['temperatura'][i]:.1f}°C | " \
                   f"{self.historial['humedad'][i]:.1f}% | " \
                   f"{estado_ventana}\n"
            self.historial_text.insert(tk.END, line)

def main():
    root = tk.Tk()
    app = SistemaInvernadero(root)
    root.mainloop()

if __name__ == "__main__":
    main()