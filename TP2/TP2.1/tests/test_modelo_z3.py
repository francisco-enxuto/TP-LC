import random

import pytest
import z3

from GameofLife_F import (
    I_z3, T_main, c_vizinhos, erro_z3, grelha_z3, proximo_z3, regra_z3,
    validatraco_z3,
)
from Auxiliares import (
    BLINKER, BLOCK, BLOCO_INICIAL, N, NORMAIS,
    aceita, conj_vivas, copia, dif, estados_z3, grelha_de, literal,
    lits_normais, m_async, m_sync, traco_z3,
)


def test_grelha_z3_dimensoes_e_tipos_de_variavel():
    g0, g1 = grelha_z3(N, 0), grelha_z3(N, 1)
    assert len(g0) == N + 2 and all(len(l) == N + 2 for l in g0)
    for i in range(N + 2):
        for j in range(N + 2):
            t = m_sync.tipo(i, j)
            if t == "final":
                assert z3.is_false(g0[i][j]) and z3.is_false(g1[i][j])
            elif t == "inicial":
                assert g0[i][j].eq(g1[i][j])             # mesma variável em todo o t
            else:
                assert not g0[i][j].eq(g1[i][j])         # uma variável por instante

def test_grelha_z3_nomes():
    g = grelha_z3(N, 4)
    assert str(g[3][5]) == "n_3_5_4"
    assert str(g[0][5]) == "Cons_0_5"
    assert str(g[5][0]) == "Cons_5_0"

def test_c_vizinhos_devolve_as_8_celulas_da_vizinhanca():
    g = grelha_z3(N, 0)
    for (i, j) in [(1, 1), (1, N), (N, 1), (N, N), (9, 9)]:
        viz = c_vizinhos(g, i, j)
        assert len(viz) == 8
        esperadas = {str(g[i + a][j + b]) for a in (-1, 0, 1) for b in (-1, 0, 1)
                     if (a, b) != (0, 0)}
        assert {str(v) for v in viz} <= esperadas
        assert str(g[i][j]) not in {str(v) for v in viz}

def test_regra_z3_tabela_completa_B3_S23():
    desloc = [(a, b) for a in (0, 1, 2) for b in (0, 1, 2) if (a, b) != (1, 1)]
    for mascara in range(256):
        for propria in (False, True):
            g = [[z3.BoolVal(False)] * 3 for _ in range(3)]
            g[1][1] = z3.BoolVal(propria)
            n = 0
            for k, (a, b) in enumerate(desloc):
                if mascara >> k & 1:
                    g[a][b] = z3.BoolVal(True)
                    n += 1
            esperado = (n == 3) or (propria and n == 2)
            obtido = z3.simplify(regra_z3(g, 1, 1))
            assert z3.is_true(obtido) == esperado, (mascara, propria)
            assert z3.is_true(obtido) or z3.is_false(obtido)

def test_proximo_z3_usa_a_celula_e_a_lista_de_vizinhos():
    mortas = [z3.BoolVal(False)] * 8
    tres = [z3.BoolVal(True)] * 3 + [z3.BoolVal(False)] * 5
    dois = [z3.BoolVal(True)] * 2 + [z3.BoolVal(False)] * 6
    assert z3.is_true(z3.simplify(proximo_z3(z3.BoolVal(False), tres)))
    assert z3.is_true(z3.simplify(proximo_z3(z3.BoolVal(True), tres)))
    assert z3.is_true(z3.simplify(proximo_z3(z3.BoolVal(True), dois)))
    assert z3.is_false(z3.simplify(proximo_z3(z3.BoolVal(False), dois)))
    assert z3.is_false(z3.simplify(proximo_z3(z3.BoolVal(True), mortas)))

def test_I_z3_aceita_o_estado_inicial_do_motor_com_qualquer_borda():
    g = m_sync.estado_inicial(0)
    for valor in (True, False):
        s = z3.Solver()
        s.add(I_z3(N), *lits_normais(g, 0))
        s.add(literal(grelha_z3(N, 0)[0][3], valor))     # uma célula inicial livre
        assert s.check() == z3.sat

def test_I_z3_rejeita_qualquer_normal_alterada():
    g = m_sync.estado_inicial(0)
    for (i, j) in [(1, 1), (3, 3), (4, 4), (N, N), (9, 9)]:
        h = [linha[:] for linha in g]
        h[i][j] ^= 1
        s = z3.Solver()
        s.add(I_z3(N), *lits_normais(h, 0))
        assert s.check() == z3.unsat, (i, j)

def test_I_z3_nao_aceita_outro_padrao_inicial():
    g = grelha_de(m_sync, [(5, 5)])
    s = z3.Solver()
    s.add(I_z3(N), *lits_normais(g, 0))
    assert s.check() == z3.unsat

def test_erro_z3_so_com_todas_as_normais_mortas():
    gz = grelha_z3(N, 2)
    s = z3.Solver()
    s.add(erro_z3(N, 2), *lits_normais(grelha_de(m_sync, []), 2))
    assert s.check() == z3.sat
    for celula in [(1, 1), (9, 9), (N, N)]:
        s = z3.Solver()
        s.add(erro_z3(N, 2), *lits_normais(grelha_de(m_sync, [celula]), 2))
        assert s.check() == z3.unsat

def test_erro_z3_ignora_a_borda():
    s = z3.Solver()
    s.add(erro_z3(N, 0), grelha_z3(N, 0)[0][5], grelha_z3(N, 0)[3][0])
    assert s.check() == z3.sat

