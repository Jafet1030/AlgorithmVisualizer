# =====================================================================
# app.py — Interfaz gráfica principal del Visualizador de Grafos
# =====================================================================
# Contiene la clase App (hereda de tk.Tk) que maneja:
#   - Construcción del layout (panel izquierdo de controles + canvas)
#   - Carga y selección de grafos
#   - Selección de algoritmo y parámetros (origen, destino, velocidad)
#   - Renderizado de frames de animación (genérico y especial Bellman-Ford)
#   - Animación paso a paso usando FuncAnimation de matplotlib
#
# Nota: Si un algoritmo no se pudo cargar (ver algorithms/__init__.py),
# el botón EJECUTAR mostrará un mensaje de error apropiado sin crashear.
# =====================================================================

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

# Módulos internos del proyecto
from config import COLORS, GRAFOS_EJEMPLO
from grafo import GrafoActivo, cargar_desde_json
from algorithms import (
    bfs_pasos, dfs_pasos, dijkstra_pasos, a_star_pasos,
    bellman_ford_pasos, kruskal_pasos, prim_pasos,
    algoritmo_disponible, obtener_error
)


class App(tk.Tk):
    """
    Ventana principal de la aplicación.

    Flujo general:
      1. Se crea la ventana y se construye la UI (_build_ui).
      2. Se carga un grafo por defecto (_load_default_graph).
      3. El usuario selecciona algoritmo, nodos y velocidad.
      4. Al presionar EJECUTAR, se llama a _run_algorithm que:
         a) Obtiene los pasos del algoritmo seleccionado.
         b) Crea una FuncAnimation que va dibujando cada paso.
    """

    def __init__(self):
        super().__init__()

        # --- Configuración de la ventana ---
        self.title("Visualizador de Algoritmos de Grafos")
        self.configure(bg=COLORS['bg_dark'])
        self.geometry("1280x820")
        self.minsize(1100, 700)

        # --- Estado interno ---
        self.ga = GrafoActivo()       # Grafo actualmente cargado
        self.current_anim = None      # Referencia a la animación activa

        # Interceptar el cierre de ventana para limpiar recursos
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Construir la interfaz y cargar el grafo por defecto
        self._build_ui()
        self._load_default_graph()

    # =================================================================
    # CIERRE LIMPIO
    # =================================================================
    def _on_close(self):
        """Detiene animaciones, cierra figuras matplotlib y termina."""
        self._stop_animation()
        plt.close('all')
        self.destroy()
        sys.exit(0)

    # =================================================================
    # CONSTRUCCIÓN DE LA INTERFAZ
    # =================================================================
    def _build_ui(self):
        """Crea el layout principal: panel izquierdo + canvas derecho."""
        main = tk.Frame(self, bg=COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=0, pady=0)

        # Panel izquierdo (controles) — ancho fijo de 310px
        self.left = tk.Frame(main, bg=COLORS['bg_panel'], width=310)
        self.left.pack(side='left', fill='y')
        self.left.pack_propagate(False)    # No dejar que los hijos cambien su ancho

        # Panel derecho (canvas de matplotlib)
        self.right = tk.Frame(main, bg=COLORS['bg_dark'])
        self.right.pack(side='right', fill='both', expand=True)

        self._build_left_panel()
        self._build_canvas()

    def _build_left_panel(self):
        """Construye todas las secciones del panel de controles."""
        p = self.left

        # ---- SECCIÓN: Selección de Grafo ----
        self._section_label(p, "GRAFO")

        # Combobox para elegir entre grafos de ejemplo
        self.graph_var = tk.StringVar(value=list(GRAFOS_EJEMPLO.keys())[0])
        combo_frame = tk.Frame(p, bg=COLORS['bg_panel'])
        combo_frame.pack(fill='x', padx=20, pady=4)

        self.graph_combo = ttk.Combobox(
            combo_frame,
            textvariable=self.graph_var,
            values=list(GRAFOS_EJEMPLO.keys()),
            state='readonly',
            font=("Helvetica", 10)
        )
        self.graph_combo.pack(fill='x')
        self.graph_combo.bind('<<ComboboxSelected>>', self._on_graph_change)

        # Botón para cargar grafo desde archivo JSON
        btn_frame = tk.Frame(p, bg=COLORS['bg_panel'])
        btn_frame.pack(fill='x', padx=20, pady=(6, 4))
        self._btn(btn_frame, "📂 Cargar JSON", self._load_json, COLORS['accent2']).pack(fill='x')

        # Etiqueta informativa (muestra nodos del grafo cargado)
        self.info_label = tk.Label(
            p, text="", font=("Helvetica", 9),
            bg=COLORS['bg_panel'], fg=COLORS['teal'], justify='left'
        )
        self.info_label.pack(padx=20, anchor='w', pady=(2, 6))

        self._sep(p)

        # ---- SECCIÓN: Selección de Algoritmo ----
        self._section_label(p, "ALGORITMO")

        # Lista de algoritmos disponibles (nombre mostrado, valor interno)
        algorithms = [
            ("BFS — Recorrido en anchura",    "bfs"),
            ("DFS — Recorrido en profundidad", "dfs"),
            ("Dijkstra — Ruta más corta",      "dijkstra"),
            ("A* — Búsqueda informada",        "astar"),
            ("Bellman-Ford — Ruta más corta",   "bellman"),
            ("Kruskal — MST",                   "kruskal"),
            ("Prim — MST",                      "prim"),
        ]

        self.algo_var = tk.StringVar(value="bfs")
        algo_frame = tk.Frame(p, bg=COLORS['bg_panel'])
        algo_frame.pack(fill='x', padx=20, pady=4)

        # Crear un radiobutton por cada algoritmo
        for text, val in algorithms:
            # Marcar con ✗ los que no se pudieron cargar
            label = text if algoritmo_disponible(val) else f"✗ {text} (error)"
            rb = tk.Radiobutton(
                algo_frame, text=label, variable=self.algo_var, value=val,
                bg=COLORS['bg_panel'], fg=COLORS['text1'],
                selectcolor=COLORS['bg_card'],
                activebackground=COLORS['bg_panel'],
                activeforeground=COLORS['accent'],
                font=("Helvetica", 10), anchor='w',
                command=self._on_algo_change
            )
            rb.pack(fill='x', pady=1)

        self._sep(p)

        # ---- SECCIÓN: Selección de Nodos (Origen / Destino) ----
        self._section_label(p, "NODOS")

        node_frame = tk.Frame(p, bg=COLORS['bg_panel'])
        node_frame.pack(fill='x', padx=20, pady=4)

        # Combo de origen
        tk.Label(
            node_frame, text="Origen:", font=("Helvetica", 10),
            bg=COLORS['bg_panel'], fg=COLORS['text1']
        ).grid(row=0, column=0, sticky='w', pady=2)

        self.origin_var = tk.StringVar()
        self.origin_combo = ttk.Combobox(
            node_frame, textvariable=self.origin_var,
            state='readonly', width=6, font=("Helvetica", 10)
        )
        self.origin_combo.grid(row=0, column=1, padx=(8, 0), pady=2)

        # Combo de destino
        tk.Label(
            node_frame, text="Destino:", font=("Helvetica", 10),
            bg=COLORS['bg_panel'], fg=COLORS['text1']
        ).grid(row=1, column=0, sticky='w', pady=2)

        self.dest_var = tk.StringVar()
        self.dest_combo = ttk.Combobox(
            node_frame, textvariable=self.dest_var,
            state='readonly', width=6, font=("Helvetica", 10)
        )
        self.dest_combo.grid(row=1, column=1, padx=(8, 0), pady=2)

        # Referencia al label de destino para poder ocultarlo/desactivarlo
        self.dest_label_widget = node_frame.grid_slaves(row=1, column=0)[0]

        self._sep(p)

        # ---- SECCIÓN: Control de Velocidad de Animación ----
        self._section_label(p, "VELOCIDAD DE ANIMACIÓN")

        speed_frame = tk.Frame(p, bg=COLORS['bg_panel'])
        speed_frame.pack(fill='x', padx=20, pady=8)

        # Etiqueta que muestra la velocidad actual en texto
        self.speed_label = tk.Label(
            speed_frame, text="Normal (1200 ms)",
            font=("Helvetica", 10, "bold"),
            bg=COLORS['bg_panel'], fg=COLORS['accent']
        )
        self.speed_label.pack(pady=(0, 8))

        # Slider (200ms = muy rápido, 3000ms = muy lento)
        self.speed_var = tk.IntVar(value=1200)
        speed_slider = tk.Scale(
            speed_frame,
            from_=200, to=3000,
            orient='horizontal',
            variable=self.speed_var,
            bg=COLORS['bg_input'],
            fg=COLORS['text1'],
            activebackground=COLORS['accent'],
            highlightthickness=0,
            troughcolor=COLORS['bg_card'],
            sliderrelief='flat',
            font=("Helvetica", 8),
            length=200,
            showvalue=0,
            command=self._update_speed_label
        )
        speed_slider.pack(fill='x', pady=(0, 4))

        # Etiquetas de referencia bajo el slider
        ref_frame = tk.Frame(speed_frame, bg=COLORS['bg_panel'])
        ref_frame.pack(fill='x')
        tk.Label(ref_frame, text="Más rápida", font=("Helvetica", 8),
                 bg=COLORS['bg_panel'], fg=COLORS['text_dim']).pack(side='left')
        tk.Label(ref_frame, text="Más lenta", font=("Helvetica", 8),
                 bg=COLORS['bg_panel'], fg=COLORS['text_dim']).pack(side='right')

        # Campo de entrada manual para valor exacto en milisegundos
        manual_frame = tk.Frame(speed_frame, bg=COLORS['bg_panel'])
        manual_frame.pack(fill='x', pady=(8, 0))

        tk.Label(
            manual_frame, text="Valor manual (ms):", font=("Helvetica", 9),
            bg=COLORS['bg_panel'], fg=COLORS['text1']
        ).pack(side='left')

        self.speed_entry = tk.Entry(
            manual_frame, width=6, font=("Helvetica", 9),
            bg=COLORS['bg_input'], fg=COLORS['text1'],
            insertbackground=COLORS['text1'],
            relief='flat', bd=2
        )
        self.speed_entry.pack(side='left', padx=(8, 4))
        self.speed_entry.insert(0, "1200")
        self.speed_entry.bind('<Return>', self._set_manual_speed)

        apply_btn = tk.Button(
            manual_frame, text="Aplicar",
            command=self._set_manual_speed,
            bg=COLORS['accent2'], fg=COLORS['text_bright'],
            font=("Helvetica", 8), relief='flat',
            cursor='hand2', padx=8, pady=2
        )
        apply_btn.pack(side='left')

        self._sep(p)

        # ---- SECCIÓN: Botones de Acción ----
        action_frame = tk.Frame(p, bg=COLORS['bg_panel'])
        action_frame.pack(fill='x', padx=20, pady=8)

        self._btn(action_frame, "▶  EJECUTAR", self._run_algorithm,
                  COLORS['accent'], large=True).pack(fill='x', pady=(0, 6))
        self._btn(action_frame, "⏹  DETENER", self._stop_animation,
                  COLORS['accent3']).pack(fill='x', pady=(0, 6))
        self._btn(action_frame, "👁  VER GRAFO", self._show_graph,
                  COLORS['bg_input']).pack(fill='x')

        # ---- Barra de estado (parte inferior del panel) ----
        self.status_var = tk.StringVar(value="Listo")
        tk.Label(
            p, textvariable=self.status_var, font=("Helvetica", 9),
            bg=COLORS['bg_panel'], fg=COLORS['text_dim'], anchor='w'
        ).pack(side='bottom', fill='x', padx=20, pady=10)

        # Ajustar estado inicial de los combos de nodos
        self._on_algo_change()

    def _build_canvas(self):
        """Crea la figura de matplotlib y la integra en el panel derecho."""
        self.fig, self.ax = plt.subplots(figsize=(9, 7))
        self.fig.patch.set_facecolor(COLORS['bg_dark'])
        self.ax.set_facecolor(COLORS['bg_card'])
        self.ax.axis('off')

        # FigureCanvasTkAgg conecta matplotlib con Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    # =================================================================
    # HELPERS DE WIDGETS
    # =================================================================
    def _section_label(self, parent, text):
        """Crea una etiqueta de sección (texto gris en mayúsculas)."""
        tk.Label(
            parent, text=text, font=("Helvetica", 9, "bold"),
            bg=COLORS['bg_panel'], fg=COLORS['text_dim']
        ).pack(padx=20, anchor='w', pady=(10, 2))

    def _sep(self, parent):
        """Crea un separador horizontal delgado."""
        tk.Frame(parent, bg=COLORS['border'], height=1).pack(
            fill='x', padx=16, pady=6
        )

    def _btn(self, parent, text, command, color, large=False):
        """
        Crea un botón estilizado con efecto hover.

        Parámetros:
            parent:  widget padre
            text:    texto del botón
            command: función a ejecutar al hacer clic
            color:   color de fondo
            large:   si es True, usa fuente más grande
        """
        font = ("Helvetica", 12, "bold") if large else ("Helvetica", 10)
        h = 2 if large else 1
        b = tk.Button(
            parent, text=text, command=command,
            bg=color, fg=COLORS['text_bright'],
            activebackground=COLORS['accent'], activeforeground='white',
            font=font, relief='flat', cursor='hand2',
            height=h, bd=0
        )
        # Efecto hover: aclarar el color al entrar, restaurar al salir
        b.bind('<Enter>', lambda e, btn=b, c=color: btn.config(bg=self._lighten(c)))
        b.bind('<Leave>', lambda e, btn=b, c=color: btn.config(bg=c))
        return b

    def _lighten(self, hex_color, factor=0.15):
        """Aclara un color hex en un factor dado (0.0 a 1.0)."""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f'#{r:02x}{g:02x}{b:02x}'

    def _update_speed_label(self, value=None):
        """Actualiza el texto descriptivo de velocidad cuando se mueve el slider."""
        speed = self.speed_var.get()
        self.speed_entry.delete(0, tk.END)
        self.speed_entry.insert(0, str(speed))

        # Categorizar la velocidad en rangos
        if speed < 400:
            desc = "Ultra Rápida"
        elif speed < 700:
            desc = "Muy Rápida"
        elif speed < 1000:
            desc = "Rápida"
        elif speed < 1400:
            desc = "Normal"
        elif speed < 1800:
            desc = "Lenta"
        else:
            desc = "Muy Lenta"

        self.speed_label.config(text=f"{desc} ({speed} ms)")

    def _set_manual_speed(self, event=None):
        """Valida y aplica la velocidad ingresada manualmente."""
        try:
            value = int(self.speed_entry.get())
            if 200 <= value <= 3000:
                self.speed_var.set(value)
                self._update_speed_label()
            else:
                messagebox.showwarning(
                    "Valor fuera de rango",
                    "Por favor ingresa un valor entre 200 y 3000 ms"
                )
                self.speed_entry.delete(0, tk.END)
                self.speed_entry.insert(0, str(self.speed_var.get()))
        except ValueError:
            messagebox.showerror(
                "Valor inválido",
                "Por favor ingresa un número entero válido"
            )
            self.speed_entry.delete(0, tk.END)
            self.speed_entry.insert(0, str(self.speed_var.get()))

    # =================================================================
    # GESTIÓN DE GRAFOS
    # =================================================================
    def _load_default_graph(self):
        """Carga el primer grafo de ejemplo al iniciar la app."""
        nombre = list(GRAFOS_EJEMPLO.keys())[0]
        d = GRAFOS_EJEMPLO[nombre]
        self.ga.cargar(d["matriz"], d["nombres"], nombre)
        self._update_node_combos()
        self._show_graph()

    def _on_graph_change(self, event=None):
        """Callback cuando el usuario selecciona un grafo del combobox."""
        nombre = self.graph_var.get()
        if nombre in GRAFOS_EJEMPLO:
            d = GRAFOS_EJEMPLO[nombre]
            self.ga.cargar(d["matriz"], d["nombres"], nombre)
            self._update_node_combos()
            self._show_graph()
            self.status_var.set(f"Cargado: {nombre}")

    def _load_json(self):
        """Abre un diálogo para cargar un grafo desde archivo JSON."""
        path = filedialog.askopenfilename(
            title="Seleccionar archivo JSON",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")]
        )
        if not path:
            return

        m, n, err = cargar_desde_json(path)
        if err:
            messagebox.showerror("Error", err)
            return

        nombre = f"Custom ({os.path.basename(path)})"
        self.ga.cargar(m, n, nombre)

        # Agregar al combobox si es nuevo
        if nombre not in GRAFOS_EJEMPLO:
            GRAFOS_EJEMPLO[nombre] = {"matriz": m, "nombres": n}
            self.graph_combo['values'] = list(GRAFOS_EJEMPLO.keys())

        self.graph_var.set(nombre)
        self._update_node_combos()
        self._show_graph()
        self.status_var.set(f"✓ Cargado: {nombre} — {self.ga.N} nodos")

    def _update_node_combos(self):
        """Actualiza las opciones de los combobox de Origen y Destino."""
        if not self.ga.loaded:
            return
        vals = self.ga.nombres
        self.origin_combo['values'] = vals
        self.dest_combo['values'] = vals
        self.origin_var.set(vals[0])           # Origen = primer nodo
        self.dest_var.set(vals[-1])            # Destino = último nodo
        self.info_label.config(text=f"{self.ga.N} nodos: {', '.join(vals)}")

    def _on_algo_change(self):
        """
        Habilita/deshabilita los combos de nodos según el algoritmo.
        - BFS/DFS: solo necesitan Origen.
        - Dijkstra/A*/Bellman-Ford: necesitan Origen y Destino.
        - Kruskal/Prim: no necesitan ninguno (trabajan con todo el grafo).
        """
        algo = self.algo_var.get()
        needs_dest = algo in ('dijkstra', 'astar', 'bellman')
        needs_origin = algo not in ('kruskal', 'prim')

        self.origin_combo.config(state='readonly' if needs_origin else 'disabled')
        self.dest_combo.config(state='readonly' if needs_dest else 'disabled')

    # =================================================================
    # DIBUJO BASE DEL GRAFO
    # =================================================================
    def _draw_base(self, title="", subtitle=""):
        """
        Dibuja el grafo completo sin resaltados (estado neutral).
        Se usa para la vista "Ver Grafo" y como base antes de animar.
        """
        self.ax.clear()
        self.ax.set_facecolor(COLORS['bg_card'])
        self.ax.axis('off')

        # Aristas base (gris, semitransparentes)
        nx.draw_networkx_edges(
            self.ga.G, self.ga.pos,
            edge_color=COLORS['edge_default'], width=2, alpha=0.5, ax=self.ax
        )
        # Nodos base (cian con borde gris)
        nx.draw_networkx_nodes(
            self.ga.G, self.ga.pos,
            node_color=COLORS['node_default'], node_size=900,
            edgecolors=COLORS['text_dim'], linewidths=2, ax=self.ax
        )
        # Etiquetas de nodos
        nx.draw_networkx_labels(
            self.ga.G, self.ga.pos,
            font_size=13, font_weight='bold', font_color='white', ax=self.ax
        )
        # Etiquetas de peso en las aristas
        edge_labels = nx.get_edge_attributes(self.ga.G, 'weight')
        nx.draw_networkx_edge_labels(
            self.ga.G, self.ga.pos,
            edge_labels=edge_labels, font_size=9, font_color=COLORS['text1'],
            bbox=dict(
                boxstyle='round,pad=0.3',
                facecolor=COLORS['bg_card'],
                edgecolor=COLORS['border'], alpha=0.9
            ),
            ax=self.ax
        )

        # Títulos
        self.fig.texts.clear()
        if title:
            self.fig.suptitle(
                title, fontsize=17, fontweight='bold',
                color=COLORS['text_bright'], y=0.97
            )
        if subtitle:
            self.ax.set_title(
                subtitle, fontsize=11, color=COLORS['text_dim'],
                pad=14, style='italic'
            )

    def _show_graph(self):
        """Muestra el grafo en su estado neutral (sin animación)."""
        self._stop_animation()
        if not self.ga.loaded:
            return
        self._draw_base(self.ga.nombre_grafo, f"Grafo ponderado — {self.ga.N} nodos")
        self.canvas.draw()

    # =================================================================
    # MOTOR DE ANIMACIÓN
    # =================================================================
    def _stop_animation(self):
        """Detiene cualquier animación en curso y resetea la figura."""
        if self.current_anim is not None:
            try:
                self.current_anim.event_source.stop()
            except Exception:
                pass
            self.current_anim = None

        # Recrear el axes limpio para evitar artefactos
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(COLORS['bg_card'])
        self.ax.axis('off')
        self.fig.patch.set_facecolor(COLORS['bg_dark'])
        self.canvas.draw_idle()

    def _run_algorithm(self):
        """
        Punto de entrada al ejecutar un algoritmo.
        Valida que haya un grafo cargado, que el algoritmo esté disponible,
        y despacha a la función de animación correspondiente.
        """
        if not self.ga.loaded:
            messagebox.showwarning("Aviso", "Carga un grafo primero")
            return

        self._stop_animation()
        self.update_idletasks()   # Procesar limpieza pendiente de Tkinter

        algo = self.algo_var.get()

        # Verificar que el algoritmo se cargó correctamente
        if not algoritmo_disponible(algo):
            error_msg = obtener_error(algo)
            messagebox.showerror(
                "Algoritmo no disponible",
                f"El algoritmo '{algo}' no se pudo cargar.\n\n"
                f"Error:\n{error_msg}"
            )
            return

        # Obtener índices de los nodos seleccionados
        origen_name = self.origin_var.get()
        dest_name = self.dest_var.get()
        origen = self.ga.nombres.index(origen_name) if origen_name in self.ga.nombres else 0
        destino = self.ga.nombres.index(dest_name) if dest_name in self.ga.nombres else self.ga.N - 1

        # Despachar al animador correspondiente (con manejo de errores)
        try:
            if algo == 'bfs':
                self._animate_bfs(origen)
            elif algo == 'dfs':
                self._animate_dfs(origen)
            elif algo == 'dijkstra':
                self._animate_dijkstra(origen, destino)
            elif algo == 'astar':
                self._animate_astar(origen, destino)
            elif algo == 'bellman':
                self._animate_bellman(origen, destino)
            elif algo == 'kruskal':
                self._animate_kruskal()
            elif algo == 'prim':
                self._animate_prim()
        except Exception as e:
            messagebox.showerror("Error en ejecución", str(e))

    # =================================================================
    # RENDERIZADORES DE FRAME
    # =================================================================
    def _render_frame(self, step_data, algo_name, subtitle,
                      highlight_edges=None, path_edges=None, eval_edge=None,
                      node_color_fn=None, label_fn=None):
        """
        Renderiza un frame genérico de animación (usado por todos los
        algoritmos excepto Bellman-Ford que tiene su versión especial).

        Parámetros:
            step_data:       datos del paso actual (no se usa directamente aquí)
            algo_name:       título del algoritmo para el suptitle
            subtitle:        subtítulo con info del paso actual
            highlight_edges: lista de aristas (nombre_u, nombre_v) a resaltar
            path_edges:      aristas del camino final (verde, más gruesas)
            eval_edge:       tupla (color, [aristas]) para arista siendo evaluada
            node_color_fn:   función(índice) → color hex para cada nodo
            label_fn:        función(índice, nombre) → texto del label del nodo
        """
        self.ax.clear()
        self.ax.set_facecolor(COLORS['bg_card'])
        self.ax.axis('off')

        # Capa 1: aristas base (todas, en gris transparente)
        nx.draw_networkx_edges(
            self.ga.G, self.ga.pos,
            edge_color=COLORS['edge_default'], width=1.5, alpha=0.35, ax=self.ax
        )

        # Capa 2: aristas resaltadas (árbol de exploración)
        if highlight_edges:
            nx.draw_networkx_edges(
                self.ga.G, self.ga.pos, edgelist=highlight_edges,
                edge_color=COLORS['edge_highlight'], width=3.5, alpha=0.85, ax=self.ax
            )

        # Capa 3: aristas del camino final (verde, gruesas)
        if path_edges:
            nx.draw_networkx_edges(
                self.ga.G, self.ga.pos, edgelist=path_edges,
                edge_color=COLORS['edge_path'], width=5, alpha=0.95, ax=self.ax
            )

        # Capa 4: arista siendo evaluada (discontinua)
        if eval_edge:
            color_e, edges_e = eval_edge
            nx.draw_networkx_edges(
                self.ga.G, self.ga.pos, edgelist=edges_e,
                edge_color=color_e, width=4, alpha=0.9, style='dashed', ax=self.ax
            )

        # Nodos con colores dinámicos según el estado del algoritmo
        if node_color_fn:
            colors = [node_color_fn(self.ga.nombres.index(n)) for n in self.ga.G.nodes()]
        else:
            colors = [COLORS['node_default']] * len(self.ga.G.nodes())
        nx.draw_networkx_nodes(
            self.ga.G, self.ga.pos, node_color=colors, node_size=900,
            edgecolors='#ffffff33', linewidths=2, ax=self.ax
        )

        # Labels de nodos (pueden incluir distancia, etc.)
        if label_fn:
            labels = {n: label_fn(self.ga.nombres.index(n), n) for n in self.ga.G.nodes()}
        else:
            labels = {n: n for n in self.ga.G.nodes()}
        nx.draw_networkx_labels(
            self.ga.G, self.ga.pos, labels=labels, font_size=11,
            font_weight='bold', font_color='white', ax=self.ax
        )

        # Pesos en las aristas
        edge_labels = nx.get_edge_attributes(self.ga.G, 'weight')
        nx.draw_networkx_edge_labels(
            self.ga.G, self.ga.pos, edge_labels=edge_labels,
            font_size=9, font_color=COLORS['text1'],
            bbox=dict(
                boxstyle='round,pad=0.3',
                facecolor=COLORS['bg_card'],
                edgecolor=COLORS['border'], alpha=0.9
            ),
            ax=self.ax
        )

        # Títulos
        self.fig.texts.clear()
        self.fig.suptitle(
            algo_name, fontsize=17, fontweight='bold',
            color=COLORS['text_bright'], y=0.97
        )
        self.ax.set_title(
            subtitle, fontsize=11, color=COLORS['text_dim'],
            pad=14, style='italic'
        )

    def _render_bellman_frame(self, step_data, algo_name, subtitle,
                              highlight_edges=None, path_edges=None, eval_edge=None,
                              node_color_fn=None, label_fn=None, distancias=None):
        """
        Renderizador especial para Bellman-Ford.
        Divide la figura en dos secciones:
          - Arriba: visualización del grafo (igual que _render_frame)
          - Abajo: tabla de distancias desde el origen a cada nodo
        """
        self.fig.clear()

        # Crear grid: 3/4 para el grafo, 1/4 para la tabla
        gs = self.fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.15)
        ax_graph = self.fig.add_subplot(gs[0])
        ax_table = self.fig.add_subplot(gs[1])

        ax_graph.set_facecolor(COLORS['bg_card'])
        ax_graph.axis('off')
        ax_table.set_facecolor(COLORS['bg_dark'])
        ax_table.axis('off')

        # ---- Dibujar grafo (misma lógica que _render_frame) ----
        nx.draw_networkx_edges(
            self.ga.G, self.ga.pos,
            edge_color=COLORS['edge_default'], width=1.5, alpha=0.35, ax=ax_graph
        )
        if highlight_edges:
            nx.draw_networkx_edges(
                self.ga.G, self.ga.pos, edgelist=highlight_edges,
                edge_color=COLORS['edge_highlight'], width=3.5, alpha=0.85, ax=ax_graph
            )
        if path_edges:
            nx.draw_networkx_edges(
                self.ga.G, self.ga.pos, edgelist=path_edges,
                edge_color=COLORS['edge_path'], width=5, alpha=0.95, ax=ax_graph
            )
        if eval_edge:
            color_e, edges_e = eval_edge
            nx.draw_networkx_edges(
                self.ga.G, self.ga.pos, edgelist=edges_e,
                edge_color=color_e, width=4, alpha=0.9, style='dashed', ax=ax_graph
            )

        if node_color_fn:
            colors = [node_color_fn(self.ga.nombres.index(n)) for n in self.ga.G.nodes()]
        else:
            colors = [COLORS['node_default']] * len(self.ga.G.nodes())
        nx.draw_networkx_nodes(
            self.ga.G, self.ga.pos, node_color=colors, node_size=900,
            edgecolors='#ffffff33', linewidths=2, ax=ax_graph
        )

        if label_fn:
            labels = {n: label_fn(self.ga.nombres.index(n), n) for n in self.ga.G.nodes()}
        else:
            labels = {n: n for n in self.ga.G.nodes()}
        nx.draw_networkx_labels(
            self.ga.G, self.ga.pos, labels=labels, font_size=11,
            font_weight='bold', font_color='white', ax=ax_graph
        )

        edge_labels = nx.get_edge_attributes(self.ga.G, 'weight')
        nx.draw_networkx_edge_labels(
            self.ga.G, self.ga.pos, edge_labels=edge_labels,
            font_size=9, font_color=COLORS['text1'],
            bbox=dict(
                boxstyle='round,pad=0.3',
                facecolor=COLORS['bg_card'],
                edgecolor=COLORS['border'], alpha=0.9
            ),
            ax=ax_graph
        )

        # Títulos
        self.fig.suptitle(
            algo_name, fontsize=17, fontweight='bold',
            color=COLORS['text_bright'], y=0.96
        )
        ax_graph.set_title(
            subtitle, fontsize=11, color=COLORS['text_dim'],
            pad=10, style='italic'
        )

        # ---- Tabla de distancias (parte inferior) ----
        if distancias is not None:
            cell_text = []
            row_colors = []

            # Fila 1: nombres de los nodos
            cell_text.append(self.ga.nombres)
            row_colors.append(COLORS['accent'])

            # Fila 2: distancias (∞ si es infinito)
            dist_row = []
            for d in distancias:
                dist_row.append('∞' if d == float('inf') else str(int(d)))
            cell_text.append(dist_row)
            row_colors.append(COLORS['bg_card'])

            # Resaltar la columna del nodo destino de la arista evaluada
            col_colors = [COLORS['bg_input']] * len(self.ga.nombres)
            if step_data.get('tipo') == 'relajacion' and 'arista_evaluada' in step_data:
                _, v = step_data['arista_evaluada']
                col_colors[v] = COLORS['node_current']

            # Crear y estilizar la tabla
            table = ax_table.table(
                cellText=cell_text, cellLoc='center',
                loc='center', bbox=[0.1, 0.3, 0.8, 0.6]
            )
            table.auto_set_font_size(False)
            table.set_fontsize(10)

            for i in range(len(cell_text)):
                for j in range(len(self.ga.nombres)):
                    cell = table[(i, j)]
                    cell.set_facecolor(row_colors[i] if i == 0 else col_colors[j])
                    cell.set_edgecolor(COLORS['border'])
                    cell.set_text_props(
                        weight='bold' if i == 0 else 'normal',
                        color=COLORS['text_bright']
                    )

            ax_table.text(
                0.5, 0.05, 'Distancias desde el origen',
                ha='center', fontsize=10, color=COLORS['text_dim'],
                transform=ax_table.transAxes
            )

        # Mantener referencia al axes del grafo para compatibilidad
        self.ax = ax_graph

    # =================================================================
    # ANIMACIONES POR ALGORITMO
    # =================================================================

    # ------ BFS ------
    def _animate_bfs(self, inicio):
        """Anima BFS paso a paso desde el nodo de inicio."""
        pasos = bfs_pasos(self.ga, inicio)
        self.status_var.set(f"BFS desde {self.ga.nombres[inicio]}...")

        def update(frame):
            p = pasos[frame]
            # Construir aristas del árbol BFS a partir del dict de padres
            he = []
            for nodo in p['visitados']:
                if p['padre'].get(nodo) is not None:
                    he.append((self.ga.nombres[p['padre'][nodo]], self.ga.nombres[nodo]))

            def ncf(idx):
                if idx == p['actual']:     return COLORS['node_current']
                if idx in p['visitados']:  return COLORS['node_visit']
                return COLORS['node_default']

            self._render_frame(
                p, f"BFS — {self.ga.nombre_grafo}",
                f"Paso {frame+1}/{len(pasos)} | Visitando: {self.ga.nombres[p['actual']]}",
                highlight_edges=he, node_color_fn=ncf
            )
            self.canvas.draw_idle()

            if frame == len(pasos) - 1:
                self.status_var.set(f"BFS completado — {len(pasos)} nodos visitados")

        self.current_anim = FuncAnimation(
            self.fig, update, frames=len(pasos),
            interval=self.speed_var.get(), repeat=False
        )
        self.canvas.draw()

    # ------ DFS ------
    def _animate_dfs(self, inicio):
        """Anima DFS paso a paso desde el nodo de inicio."""
        pasos = dfs_pasos(self.ga, inicio)
        self.status_var.set(f"DFS desde {self.ga.nombres[inicio]}...")

        def update(frame):
            p = pasos[frame]
            he = []
            for nodo in p['visitados']:
                if p['padre'].get(nodo) is not None:
                    he.append((self.ga.nombres[p['padre'][nodo]], self.ga.nombres[nodo]))

            def ncf(idx):
                if idx == p['actual']:     return COLORS['orange']
                if idx in p['visitados']:  return COLORS['accent3']
                return COLORS['node_default']

            self._render_frame(
                p, f"DFS — {self.ga.nombre_grafo}",
                f"Paso {frame+1}/{len(pasos)} | Visitando: {self.ga.nombres[p['actual']]}",
                highlight_edges=he, node_color_fn=ncf
            )
            self.canvas.draw_idle()

            if frame == len(pasos) - 1:
                self.status_var.set("DFS completado")

        self.current_anim = FuncAnimation(
            self.fig, update, frames=len(pasos),
            interval=self.speed_var.get(), repeat=False
        )
        self.canvas.draw()

    # ------ DIJKSTRA ------
    def _animate_dijkstra(self, inicio, objetivo):
        """Anima Dijkstra con frame final mostrando el camino más corto."""
        pasos, camino, dist_final = dijkstra_pasos(self.ga, inicio, objetivo)
        total = len(pasos)

        # Agregar un frame extra para mostrar el resultado final
        if camino and len(camino) > 1:
            pasos.append({
                'final': True, 'camino': camino,
                'dist': dist_final, 'padre': pasos[-1]['padre']
            })

        self.status_var.set(f"Dijkstra: {self.ga.nombres[inicio]} → {self.ga.nombres[objetivo]}...")

        def update(frame):
            p = pasos[frame]
            is_final = p.get('final', False)

            if is_final:
                # Frame final: mostrar camino en verde
                cf = p['camino']
                pe = [(self.ga.nombres[cf[i]], self.ga.nombres[cf[i+1]]) for i in range(len(cf)-1)]

                def ncf(idx):
                    return COLORS['green'] if idx in cf else COLORS['node_default']

                def lf(idx, n):
                    d = p['dist'][idx]
                    return f"{n}\n({int(d)})" if d != float('inf') else f"{n}\n(∞)"

                cost = int(dist_final[objetivo]) if dist_final[objetivo] != float('inf') else '∞'
                camino_str = " → ".join([self.ga.nombres[n] for n in cf])

                self._render_frame(
                    p, f"Dijkstra — {self.ga.nombre_grafo}",
                    f"✓ {camino_str} | Costo: {cost}",
                    path_edges=pe, node_color_fn=ncf, label_fn=lf
                )
                self.status_var.set(f"✓ Ruta: {camino_str} — Costo: {cost}")
            else:
                # Frames de exploración
                he = []
                for nodo in p['visitados']:
                    if p['padre'].get(nodo) is not None:
                        he.append((self.ga.nombres[p['padre'][nodo]], self.ga.nombres[nodo]))

                def ncf(idx):
                    if idx == objetivo:    return COLORS['orange']
                    if idx == p['actual']: return COLORS['node_current']
                    if idx in p['visitados']: return COLORS['node_visit']
                    return COLORS['node_default']

                def lf(idx, n):
                    d = p['dist'][idx]
                    return f"{n}\n({int(d)})" if d != float('inf') else f"{n}\n(∞)"

                self._render_frame(
                    p, f"Dijkstra — {self.ga.nombre_grafo}",
                    f"Paso {frame+1}/{total} | Procesando: {self.ga.nombres[p['actual']]}",
                    highlight_edges=he, node_color_fn=ncf, label_fn=lf
                )
            self.canvas.draw_idle()

        self.current_anim = FuncAnimation(
            self.fig, update, frames=len(pasos),
            interval=self.speed_var.get(), repeat=False
        )
        self.canvas.draw()

    # ------ A* ------
    def _animate_astar(self, inicio, objetivo):
        """Anima A* con frame final mostrando el camino encontrado."""
        pasos, camino, g_final = a_star_pasos(self.ga, inicio, objetivo)
        total = len(pasos)

        if camino and len(camino) > 1:
            pasos.append({
                'final': True, 'camino': camino,
                'g': g_final, 'padre': pasos[-1]['padre']
            })

        self.status_var.set(f"A*: {self.ga.nombres[inicio]} → {self.ga.nombres[objetivo]}...")

        def update(frame):
            p = pasos[frame]
            is_final = p.get('final', False)

            if is_final:
                cf = p['camino']
                pe = [(self.ga.nombres[cf[i]], self.ga.nombres[cf[i+1]]) for i in range(len(cf)-1)]

                def ncf(idx):
                    return COLORS['green'] if idx in cf else COLORS['node_default']

                cost = int(g_final.get(objetivo, 0))
                camino_str = " → ".join([self.ga.nombres[n] for n in cf])

                self._render_frame(
                    p, f"A* — {self.ga.nombre_grafo}",
                    f"✓ {camino_str} | Costo: {cost}",
                    path_edges=pe, node_color_fn=ncf
                )
                self.status_var.set(f"✓ Ruta: {camino_str} — Costo: {cost}")
            else:
                he = []
                for nodo in p['visitados']:
                    if p['padre'].get(nodo) is not None:
                        he.append((self.ga.nombres[p['padre'][nodo]], self.ga.nombres[nodo]))

                def ncf(idx):
                    if idx == objetivo:    return COLORS['orange']
                    if idx == p['actual']: return COLORS['teal']
                    if idx in p['visitados']: return '#0077b6'
                    return COLORS['node_default']

                self._render_frame(
                    p, f"A* — {self.ga.nombre_grafo}",
                    f"Paso {frame+1}/{total} | Explorando: {self.ga.nombres[p['actual']]}",
                    highlight_edges=he, node_color_fn=ncf
                )
            self.canvas.draw_idle()

        self.current_anim = FuncAnimation(
            self.fig, update, frames=len(pasos),
            interval=self.speed_var.get(), repeat=False
        )
        self.canvas.draw()

    # ------ BELLMAN-FORD ------
    def _animate_bellman(self, origen, objetivo):
        """Anima Bellman-Ford con tabla de distancias debajo del grafo."""
        pasos, camino, dist_final = bellman_ford_pasos(self.ga, origen, objetivo)

        if camino and len(camino) > 1:
            pasos.append({'final': True, 'camino': camino, 'dist': dist_final})

        self.status_var.set(f"Bellman-Ford: {self.ga.nombres[origen]} → {self.ga.nombres[objetivo]}...")

        def update(frame):
            p = pasos[frame]
            is_final = p.get('final', False)

            if is_final:
                cf = p['camino']
                pe = [(self.ga.nombres[cf[i]], self.ga.nombres[cf[i+1]]) for i in range(len(cf)-1)]

                def ncf(idx):
                    return COLORS['green'] if idx in cf else COLORS['node_default']

                def lf(idx, n):
                    d = p['dist'][idx]
                    return f"{n}\n({int(d)})" if d != float('inf') else f"{n}\n(∞)"

                cost = int(dist_final[objetivo]) if dist_final[objetivo] != float('inf') else '∞'
                camino_str = " → ".join([self.ga.nombres[n] for n in cf])

                self._render_bellman_frame(
                    p, f"Bellman-Ford — {self.ga.nombre_grafo}",
                    f"✓ {camino_str} | Costo: {cost}",
                    path_edges=pe, node_color_fn=ncf, label_fn=lf,
                    distancias=p['dist']
                )
                self.status_var.set(f"✓ Ruta: {camino_str} — Costo: {cost}")
            else:
                # Aristas del árbol de padres
                he = []
                for nodo in p['padre']:
                    if p['padre'][nodo] is not None:
                        he.append((self.ga.nombres[p['padre'][nodo]], self.ga.nombres[nodo]))

                # Arista siendo evaluada (discontinua naranja)
                eval_edge = None
                if p['tipo'] == 'relajacion' and 'arista_evaluada' in p:
                    u, v = p['arista_evaluada']
                    eval_edge = (COLORS['orange'], [(self.ga.nombres[u], self.ga.nombres[v])])

                def lf(idx, n):
                    d = p['dist'][idx]
                    return f"{n}\n({int(d)})" if d != float('inf') else f"{n}\n(∞)"

                def ncf(idx):
                    if p['tipo'] == 'relajacion' and 'arista_evaluada' in p:
                        u, v = p['arista_evaluada']
                        if idx == v: return COLORS['node_current']
                        if idx == u: return COLORS['accent']
                    return COLORS['node_default']

                # Subtítulo detallado
                if p['tipo'] == 'relajacion':
                    u, v = p['arista_evaluada']
                    ant_str = f"{int(p['dist_anterior'])}" if p['dist_anterior'] != float('inf') else "∞"
                    nueva_str = f"{int(p['dist_nueva'])}"
                    sub = (
                        f"Iteración {p['iter']} | "
                        f"Relajando {self.ga.nombres[u]}→{self.ga.nombres[v]} (peso {p['peso']}) | "
                        f"{self.ga.nombres[v]}: {ant_str} → {nueva_str} ✓"
                    )
                else:
                    sub = f"Iteración {p['iter']} | Sin cambios (convergencia alcanzada)"

                self._render_bellman_frame(
                    p, f"Bellman-Ford — {self.ga.nombre_grafo}",
                    sub, highlight_edges=he, label_fn=lf,
                    eval_edge=eval_edge, node_color_fn=ncf, distancias=p['dist']
                )
            self.canvas.draw_idle()

        self.current_anim = FuncAnimation(
            self.fig, update, frames=len(pasos),
            interval=self.speed_var.get(), repeat=False
        )
        self.canvas.draw()

    # ------ KRUSKAL ------
    def _animate_kruskal(self):
        """Anima Kruskal mostrando cada arista evaluada (aceptada/rechazada)."""
        pasos = kruskal_pasos(self.ga)
        self.status_var.set("Kruskal MST...")

        def update(frame):
            p = pasos[frame]
            # Aristas ya aceptadas en el MST
            mst_e = [(self.ga.nombres[u], self.ga.nombres[v]) for u, v in p['mst']]
            # Arista que se está evaluando en este paso
            u, v = p['edge']
            eval_e = [(self.ga.nombres[u], self.ga.nombres[v])]
            # Verde si aceptada, rojo si rechazada (formaría ciclo)
            color_e = COLORS['green'] if p['ok'] else COLORS['accent']
            estado = "✓ Aceptada" if p['ok'] else "✗ Rechazada (ciclo)"

            self._render_frame(
                p, f"Kruskal — {self.ga.nombre_grafo}",
                f"Paso {frame+1}/{len(pasos)} | {self.ga.nombres[u]}-{self.ga.nombres[v]} "
                f"(peso {p['w']}) | {estado}",
                highlight_edges=mst_e, eval_edge=(color_e, eval_e)
            )
            self.canvas.draw_idle()

            if frame == len(pasos) - 1:
                peso_total = sum(self.ga.matriz[u][v] for u, v in p['mst'])
                self.status_var.set(f"✓ MST Kruskal — Peso total: {int(peso_total)}")

        self.current_anim = FuncAnimation(
            self.fig, update, frames=len(pasos),
            interval=self.speed_var.get(), repeat=False
        )
        self.canvas.draw()

    # ------ PRIM ------
    def _animate_prim(self):
        """Anima Prim mostrando cómo crece el MST nodo a nodo."""
        pasos = prim_pasos(self.ga)
        self.status_var.set("Prim MST...")

        def update(frame):
            p = pasos[frame]
            mst_e = [(self.ga.nombres[u], self.ga.nombres[v]) for u, v in p['mst']]

            def ncf(idx):
                if idx == p['actual']:        return COLORS['green']
                if idx in p['visitados']:     return '#16a085'
                return COLORS['node_default']

            self._render_frame(
                p, f"Prim — {self.ga.nombre_grafo}",
                f"Paso {frame+1}/{len(pasos)} | Agregando: {self.ga.nombres[p['actual']]} | "
                f"Aristas MST: {len(p['mst'])}",
                highlight_edges=mst_e, node_color_fn=ncf
            )
            self.canvas.draw_idle()

            if frame == len(pasos) - 1:
                peso_total = sum(self.ga.matriz[u][v] for u, v in p['mst'])
                self.status_var.set(f"✓ MST Prim — Peso total: {int(peso_total)}")

        self.current_anim = FuncAnimation(
            self.fig, update, frames=len(pasos),
            interval=self.speed_var.get(), repeat=False
        )
        self.canvas.draw()
