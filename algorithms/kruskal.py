# =====================================================================
# algorithms/kruskal.py — Algoritmo de Kruskal (Árbol de Expansión Mínima)
# =====================================================================
# Construye el MST (Minimum Spanning Tree) seleccionando aristas
# de menor a mayor peso, siempre que no formen un ciclo.
# Usa Union-Find (Disjoint Set Union) para detectar ciclos en O(α(n)).
#
# Complejidad: O(E log E) por el ordenamiento de aristas.
# =====================================================================


def kruskal_pasos(ga):
    """
    Ejecuta Kruskal paso a paso.

    Parámetro:
        ga: Instancia de GrafoActivo.

    Retorna:
        Lista de pasos, cada uno con:
          - 'edge': (u, v) arista evaluada
          - 'w':    peso de la arista
          - 'ok':   True si se aceptó (no forma ciclo), False si se rechazó
          - 'mst':  lista de aristas aceptadas hasta ahora
    """
    # Extraer y ordenar todas las aristas por peso (solo parte superior de la matriz)
    aristas = sorted(
        [
            (i, j, ga.matriz[i][j])
            for i in range(ga.N)
            for j in range(i + 1, ga.N)
            if ga.matriz[i][j] > 0
        ],
        key=lambda x: x[2]   # Ordenar por peso ascendente
    )

    # ---- Union-Find (Disjoint Set Union) con compresión de camino ----
    padre_uf = list(range(ga.N))   # Cada nodo es su propio padre al inicio

    def find(x):
        """Encuentra el representante del conjunto con compresión de camino."""
        if padre_uf[x] != x:
            padre_uf[x] = find(padre_uf[x])  # Compresión: apuntar directo a la raíz
        return padre_uf[x]

    mst = []       # Aristas del MST acumuladas
    pasos = []

    for u, v, w in aristas:
        ru, rv = find(u), find(v)     # Raíces de los conjuntos de u y v
        aceptada = (ru != rv)          # Aceptar solo si están en conjuntos distintos

        if aceptada:
            padre_uf[ru] = rv          # Unir los dos conjuntos
            mst.append((u, v))

        # Registrar el paso (aceptada o rechazada)
        pasos.append({
            'edge': (u, v),
            'w': w,
            'ok': aceptada,
            'mst': list(mst)           # Copia del MST hasta ahora
        })

    return pasos
