# =====================================================================
# config.py — Configuración global del visualizador
# =====================================================================
# Este módulo centraliza toda la configuración visual y los datos
# de ejemplo. Si se quiere cambiar la apariencia (colores, fuentes)
# o agregar grafos predeterminados, solo se modifica este archivo.
# =====================================================================

import matplotlib
import matplotlib.pyplot as plt

# Forzar backend TkAgg para que matplotlib dibuje dentro de Tkinter
matplotlib.use('TkAgg')


# =====================================================================
# CONFIGURACIÓN DE MATPLOTLIB
# =====================================================================
# Estas opciones definen el estilo oscuro general de las figuras.
plt.rcParams['figure.facecolor'] = '#1a1a2e'   # Fondo de la figura
plt.rcParams['axes.facecolor']   = '#16213e'   # Fondo del área de dibujo
plt.rcParams['font.family']      = 'sans-serif'
plt.rcParams['font.sans-serif']  = ['DejaVu Sans', 'Arial']


# =====================================================================
# PALETA DE COLORES
# =====================================================================
# Diccionario único con todos los colores usados en la interfaz y
# en las visualizaciones de grafos. Cambiar un valor aquí se refleja
# en toda la aplicación.
# =====================================================================
COLORS = {
    # --- Fondos ---
    'bg_dark':       '#0f0f1a',    # Fondo principal de la ventana
    'bg_panel':      '#1a1a2e',    # Fondo del panel lateral izquierdo
    'bg_card':       '#16213e',    # Fondo del área donde se dibuja el grafo
    'bg_input':      '#0f3460',    # Fondo de campos de entrada / botones secundarios

    # --- Acentos ---
    'accent':        '#e94560',    # Rojo/rosa principal (botón ejecutar, nodos visitados)
    'accent2':       '#0f3460',    # Azul oscuro (botones secundarios)
    'accent3':       '#533483',    # Morado (botón detener, DFS visitados)
    'teal':          '#00b4d8',    # Cian/teal (nodo actual en A*)
    'green':         '#2ecc71',    # Verde (camino final encontrado)
    'orange':        '#f39c12',    # Naranja (nodo actual, destino)

    # --- Texto ---
    'text':          '#000000',    # Texto oscuro (para combos con fondo claro)
    'text1':         '#eaeaea',    # Texto claro principal
    'text_dim':      '#8892a0',    # Texto atenuado (subtítulos, etiquetas)
    'text_bright':   '#ffffff',    # Texto blanco brillante (títulos)

    # --- Bordes ---
    'border':        '#2a2a4a',    # Bordes y separadores

    # --- Nodos del grafo ---
    'node_default':  '#00b4d8',    # Color base de nodos (cian)
    'node_visit':    '#e94560',    # Nodo ya visitado (rojo/rosa)
    'node_current':  '#f39c12',    # Nodo siendo procesado (naranja)

    # --- Aristas del grafo ---
    'edge_default':  '#2a2a4a',    # Arista normal (gris oscuro)
    'edge_highlight':'#e94560',    # Arista resaltada durante exploración
    'edge_path':     '#2ecc71',    # Arista del camino solución (verde)
}


# =====================================================================
# GRAFOS DE EJEMPLO
# =====================================================================
# Cada entrada tiene:
#   - "matriz": matriz de adyacencia simétrica (0 = sin conexión)
#   - "nombres": etiquetas de los nodos (deben coincidir en cantidad
#                con las filas/columnas de la matriz)
#
# Para agregar un grafo nuevo, simplemente añade otra entrada al dict.
# =====================================================================
GRAFOS_EJEMPLO = {
    "Grafo 1 — 11 nodos": {
        "matriz": [
            [0,  8,  0,  0,  0,  0,  9, 10,  6, 12,  3],
            [8,  0, 10,  0,  2,  0,  0,  0,  0,  0,  7],
            [0, 10,  0,  9,  0,  0,  0,  0,  0,  0,  5],
            [0,  0,  9,  0, 13, 12,  0,  0,  0,  0,  0],
            [0,  2,  0, 13,  0, 10,  6,  0,  0,  0,  0],
            [0,  0,  0, 12, 10,  0,  8,  0,  0,  0,  0],
            [9,  0,  0,  0,  6,  8,  0,  7,  0,  0,  0],
            [10, 0,  0,  0,  0,  0,  7,  0,  3,  0,  0],
            [6,  0,  0,  0,  0,  0,  0,  3,  0, 10,  0],
            [12, 0,  0,  0,  0,  0,  0,  0, 10,  0,  8],
            [3,  7,  5,  0,  0,  0,  0,  0,  0,  8,  0],
        ],
        "nombres": ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    },
    "Grafo 2 — 7 nodos": {
        "matriz": [
            [0,  4,  0,  0,  0,  0,  0],
            [4,  0,  8,  0,  0,  0, 11],
            [0,  8,  0,  7,  0,  4,  0],
            [0,  0,  7,  0,  9, 14,  0],
            [0,  0,  0,  9,  0, 10,  0],
            [0,  0,  4, 14, 10,  0,  2],
            [0, 11,  0,  0,  0,  2,  0],
        ],
        "nombres": ['S', 'T', 'U', 'V', 'W', 'X', 'Y']
    }
}
