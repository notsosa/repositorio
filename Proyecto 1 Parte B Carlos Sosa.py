import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def reflejar_recta(z, alpha_rad): #Esta funcion refleja un punto z en una recta que forma un ángulo alpha_rad con el eje x.

    return np.exp(2j * alpha_rad) * np.conjugate(z) #Como la reflexión en una recta es equivalente a rotar el punto z, reflejarlo respecto al eje x, y luego rotarlo de nuevo, usamos la exponencial compleja para realizar esta operación de forma eficiente.


def generar_imagenes_cuña(z0, phi_rad, N): #Esta funcion genera las imágenes de una carga z0 en un plano conductor, reflejando en un ángulo phi_rad y generando N imágenes.

    imgs = []
    signs = []
    # Para la carga original k=0, signo +1 (se asume signo del usuario fuera de esta función)
    imgs.append(z0)
    signs.append(1)
    for k in range(1, N+1):
        # Posición de la imagen
        if (k % 2) == 1:
            z_new = reflejar_recta(imgs[-1], phi_rad)
        else:
            z_new = reflejar_recta(imgs[-1], 0.0)
        imgs.append(z_new)
        # Signo alterna: signo_k = (-1)^k
        signs.append((-1)**k)
    return list(zip(imgs, signs))


def calcular_y_graficar():
    try:
        # Obtener valores de la interfaz
        x = float(entry_x.get())
        y = float(entry_y.get())
        signo = var_signo.get()
        phi_deg = float(entry_phi.get())
        
        if signo not in ['+', '-']:
            raise ValueError("Signo inválido. Ingrese '+' o '-'.")
        if phi_deg <= 0 or phi_deg >= 360:
            raise ValueError("φ debe estar entre 0 y 360.")
        
        # Calcular número de imágenes según N = 360/φ - 1
        cociente = 360.0 / phi_deg
        if abs(round(cociente) - cociente) > 1e-6:
            raise ValueError("φ debe dividir exactamente a 360° para que N sea entero.")
        N = int(cociente - 1)
        
        # Convertir a número complejo y radianes
        z0 = x + 1j * y
        phi_rad = phi_deg * np.pi / 180.0
        
        # Generar listas de imágenes y sus signos (1: igual que original, -1: signo opuesto)
        imgs_signs = generar_imagenes_cuña(z0, phi_rad, N)
        # imgs_signs[0] es (z0, +1), para índices 1..N se alternan (+1, -1,...)
        
        # Extraer coordenadas y signos normalizados según signo usuario
        coords = []  # lista de (x_k, y_k, signo_real_k)
        orig_sign_factor = 1 if signo == '+' else -1
        for (z_k, factor) in imgs_signs:
            # factor = (-1)^k ; signo_usuario*factor = signo real de z_k
            actual_factor = orig_sign_factor * factor
            coords.append((np.real(z_k), np.imag(z_k), actual_factor))
        
        # Graficar
        fig.clear()
        ax = fig.add_subplot(111)
        
        # Dibujar fronteras de la cuña (dos rectas)
        ax.plot([0, 2], [0, 0], 'k--', lw=1.5)
        ax.plot([0, 2 * np.cos(phi_rad)], [0, 2 * np.sin(phi_rad)], 'k--', lw=1.5)
        
        # Dibujar carga e imágenes según signo
        # Separar en dos grupos para colores
        xs_pos, ys_pos = [], []
        xs_neg, ys_neg = [], []
        labels_pos = False
        labels_neg = False
        for idx, (xk, yk, factor) in enumerate(coords):
            if factor == 1:
                xs_pos.append(xk)
                ys_pos.append(yk)
                if not labels_pos:
                    label_pos = "Imagen+"
                    labels_pos = True
            else:
                xs_neg.append(xk)
                ys_neg.append(yk)
                if not labels_neg:
                    label_neg = "Imagen-"
                    labels_neg = True
        
        if xs_pos:
            ax.scatter(xs_pos, ys_pos, c='red', s=80, marker='o', label=label_pos)
        if xs_neg:
            ax.scatter(xs_neg, ys_neg, c='blue', s=50, marker='x', label=label_neg)
        
        # Etiquetar índices de imágenes (para verificar orden)
        for k, (xk, yk, _) in enumerate(coords):
            ax.text(xk * 1.05, yk * 1.05, str(k), fontsize=9)
        
        # Ajustes estéticos
        ax.set_aspect('equal', 'box')
        all_xs = [c[0] for c in coords]
        all_ys = [c[1] for c in coords]
        margen = max(max(map(abs, all_xs)), max(map(abs, all_ys)), 1) + 1
        ax.set_xlim(-margen, margen)
        ax.set_ylim(-margen, margen)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title(f"Imágenes para el plano φ = {phi_deg}°, N = {N}")
        ax.grid(alpha=0.3)
        ax.legend()
        
        canvas.draw()
        
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Configuración principal de la ventana Tkinter
root = tk.Tk()
root.title("Método de Imágenes en un plano Conductor")
root.geometry("800x600")

# Frame de entrada de datos (ahora centrado)
entrada_frame = tk.Frame(root)
entrada_frame.pack(side=tk.TOP, pady=10)

# Coordenada x
tk.Label(entrada_frame, text="Coordenada x:").grid(row=0, column=0, sticky='e')
entry_x = tk.Entry(entrada_frame, width=10)
entry_x.grid(row=0, column=1, padx=5)

# Coordenada y
tk.Label(entrada_frame, text="Coordenada y:").grid(row=1, column=0, sticky='e')
entry_y = tk.Entry(entrada_frame, width=10)
entry_y.grid(row=1, column=1, padx=5)

# Signo de la carga
tk.Label(entrada_frame, text="Signo (+/-):").grid(row=2, column=0, sticky='e')
var_signo = tk.StringVar(value='+')
entry_signo = tk.Entry(entrada_frame, textvariable=var_signo, width=3)
entry_signo.grid(row=2, column=1, padx=5)

# Ángulo phi
tk.Label(entrada_frame, text="Ángulo φ (grados):").grid(row=3, column=0, sticky='e')
entry_phi = tk.Entry(entrada_frame, width=10)
entry_phi.grid(row=3, column=1, padx=5)

# Botón para calcular
tk.Button(entrada_frame, text="Calcular", command=calcular_y_graficar).grid(row=4, column=0, columnspan=2, pady=5)

# Área de figura Matplotlib
def crear_figura():
    fig = plt.Figure(facecolor='white')
    return fig

# Crear figura y canvas para mostrarla en Tkinter
fig = crear_figura()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

root.mainloop()
