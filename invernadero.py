import tkinter as tk
from tkinter import *
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random
import datetime

# ============================================================
#                  BASE DE DATOS SIMPLIFICADA
# ============================================================

usuarios = {
    "usuario": "usuario"
}

# ============================================================
#          INTERFAZ UNIFICADA LOGIN / REGISTRO
# ============================================================

def mostrar_login():
    limpiar_ventana(auth_win)

    Label(auth_win, text="INICIO DE SESIÓN", fg="white", bg="#1B4332",
          font=("Arial", 18, "bold")).pack(pady=20)

    global entrada_usuario, entrada_password

    frame = Frame(auth_win, bg="#1B4332")
    frame.pack()

    Label(frame, text="Usuario:", bg="#1B4332", fg="white", font=("Arial", 12)).grid(row=0, column=0, pady=10)
    entrada_usuario = Entry(frame, font=("Arial", 12))
    entrada_usuario.grid(row=0, column=1, pady=10)

    Label(frame, text="Contraseña:", bg="#1B4332", fg="white", font=("Arial", 12)).grid(row=1, column=0, pady=10)
    entrada_password = Entry(frame, font=("Arial", 12), show="*")
    entrada_password.grid(row=1, column=1, pady=10)

    Button(auth_win, text="Entrar", bg="#52B788", fg="white", font=("Arial", 12, "bold"),
           command=validar_login).pack(pady=15)

    Button(auth_win, text="Registrarse", bg="#40916C", fg="white",
           font=("Arial", 12, "bold"), command=mostrar_registro).pack()


def mostrar_registro():
    limpiar_ventana(auth_win)

    Label(auth_win, text="REGISTRO DE USUARIO", fg="white", bg="#1B4332",
          font=("Arial", 18, "bold")).pack(pady=20)

    global reg_user, reg_pass

    frame = Frame(auth_win, bg="#1B4332")
    frame.pack()

    Label(frame, text="Nuevo Usuario:", bg="#1B4332", fg="white", font=("Arial", 12)).grid(row=0, column=0, pady=10)
    reg_user = Entry(frame, font=("Arial", 12))
    reg_user.grid(row=0, column=1, pady=10)

    Label(frame, text="Contraseña:", bg="#1B4332", fg="white", font=("Arial", 12)).grid(row=1, column=0, pady=10)
    reg_pass = Entry(frame, font=("Arial", 12), show="*")
    reg_pass.grid(row=1, column=1, pady=10)

    Button(auth_win, text="Crear Cuenta", bg="#FF4D6D", fg="white",
           font=("Arial", 12, "bold"), command=crear_usuario).pack(pady=10)

    Button(auth_win, text="Volver", bg="#2D6A4F", fg="white", font=("Arial", 12, "bold"),
           command=mostrar_login).pack()


def validar_login():
    usuario = entrada_usuario.get()
    password = entrada_password.get()

    if usuario in usuarios and usuarios[usuario] == password:
        auth_win.destroy()
        ventana_invernadero()
    else:
        messagebox.showerror("Error", "Credenciales incorrectas.")


def crear_usuario():
    user = reg_user.get().strip()
    password = reg_pass.get().strip()

    if user == "" or password == "":
        messagebox.showwarning("Advertencia", "Llene todos los campos.")
        return

    if user in usuarios:
        messagebox.showerror("Error", "Ese usuario ya existe.")
        return

    if password in usuarios.values():
        messagebox.showerror("Error", "Esa contraseña ya fue utilizada.")
        return

    usuarios[user] = password
    messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
    mostrar_login()


# Limpia widgets de una ventana
def limpiar_ventana(win):
    for widget in win.winfo_children():
        widget.destroy()


# ============================================================
#       CREAR VENTANA PRINCIPAL DE LOGIN/REGISTRO
# ============================================================

def ventana_login():
    global auth_win
    auth_win = Tk()
    auth_win.title("Autenticación - Invernadero")
    auth_win.geometry("400x380")
    auth_win.configure(bg="#1B4332")

    mostrar_login()
    auth_win.mainloop()


# ============================================================
#                      PANEL PRINCIPAL
# ============================================================

