# =====================================================================
# algorithms/bfs.py — Búsqueda en Anchura (Breadth-First Search)
# =====================================================================
# Explora el grafo nivel por nivel desde un nodo de inicio.
# Usa una cola (FIFO) para garantizar que los nodos más cercanos
# (en número de saltos) se visiten primero.
#
# Complejidad: O(V + E) donde V = nodos, E = aristas.
# =====================================================================

from collections import deque


def bfs_pasos(ga, inicio):
    """
    Ejecuta BFS y registra cada paso para la animación.

    Parámetros:
        ga:     Instancia de GrafoActivo con la matriz y metadatos.
        inicio: Índice del nodo donde comienza la búsqueda.

    Retorna:
        Lista de diccionarios, cada uno representando un paso:
          - 'actual':    índice del nodo que se está visitando
          - 'visitados': conjunto de nodos ya visitados hasta este paso
          - 'padre':     diccionario {nodo: nodo_padre} para reconstruir
                         el árbol de recorrido
    """
    visitado = set()
    cola = deque([inicio])           # Cola FIFO con nodos por explorar
    padre = {inicio: None}           # Árbol de recorrido (raíz no tiene padre)
    pasos = []

    while cola:
        u = cola.popleft()           # Sacar el primero de la cola

        if u not in visitado:
            visitado.add(u)
            # Guardar una foto del estado actual
            pasos.append({
                'actual': u,
                'visitados': set(visitado),
                'padre': dict(padre)
            })

            # Explorar vecinos: si tienen arista (peso > 0) y no fueron visitados
            for v in range(ga.N):
                if ga.matriz[u][v] > 0 and v not in visitado:
                    if v not in padre:
                        padre[v] = u     # Registrar cómo llegamos a v
                    cola.append(v)       # Encolar para visitar después

    return pasos
