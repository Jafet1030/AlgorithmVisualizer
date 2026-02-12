# =====================================================================
# algorithms/prim.py — Algoritmo de Prim (Árbol de Expansión Mínima)
# =====================================================================
# Construye el MST partiendo desde un nodo arbitrario (nodo 0).
# En cada paso, agrega la arista de menor peso que conecte un nodo
# ya incluido con uno que aún no lo está.
#
# Complejidad: O(E log V) con heap binario.
# =====================================================================

import heapq
from grafo import matriz_a_lista_ady


def prim_pasos(ga):
    """
    Ejecuta Prim paso a paso.

    Parámetro:
        ga: Instancia de GrafoActivo.

    Retorna:
        Lista de pasos, cada uno con:
          - 'actual':    nodo recién agregado al MST
          - 'visitados': lista de nodos ya incluidos en el MST
          - 'mst':       lista de aristas (u, v) del MST parcial
    """
    lista = matriz_a_lista_ady(ga.matriz)   # Convertir a lista de adyacencia
    visitado = [False] * ga.N
    heap = [(0, 0)]                          # (peso, nodo) — empezar desde nodo 0
    mst = []                                 # Aristas del MST
    padre = [-1] * ga.N                      # padre[v] = u si la arista u-v está en MST
    pasos = []

    while heap:
        peso, u = heapq.heappop(heap)        # Extraer arista de menor peso

        if visitado[u]:
            continue                         # Ya procesado, saltar

        visitado[u] = True

        # Si tiene padre (no es el nodo raíz), agregar la arista al MST
        if padre[u] != -1:
            mst.append((padre[u], u))

        # Guardar snapshot
        pasos.append({
            'actual': u,
            'visitados': [i for i in range(ga.N) if visitado[i]],
            'mst': list(mst)
        })

        # Agregar aristas hacia vecinos no visitados al heap
        for v, w in lista[u]:
            if not visitado[v]:
                padre[v] = u
                heapq.heappush(heap, (w, v))

    return pasos