def ventana_invernadero():
    global panel_invernadero, root

    root = Tk()
    root.title("Panel del Invernadero")
    root.geometry("1000x600")
    root.configure(bg="#2D6A4F")

    top_frame = Frame(root, bg="#2D6A4F")
    top_frame.pack(fill="x")

    Label(top_frame, text="INVERNADERO INTELIGENTE", bg="#2D6A4F",
          fg="white", font=("Arial", 22, "bold")).pack(side="left", padx=20, pady=10)

    Button(top_frame, text="Cerrar Sesión", bg="#FF4D6D", fg="white",
           font=("Arial", 12, "bold"), command=cerrar_sesion).pack(side="right", padx=20)

    panel_invernadero = Frame(root, bg="#40916C")
    panel_invernadero.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    Label(panel_invernadero, text="Temperatura Actual:", bg="#40916C",
          fg="white", font=("Arial", 16)).pack(pady=5)

    Label(panel_invernadero, text="Humedad Actual:", bg="#40916C",
          fg="white", font=("Arial", 16)).pack(pady=5)

    crear_grafica(panel_invernadero)
    root.after(2000, actualizar_grafica)

    crear_panel_historial(root)

    root.mainloop()


def cerrar_sesion():
    root.destroy()
    ventana_login()


# ============================================================
#                    GRÁFICA EN TIEMPO REAL
# ============================================================

historial_temperatura = []
historial_humedad = []
historial_tiempo = []

def crear_grafica(panel):
    global fig, ax_temp, canvas

    fig = Figure(figsize=(6, 3), dpi=100)
    ax_temp = fig.add_subplot(111)

    ax_temp.set_facecolor("#1B4332")
    fig.set_facecolor("#1B4332")
    ax_temp.tick_params(colors="white")
    ax_temp.set_title("Temperatura & Humedad", color="white")

    canvas = FigureCanvasTkAgg(fig, master=panel)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)


def actualizar_grafica():
    temperatura = random.randint(18, 32)
    humedad = random.randint(40, 90)
    tiempo = datetime.datetime.now().strftime("%H:%M:%S")

    historial_temperatura.append(temperatura)
    historial_humedad.append(humedad)
    historial_tiempo.append(tiempo)

    if len(historial_tiempo) > 20:
        historial_temperatura.pop(0)
        historial_humedad.pop(0)
        historial_tiempo.pop(0)

    ax_temp.clear()
    ax_temp.plot(historial_tiempo, historial_temperatura, marker="o", color="#FF6B6B", label="°C")
    ax_temp.plot(historial_tiempo, historial_humedad, marker="o", color="#4D96FF", label="%")

    ax_temp.set_facecolor("#1B4332")
    ax_temp.tick_params(colors="white")
    ax_temp.set_title("Temperatura & Humedad", color="white")
    ax_temp.legend(facecolor="#40916C", labelcolor="white")

    canvas.draw()

    panel_invernadero.after(2000, actualizar_grafica)


# ============================================================
#                        HISTORIAL
# ============================================================

def mostrar_historial(filtro):
    historial_frame.delete(0, "end")

    for i in range(len(historial_tiempo)):
        registro = f"{historial_tiempo[i]}  |  {historial_temperatura[i]}°C  |  {historial_humedad[i]}%"
        historial_frame.insert("end", registro)


def crear_panel_historial(root):
    global historial_frame

    panel = Frame(root, bg="#1B4332")
    panel.pack(side="right", fill="y", padx=10)

    Label(panel, text="HISTORIAL", bg="#1B4332", fg="white",
          font=("Arial", 18, "bold")).pack(pady=10)

    Button(panel, text="Por Hora", bg="#FF4D6D", fg="white",
           command=lambda: mostrar_historial("hora")).pack(fill="x", pady=5)
    Button(panel, text="Por Día", bg="#FF4D6D", fg="white",
           command=lambda: mostrar_historial("dia")).pack(fill="x", pady=5)
    Button(panel, text="Por Semana", bg="#FF4D6D", fg="white",
           command=lambda: mostrar_historial("semana")).pack(fill="x", pady=5)
    Button(panel, text="Por Mes", bg="#FF4D6D", fg="white",
           command=lambda: mostrar_historial("mes")).pack(fill="x", pady=5)

    historial_frame = Listbox(panel, width=35, height=25, bg="#2D6A4F", fg="white")
    historial_frame.pack(pady=20)


# ============================================================
#                      EJECUTAR APP
# ============================================================

ventana_login()
