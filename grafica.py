import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random
import datetime

# ----------- LISTAS PARA GUARDAR EL HISTORIAL --------------
historial_temperatura = []
historial_humedad = []
historial_tiempo = []

fig = None
ax_temp = None
canvas = None


# -------------- GRÁFICA EN TIEMPO REAL ---------------------
def crear_grafica(panel):
    global fig, ax_temp, canvas

    fig = Figure(figsize=(6, 3), dpi=100)

    ax_temp = fig.add_subplot(111)
    ax_temp.set_title("Temperatura y Humedad en Tiempo Real", color="#F0F0F0")
    ax_temp.set_facecolor("#1B4332")
    fig.set_facecolor("#1B4332")

    ax_temp.tick_params(colors="white")

    canvas = FigureCanvasTkAgg(fig, master=panel)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)


def actualizar_grafica(panel):
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
    ax_temp.plot(historial_tiempo, historial_temperatura, marker='o', color="#FF6B6B", label="Temperatura °C")
    ax_temp.plot(historial_tiempo, historial_humedad, marker='o', color="#4D96FF", label="Humedad %")

    ax_temp.set_title("Temperatura y Humedad en Tiempo Real", color="white")
    ax_temp.set_facecolor("#1B4332")
    ax_temp.tick_params(colors="white")
    ax_temp.legend(facecolor="#40916C", edgecolor="white", labelcolor="white")

    canvas.draw()

    panel.after(2000, lambda: actualizar_grafica(panel))
