import numpy as np
import matplotlib
# Usar backend TkAgg para incrustar Matplotlib en Tkinter
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import tkinter as tk
from tkinter import ttk

# --------------------
# PARÁMETROS GLOBALES
# --------------------
N = 5  # Número de términos a truncar en la serie
# Diccionario con casos predefinidos: clave->(a, b, V1, V2)
casos = {
    1: (1.0, 1.0, 100.0, 50.0),
    2: (1.0, 2.0, 100.0, 50.0),
    3: (1.0, 3.0, 100.0, 50.0),
    4: (4.0, 1.0, 100.0, 50.0)
}

# -------------------------------------
# CÁLCULO DEL POTENCIAL ELECTROSTÁTICO
# -------------------------------------
def potencial(X, Y, a, b, V1, V2, N):
    """
    Calcula el potencial V(x,y) usando los primeros N términos de la serie.
    La placa es de dimensiones a (en y) por b (en x). Bordes:
      V(x,0) = 0, V(x,a) = 0, V(0,y) = V1, V(b,y) = V2
    Parámetros:
      X, Y: mallas de coordenadas
      a, b: dimensiones de la placa
      V1, V2: potencial en las paredes laterales
      N: número de términos de la serie a sumar (truncamiento)
    Retorna:
      Matriz V con mismo shape que X, Y.
    """
    V = np.zeros_like(X)
    ns = np.arange(1, 2 * N, 2)  # n = 1, 3, 5, ..., (2N-1)
    coef = 4.0 / np.pi
    for n in ns:
        sinh_denom = np.sinh((n * np.pi * b) / a)
        # term1 asociado a V1 en x=0, term2 a V2 en x=b
        term1 = V1 * np.sinh((n * np.pi * (b - X)) / a)
        term2 = V2 * np.sinh((n * np.pi * X) / a)
        sin_y = np.sin((n * np.pi * Y) / a)
        V += coef * (1.0 / n) * ((term1 + term2) / sinh_denom) * sin_y
    return V

# ------------------------------------------
# GENERACIÓN DE DATOS (MALLA Y POTENCIAL)
# ------------------------------------------
def generar_datos(a, b, V1, V2):
    """
    Genera la malla (X, Y) y el potencial V para el caso especificado.
    - Resolución de 0.1 en x e y.
    Parámetros:
      a, b: dimensiones
      V1, V2: potenciales en los bordes laterales
    Retorna:
      xs, ys: vectores con coordenadas en x e y
      X, Y: mallas de coordenadas (np.meshgrid)
      V: matriz de potencial evaluado en la malla.
    """
    step = 0.1
    xs = np.arange(0, b + 1e-9, step)
    ys = np.arange(0, a + 1e-9, step)
    X, Y = np.meshgrid(xs, ys)
    V = potencial(X, Y, a, b, V1, V2, N)
    return xs, ys, X, Y, V

# ------------------------------------------
# MOSTRAR TABLA EN TKINTER (Treeview)
# ------------------------------------------
def mostrar_tabla(frame, xs, ys, V):
    """
    Muestra los valores de V(x,y) en un Treeview con scroll horizontal y vertical.
    Parameters:
      frame: contenedor donde se inserta la tabla
      xs, ys: vectores de coordenadas x e y
      V: matriz potencial
    """
    # Limpiar cualquier widget previo en el frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Crear subframe para scrollbars y tabla
    table_frame = ttk.Frame(frame)
    table_frame.pack(fill="both", expand=True)

    # Crear Treeview con todas las columnas (coordenadas x)
    tree = ttk.Treeview(table_frame)
    cols = [f"{x:.1f}" for x in xs]
    tree["columns"] = cols
    tree.heading("#0", text="y \\ x")
    tree.column("#0", width=50, anchor="center")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=60, anchor="center")

    # Insertar cada fila (coordenada y y valores de V)
    for i, y in enumerate(ys):
        valores = [f"{V[i, j]:.4f}" for j in range(len(xs))]
        tree.insert("", "end", text=f"{y:.1f}", values=valores)

    # Crear scrollbars
    x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(xscroll=x_scroll.set, yscroll=y_scroll.set)

    # Ubicar tabla y scrollbars en grid
    tree.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")

    # Ajustar pesos para que la tabla crezca con el frame
    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

# ------------------------------------------
# MOSTRAR CONTORNO 2D
# ------------------------------------------
def mostrar_contorno(frame, xs, ys, X, Y, V):
    """
    Muestra un contorno equipotencial 2D usando Matplotlib incrustado.
    Parameters:
      frame: contenedor donde se inserta la figura
      xs, ys: vectores de coordenadas (para ticks)
      X, Y, V: mallas y potencial calculado
    """
    # Limpiar contenido previo
    for widget in frame.winfo_children():
        widget.destroy()

    # Crear figura y ejes
    fig = plt.Figure(figsize=(7, 6))
    ax = fig.add_subplot(111)

    # Niveles de contorno uniformemente espaciados
    levels = np.linspace(V.min(), V.max(), 10)
    cf = ax.contourf(X, Y, V, levels=levels, cmap='plasma',
                     vmin=V.min(), vmax=V.max())
    cs = ax.contour(X, Y, V, levels=levels, colors='k', linewidths=0.8)
    ax.clabel(cs, inline=True, fontsize=6, fmt="%.0f")

    # Etiquetas y formato
    ax.set_xlabel('x', fontsize=8)
    ax.set_ylabel('y', fontsize=8)
    ax.set_aspect('equal', 'box')

    # Ticks con resolución 0.1 según el problema
    ax.set_xticks(xs)
    ax.set_yticks(ys)
    ax.tick_params(axis='x', labelsize=6)
    ax.tick_params(axis='y', labelsize=6)

    # Barra de color
    fig.colorbar(cf, ax=ax, label='V (volts)')

    # Incrustar en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# ------------------------------------------