def test_T_main_modo_invalido_levanta_erro():
    with pytest.raises(ValueError):
        T_main(N, 0, "OUTRO")


def test_T_sync_aceita_o_sucessor_do_motor():
    for g in estados_z3():
        assert aceita("SYNC", g, m_sync.sucessores(g)[0])

def test_T_sync_rejeita_qualquer_normal_alterada():
    random.seed(1)
    for g in estados_z3()[:6]:
        h = m_sync.sucessores(g)[0]
        for (i, j) in random.sample(NORMAIS, 12):
            x = copia(h)
            x[i][j] ^= 1
            assert not aceita("SYNC", g, x), (i, j)

def test_T_sync_rejeita_alterar_borda_ou_finais():
    g = m_sync.estado_inicial(0)
    h = m_sync.sucessores(g)[0]
    x = copia(h); x[0][3] ^= 1                    # inicial muda entre instantes
    assert not aceita("SYNC", g, x)
    x = copia(h); x[N + 1][4] = 1                 # final fica viva
    assert not aceita("SYNC", g, x)

def test_T_sync_exige_movimento_quando_o_motor_o_exige():
    g = grelha_de(m_sync, BLINKER)
    assert not aceita("SYNC", g, g)               # blinker não é ponto fixo
    b = grelha_de(m_sync, BLOCK)
    assert aceita("SYNC", b, b)                   # bloco é ponto fixo

def test_T_async_aceita_os_sucessores_que_mudam_e_uma_amostra_dos_iguais():
    random.seed(2)
    for g in estados_z3()[:6]:
        s = m_async.sucessores(g)
        mudam = [h for h in s if h != g]
        iguais = [h for h in s if h == g]
        for h in mudam + random.sample(iguais, min(5, len(iguais))):
            assert aceita("ASYNC", g, h)

def test_T_async_aceita_auto_ciclo():
    g = grelha_de(m_async, BLINKER)
    assert aceita("ASYNC", g, g)                  # escolher uma célula que não muda

def test_T_async_rejeita_duas_celulas_alteradas():
    g = grelha_de(m_async, BLINKER)
    h = next(h for h in m_async.sucessores(g) if h != g)
    i, j = dif(g, h)[0]
    for (a, b) in [(10, 10), (2, 15), (4, 5)]:
        if (a, b) != (i, j):
            x = copia(h)
            x[a][b] ^= 1
            assert not aceita("ASYNC", g, x), (a, b)

def test_T_async_rejeita_varias_celulas_que_seguem_a_regra():
    g = grelha_de(m_async, BLINKER)
    sync = m_sync.sucessores(g)[0]
    assert aceita("SYNC", g, sync)
    assert not aceita("ASYNC", g, sync)          # 4 mudanças de uma só vez
    x = copia(g)
    x[3][5] = 1
    x[5][5] = 1                                  # dois nascimentos, ambos legítimos
    assert not aceita("ASYNC", g, x)

def test_T_async_rejeita_uma_celula_com_o_valor_contrario_ao_da_regra():
    g = grelha_de(m_async, BLINKER)
    sync = m_sync.sucessores(g)[0]
    for (i, j) in [(10, 10), (4, 5), (3, 5), (4, 4)]:
        x = copia(g)
        x[i][j] = 1 - sync[i][j]                  # contrário do que a regra dá
        if x != g:
            assert not aceita("ASYNC", g, x), (i, j)

def test_T_async_rejeita_alterar_borda():
    g = m_async.estado_inicial(0)
    x = copia(g); x[0][2] ^= 1
    assert not aceita("ASYNC", g, x)


def test_extrair_devolve_k_mais_1_grelhas_0_1_do_tamanho_certo():
    tr = traco_z3("SYNC", 3)
    assert len(tr) == 4
    assert all(len(g) == N + 2 and all(len(l) == N + 2 for l in g) for g in tr)
    assert all(v in (0, 1) for g in tr for l in g for v in l)

def test_extrair_respeita_estado_inicial_finais_e_constantes():
    for modo in ("SYNC", "ASYNC"):
        tr = traco_z3(modo, 3)
        assert conj_vivas(tr[0]) == BLOCO_INICIAL
        for g in tr:
            for i in range(N + 2):
                for j in range(N + 2):
                    t = m_sync.tipo(i, j)
                    if t == "final":
                        assert g[i][j] == 0
                    if t == "inicial":
                        assert g[i][j] == tr[0][i][j]

def test_valida_traco_aceita_tracos_do_solver_nos_dois_modos():
    assert validatraco_z3(m_sync, traco_z3("SYNC", 4))
    assert validatraco_z3(m_async, traco_z3("ASYNC", 4))

def test_valida_traco_rejeita_traco_adulterado():
    tr = traco_z3("SYNC", 3)
    mau = [copia(g) for g in tr]
    mau[2][9][9] ^= 1                                 # transição inválida
    with pytest.raises(AssertionError):
        validatraco_z3(m_sync, mau)
    mau = [copia(g) for g in tr]
    mau[0][1][1] ^= 1                                 # estado inicial inválido
    with pytest.raises(AssertionError):
        validatraco_z3(m_sync, mau)

def test_valida_traco_async_rejeita_duas_mudancas_num_passo():
    tr = traco_z3("ASYNC", 3)
    mau = [copia(g) for g in tr]
    mau[1] = copia(tr[0])
    mau[1][1][1] ^= 1
    mau[1][2][2] ^= 1                                 # duas células mudam
    with pytest.raises(AssertionError):
        validatraco_z3(m_async, mau)
