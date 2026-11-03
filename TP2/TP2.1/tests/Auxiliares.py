"""Fixtures e funções auxiliares partilhadas pelos testes."""
import random
from functools import cache

import z3

from GameofLife_F import (GameOfLife_Engine, I_z3, T_main, extrair, grelha_z3)

N = 30

m_sync = GameOfLife_Engine(N, "SYNC")
m_async = GameOfLife_Engine(N, "ASYNC")

GLIDER = [(2, 3), (3, 4), (4, 2), (4, 3), (4, 4)]
BLINKER = [(4, 4), (4, 5), (4, 6)]
BLOCK = [(8, 8), (8, 9), (9, 8), (9, 9)]
BLOCO_INICIAL = {(i, j) for i in (1, 2, 3) for j in (1, 2, 3)}
NORMAIS = [(i, j) for i in range(1, N + 1) for j in range(1, N + 1)]

def conj_vivas(g):                      # conjunto das normais vivas
    return {(i, j) for (i, j) in NORMAIS if g[i][j] == 1}

def dif(a, b):                          # posições onde duas grelhas diferem
    return [(i, j) for i in range(N + 2) for j in range(N + 2) if a[i][j] != b[i][j]]

def copia(g):
    return [linha[:] for linha in g]

def avanca(e, g, n):                    # n passos SYNC
    for _ in range(n):
        g = e.sucessores(g)[0]
    return g

def desloca(celulas, di, dj):
    return {(i + di, j + dj) for (i, j) in celulas}

def borda_const(e, v):                  # dicionário {célula inicial: v}
    return {(i, j): v for i in range(N + 2) for j in range(N + 2)
            if e.tipo(i, j) == "inicial"}

def cte_iguais(e, a, b):                # iniciais e finais iguais nas duas grelhas?
    return all(a[i][j] == b[i][j] for i in range(N + 2) for j in range(N + 2)
               if e.tipo(i, j) != "normal")

def grelha_de(e, vivas_lista, borda=0):  # estado só com estas normais vivas
    return e.estado_inicial(borda, vivas_lista)

def estados_de_teste():                 # estados variados para os testes do motor
    random.seed(5)
    return [
        m_sync.estado_inicial(0), m_sync.estado_inicial(1), m_sync.estado_inicial(),
        grelha_de(m_sync, BLINKER), grelha_de(m_sync, GLIDER),
        grelha_de(m_sync, BLOCK + BLINKER),
    ]

def estados_z3():                       # estados para a validação cruzada com o Z3
    random.seed(7)
    base = [
        m_sync.estado_inicial(0), m_sync.estado_inicial(1), m_sync.estado_inicial(),
        m_sync.estado_inicial(), grelha_de(m_sync, BLINKER), grelha_de(m_sync, GLIDER),
        grelha_de(m_sync, BLOCK),
    ]
    extra = [avanca(m_sync, g, 3) for g in base[:4]]        # estados mais "evoluídos"
    return base + extra


@cache
def resolvedor_T(modo):
    s = z3.Solver()
    s.add(T_main(N, 0, modo))
    return s

def literal(var, valor):
    return var if valor else z3.Not(var)

def lits_normais(g, t):
    """Fixa as células normais do instante t aos valores da grelha g."""
    gz = grelha_z3(N, t)
    return [literal(gz[i][j], g[i][j])
            for i in range(1, N + 1) for j in range(1, N + 1)]

def aceita(modo, g, h):
    """T(g -> h) é satisfazível? g e h são grelhas completas do motor.
    Fixa as normais de g (t=0) e de h (t=1) e as iniciais (partilhadas)."""
    g0, g1 = grelha_z3(N, 0), grelha_z3(N, 1)
    lits = []
    for i in range(N + 2):
        for j in range(N + 2):
            t = m_sync.tipo(i, j)
            if t == "final":
                if g[i][j] != 0 or h[i][j] != 0:
                    return False             # finais são constantes 0
            elif t == "inicial":             # mesma variável nos dois instantes
                lits += [literal(g0[i][j], g[i][j]), literal(g0[i][j], h[i][j])]
            else:
                lits += [literal(g0[i][j], g[i][j]), literal(g1[i][j], h[i][j])]
    return resolvedor_T(modo).check(*lits) == z3.sat

def traco_z3(modo, k):
    """Traço de k transições, gerado pelo Z3 a partir do estado inicial."""
    s = z3.Solver()
    s.add(I_z3(N))
    for t in range(k):
        s.add(T_main(N, t, modo))
    assert s.check() == z3.sat
    return extrair(s.model(), N, k)