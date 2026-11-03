import matplotlib
matplotlib.use("Agg")

import random

import matplotlib.pyplot as plt
import numpy as np
import pytest

from GameofLife_F import GameOfLife_Engine
from Auxiliares import (
    BLINKER, BLOCK, BLOCO_INICIAL, GLIDER, N, NORMAIS,
    avanca, borda_const, conj_vivas, copia, cte_iguais, desloca, dif,
    estados_de_teste, grelha_de, m_async, m_sync,
)


def test_construtor_rejeita_parametros_invalidos():
    with pytest.raises(AssertionError):
        GameOfLife_Engine(16, "SYNC")             # N > 16
    with pytest.raises(AssertionError):
        GameOfLife_Engine(17, "OUTRO")            # modo inválido
    e = GameOfLife_Engine(17, "ASYNC")
    assert e.N == 17 and e.modo == "ASYNC"

def test_tipo_contagens_para_varios_N():
    for n in (17, 20, 25):
        e = GameOfLife_Engine(n, "SYNC")
        tipos = [e.tipo(i, j) for i in range(n + 2) for j in range(n + 2)]
        assert tipos.count("normal") == n * n
        assert tipos.count("inicial") == 2 * n + 1
        assert tipos.count("final") == 2 * n + 3
        assert len(tipos) == (n + 2) ** 2

def test_tipo_cantos_e_extremos():
    assert m_sync.tipo(0, 0) == "inicial"
    assert m_sync.tipo(0, N) == "inicial"
    assert m_sync.tipo(N, 0) == "inicial"
    assert m_sync.tipo(0, N + 1) == "final"        # canto: final, não inicial
    assert m_sync.tipo(N + 1, 0) == "final"
    assert m_sync.tipo(N + 1, N + 1) == "final"
    assert m_sync.tipo(N + 1, 5) == "final"
    assert m_sync.tipo(5, N + 1) == "final"
    assert m_sync.tipo(0, 5) == "inicial" and m_sync.tipo(5, 0) == "inicial"
    assert m_sync.tipo(1, 1) == "normal" and m_sync.tipo(N, N) == "normal"

def test_estado_inicial_bloco_finais_e_borda_constante():
    for v in (0, 1):
        g = m_sync.estado_inicial(v)
        assert conj_vivas(g) == BLOCO_INICIAL
        for i in range(N + 2):
            for j in range(N + 2):
                t = m_sync.tipo(i, j)
                if t == "inicial":
                    assert g[i][j] == v
                if t == "final":
                    assert g[i][j] == 0

def test_estado_inicial_borda_dicionario():
    b = borda_const(m_sync, 0)
    b[(0, 3)] = 1
    b[(7, 0)] = 1
    g = m_sync.estado_inicial(b)
    assert g[0][3] == 1 and g[7][0] == 1 and g[0][4] == 0 and g[0][0] == 0

def test_estado_inicial_borda_aleatoria_usa_os_dois_valores():
    random.seed(0)
    vistos = set()
    for _ in range(30):
        g = m_sync.estado_inicial()
        assert conj_vivas(g) == BLOCO_INICIAL
        vistos |= {g[i][j] for i in range(N + 2) for j in range(N + 2)
                   if m_sync.tipo(i, j) == "inicial"}
    assert vistos == {0, 1}

def test_estado_inicial_com_vivas_personalizadas():
    g = m_sync.estado_inicial(0, GLIDER)
    assert conj_vivas(g) == set(GLIDER)
    assert all(g[i][j] == 0 for i in range(N + 2) for j in range(N + 2)
               if m_sync.tipo(i, j) != "normal")

def test_estado_inicial_rejeita_vivas_fora_das_normais():
    for c in [(0, 5), (5, 0), (N + 1, 3), (3, N + 1), (N + 2, 2)]:
        with pytest.raises(ValueError):
            m_sync.estado_inicial(0, [c])


def test_conta_vizinhos_valores_conhecidos():
    g = m_sync.estado_inicial(0)
    assert m_sync.conta_vizinhos(g, 1, 1) == 3
    assert m_sync.conta_vizinhos(g, 1, 2) == 5
    assert m_sync.conta_vizinhos(g, 2, 2) == 8
    assert m_sync.conta_vizinhos(g, 4, 4) == 1
    assert m_sync.conta_vizinhos(g, 10, 10) == 0

