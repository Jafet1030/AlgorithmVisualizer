# =====================================================================
# main.py — Punto de entrada del Visualizador de Algoritmos de Grafos
# =====================================================================
# Ejecutar con:   python main.py
#
# Este archivo simplemente:
#   1. Crea la ventana principal (App).
#   2. Aplica estilos TTK personalizados.
#   3. Inicia el loop principal de Tkinter.
#
# Toda la lógica está distribuida en los demás módulos:
#   - config.py            → Colores, grafos de ejemplo
#   - grafo.py             → Modelo de datos y utilidades
#   - algorithms/          → Cada algoritmo en su propio archivo
#   - app.py               → Interfaz gráfica y animaciones
# =====================================================================

from tkinter import ttk
from config import COLORS
from app import App


def apply_ttk_style():
    """
    Configura el tema visual de los widgets ttk (Combobox, etc.)
    para que se integren con la paleta oscura de la aplicación.
    """
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(
        'TCombobox',
        fieldbackground=COLORS['bg_input'],
        background=COLORS['bg_input'],
        foreground=COLORS['text'],
        borderwidth=0,
        relief='flat'
    )


if __name__ == "__main__":
    app = App()
    apply_ttk_style()
    app.mainloop()