# MOSTRAR SUPERFICIE 3D
# ------------------------------------------
def mostrar_superficie(frame, xs, ys, a, b, V1, V2):
    """
    Muestra la superficie 3D del potencial.
    Parameters:
      frame: contenedor donde se inserta la figura
      xs, ys: vectores coordenadas originales (para ticks)
      a, b, V1, V2: parámetros del problema para recalcular con malla fina
    """
    # Limpiar contenido previo
    for widget in frame.winfo_children():
        widget.destroy()

    fig = plt.Figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Malla más fina para suavizar superficie
    tstep = 0.02
    xs_plot = np.arange(0, b + 1e-9, tstep)
    ys_plot = np.arange(0, a + 1e-9, tstep)
    X_plot, Y_plot = np.meshgrid(xs_plot, ys_plot)
    V_plot = potencial(X_plot, Y_plot, a, b, V1, V2, N)

    surf = ax.plot_surface(
        X_plot, Y_plot, V_plot,
        rcount=len(ys_plot),
        ccount=len(xs_plot),
        cmap='viridis',
        edgecolor='none',
        antialiased=True,
        vmin=0, vmax=100
    )

    # Etiquetas y ticks
    ax.set_xlabel('x', fontsize=8)
    ax.set_ylabel('y', fontsize=8)
    ax.set_zlabel('V(x,y)', fontsize=8)
    # Ticks cada 0.5 en x e y para legibilidad
    ax.set_xticks(np.arange(0, b + 1e-9, 0.5))
    ax.set_yticks(np.arange(0, a + 1e-9, 0.5))
    ax.tick_params(axis='x', labelsize=6)
    ax.tick_params(axis='y', labelsize=6)
    ax.tick_params(axis='z', labelsize=6)
    ax.view_init(elev=30, azim=-60)

    # Barra de color
    fig.colorbar(surf, ax=ax, shrink=0.6, aspect=10, label='V (volts)')

    # Incrustar en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# ------------------------------------------
# INTERFAZ TKINTER: MENÚ PRINCIPAL (DEFENSIVO)
# ------------------------------------------
root = tk.Tk()
root.title("Menú de Resultados: Potencial Electrostático")
root.geometry("800x600")

# Panel superior: contiene selección de caso y botones
frame_menu = ttk.Frame(root)
frame_menu.pack(side="top", fill="x")

# Etiqueta y Combobox con validación básica
ttk.Label(frame_menu, text="Seleccionar Caso:").pack(side="left", padx=5)
combo_caso = ttk.Combobox(frame_menu, values=list(casos.keys()), width=5)
combo_caso.current(0)
combo_caso.pack(side="left", padx=5)
# Programación defensiva: asegurar que solo valores válidos sean seleccionables
combo_caso.config(state="readonly")  # evita entradas arbitrarias

# Botones para mostrar cada opción
btn_tabla = ttk.Button(frame_menu, text="Mostrar Tabla")
btn_contorno = ttk.Button(frame_menu, text="Mostrar Contorno")
btn_superficie = ttk.Button(frame_menu, text="Mostrar 3D")
btn_tabla.pack(side="left", padx=5)
btn_contorno.pack(side="left", padx=5)
btn_superficie.pack(side="left", padx=5)

# Panel inferior: área donde se mostrará la tabla o las gráficas
frame_display = ttk.Frame(root)
frame_display.pack(side="top", fill="both", expand=True)

# Función defensiva para actualizar pantalla
def actualizar_display(tipo):
    try:
        # Validar selección de caso
        caso_sel = int(combo_caso.get())
        if caso_sel not in casos:
            raise ValueError("Caso seleccionado no válido")

        a, b, V1, V2 = casos[caso_sel]
        xs, ys, X, Y, V = generar_datos(a, b, V1, V2)
        if tipo == 'tabla':
            mostrar_tabla(frame_display, xs, ys, V)
        elif tipo == 'contorno':
            mostrar_contorno(frame_display, xs, ys, X, Y, V)
        elif tipo == 'superficie':
            mostrar_superficie(frame_display, xs, ys, a, b, V1, V2)
        else:
            # En caso de mal uso, mostrar mensaje
            tk.messagebox.showerror("Error", f"Tipo desconocido: {tipo}")
    except Exception as e:
        # Manejo de errores en selección y generación de gráficos
        tk.messagebox.showerror("Error", f"Ha ocurrido un error: {e}")

# Asignar comandos a botones
btn_tabla.config(command=lambda: actualizar_display('tabla'))
btn_contorno.config(command=lambda: actualizar_display('contorno'))
btn_superficie.config(command=lambda: actualizar_display('superficie'))

# Iniciar bucle principal de Tkinter
root.mainloop()
