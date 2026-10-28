# /// script
# dependencies = [
#     "marimo",
#     "matplotlib==3.11.2",
#     "numpy==2.5.4",
#     "z3-solver==5.3.2.0",
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
    import matplotlib.pyplot as plt
    import numpy as np
 

    return np, plt, random


@app.cell
def _():
    # Parâmetros do trabalho 
    N = 17
    MODO = "SYNC"   # "SYNC" (todas em simultâneo) ou "ASYNC" (uma de cada vez)
    return MODO, N


@app.cell
def _(np, plt, random):
    class GameOfLife_Engine:
        def __init__(self, N, modo):
            assert N > 16
            assert modo in ("SYNC", "ASYNC")
            self.N = N
            self.modo = modo  
 
        def tipo(self, i, j):
            N = self.N
            if max(i, j) == N + 1:    # um índice é N+1 -> final
                return "final"
            if min(i, j) == 0:        # um índice é 0 (e nenhum é N+1) -> inicial
                return "inicial"
            return "normal"
 
        def estado_inicial(self, borda=None, vivas=None):
            """
            borda: None -> aleatória | int (0/1) -> constante | dict {(i,j): valor}
            vivas: None -> regra do enunciado (bloco 3x3)
                   iterável de (i,j) -> só essas casas normais começam vivas
            """
            N = self.N
    
            if vivas is not None:
                vivas = set(vivas)
                for (i, j) in vivas:
                    if not (1 <= i <= N and 1 <= j <= N):
                        raise ValueError(f"({i},{j}) não é uma casa normal")
    
            grelha = [[0] * (N + 2) for _ in range(N + 2)]
            for i in range(N + 2):
                for j in range(N + 2):
                    t = self.tipo(i, j)
                    if t == "inicial":
                        if borda is None:
                            grelha[i][j] = random.randint(0, 1)
                        elif isinstance(borda, dict):
                            grelha[i][j] = borda[(i, j)]
                        else:
                            grelha[i][j] = borda          # valor constante
                    elif t == "normal":
                        if vivas is None:
                            grelha[i][j] = 1 if (i <= 3 and j <= 3) else 0
                        else:
                            grelha[i][j] = 1 if (i, j) in vivas else 0
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


            
        def passo(self, g):
            """Um passo de simulação: devolve UMA grelha."""
            if self.modo == "SYNC":
                return self.sucessores(g)[0]
            # ASYNC: atualiza só uma célula aleatória 
            i = random.randint(1, self.N)
            j = random.randint(1, self.N)
            nova = [linha[:] for linha in g]
            nova[i][j] = self.proximo_valor(g, i, j)
            return nova

        def c_vivas(self,grid):
            N = len(grid) - 2
            return sum(sum(linha[1:N + 1]) for linha in grid[1:N + 1])
        
    #LLM inicio        
        def imprimir_grid(self,grid, tamanho=5):
            fig, ax = plt.subplots(figsize=(tamanho, tamanho))
            ax.imshow(np.array(grid), cmap="gray", vmin=0, vmax=1, interpolation="nearest")
            ax.axis("off")
            return fig
    #LLM fim
    return (GameOfLife_Engine,)


@app.cell
def _(GameOfLife_Engine, MODO, N, plt):
    def simulacao(engine, steps, borda=None, vivas=None, mostrar=True):   
        g = engine.estado_inicial(borda, vivas)                           
        historico = [engine.c_vivas(g)]

        for k in range(steps):
            if mostrar:
                fig = engine.imprimir_grid(g)
                fig.suptitle(f"Passo {k} | vivas: {historico[-1]}")
                plt.show()
                plt.close(fig)
            g = engine.passo(g)
            historico.append(engine.c_vivas(g))

        return g, historico


    engine = GameOfLife_Engine(N, MODO)
    g_final, vivas = simulacao(engine, 5)
    """
    Ao cumpre as regras do enenciado, apenas usado para mostrar que a engine simula corretamente o game of life utilizando estruturas de celulas conhecidas 
    glider = [(2, 3), (3, 4), (4, 2), (4, 3), (4, 4)]
    blinker=[(4, 4), (4, 5), (4, 6)]

    g_final, vivas = simulacao(engine, 30,0,glider) 
    g_final, vivas = simulacao(engine, 30,0,blinker) 
    """
    print(vivas)
    return (engine,)


