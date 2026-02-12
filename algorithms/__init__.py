# =====================================================================
# algorithms/__init__.py — Carga segura de todos los algoritmos
# =====================================================================
# Este archivo importa cada algoritmo de su módulo individual.
# Si algún módulo tiene un error de sintaxis o dependencia faltante,
# se atrapa la excepción y se registra en ERRORES_CARGA, pero el
# resto de la aplicación sigue funcionando normalmente.
#
# Así, un bug en (por ejemplo) bellman_ford.py NO rompe BFS ni Dijkstra.
# =====================================================================

import traceback

# Diccionario donde se registran los errores de carga.
# Clave: nombre del algoritmo, Valor: mensaje de error.
ERRORES_CARGA = {}

# ---- BFS ----
try:
    from algorithms.bfs import bfs_pasos
except Exception as e:
    ERRORES_CARGA['bfs'] = traceback.format_exc()
    bfs_pasos = None

# ---- DFS ----
try:
    from algorithms.dfs import dfs_pasos
except Exception as e:
    ERRORES_CARGA['dfs'] = traceback.format_exc()
    dfs_pasos = None

# ---- Dijkstra ----
try:
    from algorithms.dijkstra import dijkstra_pasos
except Exception as e:
    ERRORES_CARGA['dijkstra'] = traceback.format_exc()
    dijkstra_pasos = None

# ---- A* ----
try:
    from algorithms.a_star import a_star_pasos
except Exception as e:
    ERRORES_CARGA['astar'] = traceback.format_exc()
    a_star_pasos = None

# ---- Bellman-Ford ----
try:
    from algorithms.bellman_ford import bellman_ford_pasos
except Exception as e:
    ERRORES_CARGA['bellman'] = traceback.format_exc()
    bellman_ford_pasos = None

# ---- Kruskal ----
try:
    from algorithms.kruskal import kruskal_pasos
except Exception as e:
    ERRORES_CARGA['kruskal'] = traceback.format_exc()
    kruskal_pasos = None

# ---- Prim ----
try:
    from algorithms.prim import prim_pasos
except Exception as e:
    ERRORES_CARGA['prim'] = traceback.format_exc()
    prim_pasos = None


def algoritmo_disponible(nombre):
    """
    Verifica si un algoritmo se cargó correctamente.

    Parámetro:
        nombre: clave del algoritmo ('bfs', 'dfs', 'dijkstra', etc.)

    Retorna:
        True si está disponible, False si hubo error al importar.
    """
    return nombre not in ERRORES_CARGA


def obtener_error(nombre):
    """
    Retorna el mensaje de error de carga de un algoritmo, o None si no hubo error.
    """
    return ERRORES_CARGA.get(nombre, None)


# Imprimir resumen al cargar (útil para depuración en consola)
if ERRORES_CARGA:
    print("⚠ Algoritmos con errores de carga:")
    for nombre, error in ERRORES_CARGA.items():
        print(f"  ✗ {nombre}: {error.splitlines()[-1]}")
else:
    print("✓ Todos los algoritmos cargados correctamente")
