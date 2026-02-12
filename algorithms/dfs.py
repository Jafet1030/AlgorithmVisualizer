# =====================================================================
# algorithms/dfs.py — Búsqueda en Profundidad (Depth-First Search)
# =====================================================================
# Explora el grafo yendo lo más profundo posible por cada rama
# antes de retroceder (backtracking). Usa recursión (pila implícita).
#
# Complejidad: O(V + E) donde V = nodos, E = aristas.
# =====================================================================


def dfs_pasos(ga, inicio):
    """
    Ejecuta DFS recursivo y registra cada paso para la animación.

    Parámetros:
        ga:     Instancia de GrafoActivo.
        inicio: Índice del nodo raíz.

    Retorna:
        Lista de pasos con la misma estructura que BFS:
          - 'actual', 'visitados', 'padre'
    """
    visitado = set()
    padre = {inicio: None}
    pasos = []

    def _dfs(u):
        """Función recursiva interna que realiza el recorrido."""
        visitado.add(u)

        # Capturar el estado en este momento de la exploración
        pasos.append({
            'actual': u,
            'visitados': set(visitado),
            'padre': dict(padre)
        })

        # Recorrer vecinos en orden de índice
        for v in range(ga.N):
            if ga.matriz[u][v] > 0 and v not in visitado:
                padre[v] = u          # Registrar arista del árbol DFS
                _dfs(v)               # Llamada recursiva (profundizar)

    _dfs(inicio)
    return pasos