@app.cell
def _():
    import z3

    def grelha_z3(N,t):
    
        g_z3 = [[0] * (N + 2) for _ in range(N + 2)]
    
        for i in range(len(g_z3)):
            for j in range(len(g_z3)):
                if max(i,j) == N+1:
                    g_z3[i][j] = False
                elif min(i, j) == 0:         
                    g_z3[i][j] = z3.Bool(f"Cons_{i}_{j}") 
                else:
                    g_z3[i][j] = z3.Bool(f"n_{i}_{j}_{t}")
            
        return g_z3


    def c_vizinhos (g,i,j):
        vizinhos = []
        h = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (dx, dy) != (0, 0):
                    vizinhos[h] = g[i + dx][j + dy]
                    h += 1
        
        return vizinhos

    def c_contagem(vizinhos):
        return z3.Sum([z3.If(v, 1, 0) for v in vizinhos])

    def proximo_z3(x ,c):
        return (z3.If(c == 3,True,z3.If(c==2,x,False)))

    return c_contagem, c_vizinhos, grelha_z3, proximo_z3, z3


@app.cell
def _(engine, proximo_z3, z3):
    # LLM: estrutura do teste (gerada na conversa com o Claude)


    def teste_proximo(engine):
        x = z3.Bool("x")
        c = z3.Int("c")
    
        expr = proximo_z3(x, c)          # fórmula simbólica, avaliada por modelo

        posicoes = [(a, b) for a in range(3) for b in range(3) if (a, b) != (1, 1)]

        def regra(xv, cv):
            if cv == 3:
                return "nasce" if xv == 0 else "sobrevive"
            if cv == 2:
                return "continua morta" if xv == 0 else "sobrevive"
            return "continua morta" if xv == 0 else "morre"

        print(f"{'x':>2} {'c':>2} | {'engine':>6} {'z3':>3} | {'ok':>2} | regra")
        print("-" * 46)

        falhas = 0
        for xv in (0, 1):
            for cv in range(9):
                # grelha 3x3 concreta: centro = xv e exatamente cv vizinhos vivos
                g = [[0] * 3 for _ in range(3)]
                g[1][1] = xv
                for (a, b) in posicoes[:cv]:
                    g[a][b] = 1
                assert engine.conta_vizinhos(g, 1, 1) == cv   # sanidade do teste

                esperado = engine.proximo_valor(g, 1, 1)

                s = z3.Solver()
                s.add(x == bool(xv), c == cv)                 # fixa o caso
                assert s.check() == z3.sat
                obtido = int(z3.is_true(s.model().eval(expr, model_completion=True)))

                ok = (obtido == esperado)
                falhas += not ok
                print(f"{xv:>2} {cv:>2} | {esperado:>6} {obtido:>3} | "
                      f"{'✓' if ok else '✗':>2} | {regra(xv, cv)}")

        print("-" * 46)
        print(f"{18 - falhas}/18 casos coincidem")
        assert falhas == 0

    teste_proximo(engine)
    return


@app.cell
def _(c_contagem, c_vizinhos, grelha_z3, prox, proximo_z3, z3):

    def T_sync(N, t):
        g  = grelha_z3(N, t)       
        gp = grelha_z3(N, t + 1)  
        restricoes = []

        for i in range(1,N+1):              
            for j in range(1,N+1):
                v = c_vizinhos(g,i,j)
                c = c_contagem(v)
                porx = proximo_z3(g[i][j],c)
                restricoes.append(gp[i][j] == prox )

        return z3.And(restricoes)

    return


if __name__ == "__main__":
    app.run()
