# =====================================================================
# algorithms/bellman_ford.py — Algoritmo de Bellman-Ford
# =====================================================================
# Encuentra la ruta más corta desde un origen a todos los demás nodos.
# A diferencia de Dijkstra, soporta aristas con pesos negativos.
# Funciona relajando TODAS las aristas repetidamente (N-1 veces).
#
# Complejidad: O(V * E)
# =====================================================================

from grafo import matriz_a_aristas


def bellman_ford_pasos(ga, origen, objetivo):
    """
    Ejecuta Bellman-Ford paso a paso, registrando cada relajación.

    Parámetros:
        ga:       Instancia de GrafoActivo.
        origen:   Índice del nodo origen.
        objetivo: Índice del nodo destino.

    Retorna:
        (pasos, camino, dist) donde:
          - pasos:  lista detallada de cada relajación o convergencia
          - camino: ruta más corta como lista de índices
          - dist:   lista de distancias finales
    """
    # Obtener todas las aristas como (u, v, peso)
    grafo = matriz_a_aristas(ga.matriz)

    dist = [float('inf')] * ga.N     # Distancias tentativas
    dist[origen] = 0                  # Origen tiene distancia 0
    padre = {origen: None}            # Para reconstruir el camino
    pasos = []

    # Repetir N-1 veces (máximo de relajaciones necesarias)
    for i in range(ga.N - 1):
        cambio_en_iteracion = False

        # Intentar relajar CADA arista del grafo
        for u, v, peso in grafo:
            dist_anterior = dist[v]

            # ¿Podemos mejorar la distancia a v pasando por u?
            if dist[u] != float('inf') and dist[u] + peso < dist[v]:
                dist[v] = dist[u] + peso
                padre[v] = u
                cambio_en_iteracion = True

                # Registrar esta relajación exitosa con todos los detalles
                pasos.append({
                    'iter': i + 1,                # Número de iteración
                    'dist': dist[:],               # Distancias actuales
                    'padre': dict(padre),          # Árbol de padres
                    'cambio': True,
                    'arista_evaluada': (u, v),     # Arista que se relajó
                    'peso': peso,                  # Peso de la arista
                    'dist_anterior': dist_anterior, # Distancia ANTES de relajar
                    'dist_nueva': dist[v],          # Distancia DESPUÉS de relajar
                    'tipo': 'relajacion'
                })

        # Si ninguna arista mejoró, el algoritmo convergió temprano
        if not cambio_en_iteracion:
            pasos.append({
                'iter': i + 1,
                'dist': dist[:],
                'padre': dict(padre),
                'cambio': False,
                'tipo': 'sin_cambios'
            })
            break

    # Reconstruir el camino más corto
    camino = []
    n = objetivo
    while n is not None and n in padre:
        camino.append(n)
        n = padre[n]
    camino.reverse()

    return pasos, camino, dist
