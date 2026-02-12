# =====================================================================
# grafo.py — Modelo de datos del grafo y funciones auxiliares
# =====================================================================
# Contiene:
#   - GrafoActivo: clase que encapsula el grafo actualmente cargado
#     (matriz de adyacencia, nombres, objeto NetworkX, posiciones).
#   - Funciones auxiliares para convertir entre representaciones
#     (matriz → aristas, matriz → lista de adyacencia, etc.).
#   - Carga de grafos desde archivos JSON.
# =====================================================================

import math
import json
import numpy as np
import networkx as nx


class GrafoActivo:
    """
    Encapsula el grafo con el que se está trabajando.

    Atributos:
        matriz (np.ndarray | None): Matriz de adyacencia NxN.
        nombres (list[str] | None):  Etiquetas de cada nodo.
        N (int):                     Número de nodos.
        G (nx.Graph | None):         Representación NetworkX del grafo.
        pos (dict | None):           Posiciones {nodo: (x, y)} para dibujo.
        nombre_grafo (str):          Nombre descriptivo del grafo cargado.
    """

    def __init__(self):
        self.matriz = None
        self.nombres = None
        self.N = 0
        self.G = None
        self.pos = None
        self.nombre_grafo = ""

    def cargar(self, matriz, nombres, nombre_grafo="Personalizado"):
        """
        Carga un grafo nuevo a partir de su matriz de adyacencia.

        Parámetros:
            matriz:       Lista de listas (o ndarray) con los pesos.
                          0 indica que no hay arista entre dos nodos.
            nombres:      Lista de strings con las etiquetas de los nodos.
            nombre_grafo: Texto descriptivo que se muestra en la interfaz.
        """
        self.matriz = np.array(matriz)
        self.nombres = nombres
        self.N = len(matriz)
        self.nombre_grafo = nombre_grafo

        # Construir el grafo NetworkX a partir de la parte superior
        # de la matriz (es simétrica, así evitamos aristas duplicadas).
        self.G = nx.Graph()
        for i in range(self.N):
            for j in range(i + 1, self.N):
                if self.matriz[i][j] > 0:
                    self.G.add_edge(
                        self.nombres[i],
                        self.nombres[j],
                        weight=int(self.matriz[i][j])
                    )

        # Calcular posiciones con layout spring (semilla fija = reproducible)
        self.pos = nx.spring_layout(self.G, seed=42, k=2, iterations=50)

    @property
    def loaded(self):
        """Retorna True si ya se cargó algún grafo."""
        return self.matriz is not None


# =====================================================================
# FUNCIONES DE CONVERSIÓN DE REPRESENTACIONES
# =====================================================================

def matriz_a_aristas(m):
    """
    Convierte una matriz de adyacencia en lista de aristas (u, v, peso).
    Incluye ambas direcciones (u→v y v→u) porque Bellman-Ford
    necesita considerar todas las aristas dirigidas.
    """
    return [
        (i, j, m[i][j])
        for i in range(len(m))
        for j in range(len(m))
        if m[i][j] != 0
    ]


def matriz_a_lista_ady(m):
    """
    Convierte una matriz de adyacencia en lista de adyacencia.
    Retorna: lista donde lista[i] = [(vecino_j, peso), ...]
    Usada por el algoritmo de Prim.
    """
    lista = [[] for _ in range(len(m))]
    for i in range(len(m)):
        for j in range(len(m)):
            if m[i][j] != 0:
                lista[i].append((j, m[i][j]))
    return lista


def generar_coords(n):
    """
    Genera coordenadas en cuadrícula para n nodos.
    Se usan como posiciones ficticias para la heurística de A*
    (distancia euclidiana entre posiciones en la cuadrícula).
    """
    coords = {}
    columnas = math.ceil(math.sqrt(n))
    for i in range(n):
        coords[i] = (i % columnas, i // columnas)
    return coords


# =====================================================================
# CARGA DESDE ARCHIVO JSON
# =====================================================================

def cargar_desde_json(ruta):
    """
    Lee un archivo JSON y extrae la información del grafo.

    Formatos soportados:
      1) {"matriz": [[...], ...], "nombres": ["A", "B", ...]}
         → Matriz de adyacencia directa. Si 'nombres' no existe,
           se generan automáticamente (A, B, C...).

      2) {"aristas": [{"origen": "A", "destino": "B", "peso": 5}, ...]}
         → Lista de aristas. Se construye la matriz internamente.

    Retorna:
        (matriz, nombres, None)       si todo salió bien.
        (None, None, mensaje_error)   si hubo algún problema.
    """
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # ----- Formato 1: Matriz de adyacencia -----
        if "matriz" in data:
            matriz = data["matriz"]
            n = len(matriz)

            # Verificar que sea cuadrada
            for fila in matriz:
                if len(fila) != n:
                    return None, None, "La matriz no es cuadrada"

            # Forzar simetría (tomar el mayor de los dos valores)
            for i in range(n):
                for j in range(n):
                    if matriz[i][j] != matriz[j][i]:
                        val = max(matriz[i][j], matriz[j][i])
                        matriz[i][j] = val
                        matriz[j][i] = val

            # Generar nombres por defecto si no se proporcionan
            nombres = data.get("nombres", None)
            if nombres is None or len(nombres) != n:
                nombres = [
                    chr(65 + i) if i < 26 else f"N{i}"
                    for i in range(n)
                ]
            return matriz, nombres, None

        # ----- Formato 2: Lista de aristas -----
        elif "aristas" in data:
            # Recopilar todos los nodos mencionados
            nodos = set()
            for a in data["aristas"]:
                nodos.add(str(a["origen"]))
                nodos.add(str(a["destino"]))

            nombres = sorted(list(nodos))
            idx = {nombre: i for i, nombre in enumerate(nombres)}
            n = len(nombres)

            # Construir la matriz de adyacencia
            matriz = [[0] * n for _ in range(n)]
            for a in data["aristas"]:
                u, v = idx[str(a["origen"])], idx[str(a["destino"])]
                peso = a.get("peso", 1)
                matriz[u][v] = peso
                matriz[v][u] = peso  # Grafo no dirigido

            return matriz, nombres, None

        else:
            return None, None, "JSON debe contener 'matriz' o 'aristas'"

    except FileNotFoundError:
        return None, None, "Archivo no encontrado"
    except json.JSONDecodeError:
        return None, None, "JSON inválido"
    except Exception as e:
        return None, None, str(e)