def test_conta_vizinhos_conta_a_borda_mas_nao_as_finais_vivas():
    g = m_sync.estado_inicial(1)                  # iniciais todas vivas
    assert m_sync.conta_vizinhos(g, 1, 1) == 8    # 5 da borda + 3 do bloco
    assert m_sync.conta_vizinhos(g, 1, N) == 2    # (0,N+1) é final: vale 0
    assert m_sync.conta_vizinhos(g, N, 1) == 2    # (N+1,0) é final: vale 0
    assert m_sync.conta_vizinhos(g, N, N) == 0

def test_vizinhanca_e_a_do_enunciado_max_abs_igual_1():
    # Para cada normal (i,j): acender UMA célula (a,b) conta 1 sse max(|i-a|,|j-b|)==1.
    g = [[0] * (N + 2) for _ in range(N + 2)]
    for (i, j) in NORMAIS:
        for a in range(N + 2):
            for b in range(N + 2):
                g[a][b] = 1
                esperado = 1 if max(abs(i - a), abs(j - b)) == 1 else 0
                assert m_sync.conta_vizinhos(g, i, j) == esperado, (i, j, a, b)
                g[a][b] = 0

def test_proximo_valor_tabela_completa_B3_S23():
    # todas as 2^8 configurações de vizinhas x célula viva/morta, no centro da grelha
    desloc = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]
    for mascara in range(256):
        for propria in (0, 1):
            g = [[0] * (N + 2) for _ in range(N + 2)]
            g[9][9] = propria
            n = 0
            for k, (a, b) in enumerate(desloc):
                if mascara >> k & 1:
                    g[9 + a][9 + b] = 1
                    n += 1
            esperado = 1 if (n == 3 or (propria == 1 and n == 2)) else 0
            assert m_sync.proximo_valor(g, 9, 9) == esperado, (mascara, propria)

def test_proximo_valor_nao_altera_a_grelha():
    g = grelha_de(m_sync, BLOCK + [(5, 5), (5, 6)])
    antes = copia(g)
    for (i, j) in NORMAIS:
        m_sync.proximo_valor(g, i, j)
    assert g == antes

def test_c_vivas_conta_so_normais():
    assert m_sync.c_vivas(m_sync.estado_inicial(0)) == 9
    assert m_sync.c_vivas(m_sync.estado_inicial(1)) == 9     # borda viva não conta
    assert m_sync.c_vivas(grelha_de(m_sync, [])) == 0
    assert m_sync.c_vivas(grelha_de(m_sync, [(5, 5), (N, N), (1, 1)])) == 3

def test_estado_erro_so_quando_nao_ha_normais_vivas():
    assert not m_sync.estado_erro(m_sync.estado_inicial(0))
    assert m_sync.estado_erro(grelha_de(m_sync, [], 0))
    assert m_sync.estado_erro(grelha_de(m_sync, [], 1))      # borda viva, normais mortas
    assert not m_sync.estado_erro(grelha_de(m_sync, [(N, N)]))


def test_bloco_e_estavel():
    g = grelha_de(m_sync, BLOCK)
    assert conj_vivas(m_sync.sucessores(g)[0]) == set(BLOCK)
    assert conj_vivas(avanca(m_sync, g, 10)) == set(BLOCK)

def test_blinker_tem_periodo_2():
    g = grelha_de(m_sync, BLINKER)                       # horizontal na linha 4
    vertical = {(3, 5), (4, 5), (5, 5)}
    assert conj_vivas(avanca(m_sync, g, 1)) == vertical
    assert conj_vivas(avanca(m_sync, g, 2)) == set(BLINKER)
    assert conj_vivas(avanca(m_sync, g, 11)) == vertical
    assert conj_vivas(avanca(m_sync, g, 12)) == set(BLINKER)

def test_blinker_com_borda_viva_longe_nao_e_afetado():
    g = m_sync.estado_inicial(borda_const(m_sync, 1), [(12, 12), (12, 13), (12, 14)])
    # o blinker está a mais de 1 célula do bordo e do bloco: só a evolução local conta
    h = avanca(m_sync, g, 1)
    assert {(11, 13), (12, 13), (13, 13)} <= conj_vivas(h)

def test_glider_desloca_uma_celula_na_diagonal_de_4_em_4_passos():
    g = grelha_de(m_sync, GLIDER)
    for k in range(1, 11):                               # 40 passos, ainda longe do fim
        g = avanca(m_sync, g, 4)
        assert conj_vivas(g) == desloca(GLIDER, k, k), f"após {4 * k} passos"

