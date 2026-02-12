# =====================================================================
# algorithms/dijkstra.py — Algoritmo de Dijkstra
# =====================================================================
# Encuentra la ruta más corta entre un nodo origen y un destino
# en grafos con pesos NO negativos. Usa un min-heap (cola de prioridad)
# para siempre procesar el nodo con menor distancia acumulada.
#
# Complejidad: O((V + E) log V) con heap binario.
# =====================================================================

import heapq


def dijkstra_pasos(ga, inicio, objetivo):
    """
    Ejecuta Dijkstra paso a paso.

    Parámetros:
        ga:       Instancia de GrafoActivo.
        inicio:   Índice del nodo origen.
        objetivo: Índice del nodo destino.

    Retorna:
        (pasos, camino, dist) donde:
          - pasos:  lista de snapshots del estado en cada iteración
          - camino: lista de índices del camino más corto [inicio, ..., objetivo]
          - dist:   lista de distancias finales desde el origen a cada nodo
    """
    dist = [float('inf')] * ga.N     # Distancias tentativas (infinito al inicio)
    padre = {inicio: None}           # Para reconstruir el camino
    dist[inicio] = 0                 # Distancia al origen es 0
    pq = [(0, inicio)]               # Min-heap: (distancia_acumulada, nodo)
    pasos = []
    visitado = set()

    while pq:
        costo, u = heapq.heappop(pq)  # Extraer nodo con menor distancia

        # Si ya lo procesamos, saltar (puede haber entradas duplicadas en el heap)
        if u in visitado:
            continue

        visitado.add(u)

        # Guardar snapshot del estado actual
        pasos.append({
            'actual': u,
            'visitados': set(visitado),
            'dist': dist[:],           # Copia de las distancias actuales
            'padre': dict(padre)
        })

        # Si llegamos al destino, podemos parar
        if u == objetivo:
            break

        # Relajar aristas: intentar mejorar la distancia a cada vecino
        for v in range(ga.N):
            if ga.matriz[u][v] > 0:
                nuevo = costo + ga.matriz[u][v]
                if nuevo < dist[v]:
                    dist[v] = nuevo
                    padre[v] = u
                    heapq.heappush(pq, (nuevo, v))  # Agregar con nueva prioridad

    # Reconstruir el camino desde el destino hasta el origen
    camino = []
    n = objetivo
    while n is not None and n in padre:
        camino.append(n)
        n = padre[n]
    camino.reverse()

    return pasos, camino, dist
