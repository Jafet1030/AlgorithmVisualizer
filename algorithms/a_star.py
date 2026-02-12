# =====================================================================
# algorithms/a_star.py — Algoritmo A* (A-Star)
# =====================================================================
# Variante informada de Dijkstra que usa una heurística h(n) para
# estimar la distancia restante al objetivo. La función de evaluación
# es f(n) = g(n) + h(n), donde g(n) es el costo real acumulado.
#
# La heurística usada aquí es la distancia euclidiana entre posiciones
# ficticias en una cuadrícula (generadas por generar_coords).
#
# Complejidad: depende de la heurística; en el mejor caso O(V log V).
# =====================================================================

import heapq
from grafo import generar_coords


def a_star_pasos(ga, inicio, objetivo):
    """
    Ejecuta A* paso a paso.

    Parámetros:
        ga:       Instancia de GrafoActivo.
        inicio:   Índice del nodo origen.
        objetivo: Índice del nodo destino.

    Retorna:
        (pasos, camino, g) donde:
          - pasos:  snapshots de cada iteración
          - camino: lista de índices del camino encontrado
          - g:      diccionario {nodo: costo_real} al finalizar
    """
    import math

    # Generar coordenadas ficticias para la heurística
    coords = generar_coords(ga.N)

    def h(a, b):
        """Heurística: distancia euclidiana entre nodos a y b."""
        return math.hypot(
            coords[b][0] - coords[a][0],
            coords[b][1] - coords[a][1]
        )

    # Cola de prioridad con f(n) = g(n) + h(n)
    pq = [(h(inicio, objetivo), inicio)]
    g = {inicio: 0}            # Costo real acumulado desde el origen
    padre = {inicio: None}     # Árbol de búsqueda
    pasos = []
    visitado = set()

    while pq:
        _, u = heapq.heappop(pq)  # Extraer nodo con menor f(n)

        if u in visitado:
            continue

        visitado.add(u)

        # Snapshot del estado
        pasos.append({
            'actual': u,
            'visitados': set(visitado),
            'g': dict(g),
            'padre': dict(padre)
        })

        # Si alcanzamos el objetivo, terminamos
        if u == objetivo:
            break

        # Expandir vecinos
        for v in range(ga.N):
            if ga.matriz[u][v] > 0:
                nuevo = g[u] + ga.matriz[u][v]
                # Solo actualizar si encontramos un camino mejor
                if v not in g or nuevo < g[v]:
                    g[v] = nuevo
                    padre[v] = u
                    # Prioridad = costo real + estimación al destino
                    heapq.heappush(pq, (nuevo + h(v, objetivo), v))

    # Reconstruir camino
    camino = []
    n = objetivo
    while n is not None and n in padre:
        camino.append(n)
        n = padre[n]
    camino.reverse()

    return pasos, camino, g