def test_glider_tem_sempre_5_celulas_enquanto_livre():
    g = grelha_de(m_sync, GLIDER)
    for _ in range(40):
        assert m_sync.c_vivas(g) == 5
        g = avanca(m_sync, g, 1)

def test_glider_contra_o_bordo_final_mantem_constantes():
    g0 = grelha_de(m_sync, GLIDER)
    g = g0
    for _ in range(80):                                  # chega ao fim da grelha
        g = avanca(m_sync, g, 1)
        assert cte_iguais(m_sync, g0, g)                 # finais continuam a 0
        assert all(v in (0, 1) for linha in g for v in linha)

def test_primeiro_passo_do_estado_inicial_do_enunciado_com_borda_zero():
    g = m_sync.estado_inicial(0)
    esperado = {(1, 1), (1, 3), (3, 1), (3, 3), (2, 4), (4, 2)}
    assert conj_vivas(avanca(m_sync, g, 1)) == esperado

def test_estado_inicial_do_enunciado_com_borda_zero_estabiliza_ao_passo_4():
    g = avanca(m_sync, m_sync.estado_inicial(0), 4)
    assert m_sync.c_vivas(g) == 7                        # still life de 7 células
    assert m_sync.sucessores(g)[0] == g                  # ponto fixo
    assert avanca(m_sync, g, 20) == g


def test_sync_devolve_um_unico_sucessor_e_nao_altera_a_entrada():
    for g in estados_de_teste():
        antes = copia(g)
        s = m_sync.sucessores(g)
        assert len(s) == 1
        assert g == antes

def test_sync_le_sempre_o_estado_antigo():
    for g in estados_de_teste():
        h = m_sync.sucessores(g)[0]
        for (i, j) in NORMAIS:
            assert h[i][j] == m_sync.proximo_valor(g, i, j)

def test_sync_mantem_iniciais_e_finais():
    for g in estados_de_teste():
        assert cte_iguais(m_sync, g, m_sync.sucessores(g)[0])

def test_async_devolve_N_ao_quadrado_sucessores_cada_um_difere_em_no_maximo_uma_celula():
    for g in estados_de_teste():
        antes = copia(g)
        s = m_async.sucessores(g)
        assert len(s) == N * N
        assert g == antes
        for k, h in enumerate(s):
            i, j = divmod(k, N)                      # ordem dos ciclos: linha, coluna
            assert set(dif(g, h)) <= {(i + 1, j + 1)}
            assert cte_iguais(m_async, g, h)

def test_async_cada_sucessor_e_o_sync_restrito_a_essa_celula():
    for g in estados_de_teste():
        sync = m_sync.sucessores(g)[0]
        for k, h in enumerate(m_async.sucessores(g)):
            i, j = divmod(k, N)
            esperado = copia(g)
            esperado[i + 1][j + 1] = sync[i + 1][j + 1]
            assert h == esperado

def test_async_blinker_so_4_sucessores_diferem_e_os_restantes_sao_auto_ciclos():
    g = grelha_de(m_async, BLINKER)
    s = m_async.sucessores(g)
    mudancas = [dif(g, h) for h in s if h != g]
    assert sorted(mudancas) == [[(3, 5)], [(4, 4)], [(4, 6)], [(5, 5)]]
    assert sum(1 for h in s if h == g) == N * N - 4

def test_async_estado_de_erro_e_sumidouro_com_borda_zero():
    g = grelha_de(m_async, [], 0)
    assert all(h == g for h in m_async.sucessores(g))

def test_modo_invalido_em_sucessores_levanta_erro():
    e = GameOfLife_Engine(N, "SYNC")
    e.modo = "OUTRO"
    with pytest.raises(ValueError):
        e.sucessores(e.estado_inicial(0))

def test_passo_sync_e_o_unico_sucessor():
    for g in estados_de_teste():
        assert m_sync.passo(g) == m_sync.sucessores(g)[0]

def test_passo_async_e_um_dos_sucessores_e_nao_altera_a_entrada():
    random.seed(3)
    g = grelha_de(m_async, BLINKER)
    for _ in range(15):
        antes = copia(g)
        h = m_async.passo(g)
        assert g == antes
        assert h in m_async.sucessores(g)
        g = h

def test_execucoes_longas_preservam_constantes_nos_dois_modos():
    random.seed(11)
    for e in (m_sync, m_async):
        for _ in range(3):
            g0 = e.estado_inicial()
            g = g0
            for _ in range(300):
                g = e.passo(g)
                assert cte_iguais(e, g0, g)
                assert all(v in (0, 1) for linha in g for v in linha)
