import customtkinter as ctk
from grafica import historial_temperatura, historial_humedad, historial_tiempo

historial_box = None


def filtrar(filtro):
    historial_box.delete(0, "end")

    for i in range(len(historial_tiempo)):
        registro = f"{historial_tiempo[i]}  |  {historial_temperatura[i]}°C  |  {historial_humedad[i]}%"
        historial_box.insert("end", registro)


def crear_panel_historial(root):
    global historial_box

    panel = ctk.CTkFrame(root, width=250, height=600, fg_color="#40916C", corner_radius=15)
    panel.place(x=720, y=100)

    title = ctk.CTkLabel(panel, text="Historial", font=("Montserrat", 22, "bold"), text_color="white")
    title.pack(pady=10)

    # Botones de filtros
    ctk.CTkButton(panel, text="Por Hora", fg_color="#FF4D6D",
                  command=lambda: filtrar("hora")).pack(fill="x", pady=5)

    ctk.CTkButton(panel, text="Por Día", fg_color="#FF4D6D",
                  command=lambda: filtrar("dia")).pack(fill="x", pady=5)

    ctk.CTkButton(panel, text="Por Semana", fg_color="#FF4D6D",
                  command=lambda: filtrar("semana")).pack(fill="x", pady=5)

    ctk.CTkButton(panel, text="Por Mes", fg_color="#FF4D6D",
                  command=lambda: filtrar("mes")).pack(fill="x", pady=5)

    historial_box = ctk.CTkTextbox(panel, width=220, height=350, fg_color="#1B4332", text_color="white")
    historial_box.pack(pady=15)
