# /// script
# dependencies = [
#     "marimo",
# ]
# requires-python = ">=3.12"
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import random
    from collections import Counter
 

    return (random,)


@app.cell
def _():
    # Parâmetros do trabalho (definidos UMA só vez; o resto do notebook lê daqui)
    N = 17
    MODO = "SYNC"   # "SYNC" (todas em simultâneo) ou "ASYNC" (uma de cada vez)
    return


@app.cell
def _(random):
    class GameOfLife_Engine:
        def __init__(self, N, modo):
            assert N > 16
            assert modo in ("SYNC", "ASYNC")
            self.N = N
            self.modo = modo  # SYNC: todas ao mesmo tempo; ASYNC: uma de cada vez
 
        def tipo(self, i, j):
            N = self.N
            if max(i, j) == N + 1:    # um índice é N+1 -> final
                return "final"
            if min(i, j) == 0:        # um índice é 0 (e nenhum é N+1) -> inicial
                return "inicial"
            return "normal"
 
        def estado_inicial(self, borda=None):
            N = self.N
            grelha = [[0] * (N + 2) for _ in range(N + 2)]
            for i in range(N + 2):
                for j in range(N + 2):
                    t = self.tipo(i, j)
                    if t == "inicial":
                        grelha[i][j] = random.randint(0, 1) if borda is None else borda[(i, j)]
                    elif t == "normal":
                        grelha[i][j] = 1 if (i <= 3 and j <= 3) else 0
            return grelha
 
        def conta_vizinhos(self, g, i, j):
            vivos = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (dx, dy) != (0, 0):
                        vivos += g[i + dx][j + dy]
            return vivos
 
        def proximo_valor(self, g, i, j):
            v = self.conta_vizinhos(g, i, j)
            if v == 3:
                return 1              # nasce ou sobrevive
            if v == 2:
                return g[i][j]        # mantém o valor atual
            return 0                  # morre ou continua morta
 
        def sucessores(self, g):
            N = self.N
 
            if self.modo == "SYNC":
                nova = [linha[:] for linha in g]               # mantém iniciais e finais
                for i in range(1, N + 1):
                    for j in range(1, N + 1):
                        nova[i][j] = self.proximo_valor(g, i, j)   # lê sempre de g (antiga)
                return [nova]
 
            elif self.modo == "ASYNC":
                resultado = []
                for i in range(1, N + 1):
                    for j in range(1, N + 1):
                        nova = [linha[:] for linha in g]       # uma cópia por escolha
                        nova[i][j] = self.proximo_valor(g, i, j)
                        resultado.append(nova)
                return resultado
 
            else:
                raise ValueError("modo inválido: usa 'SYNC' ou 'ASYNC'")
 

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
