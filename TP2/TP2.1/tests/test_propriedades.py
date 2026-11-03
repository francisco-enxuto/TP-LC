import z3

from GameofLife_F import (
    alcanca_viva, bmc_erro_p1,grelha_z3, inv_p1,
    p2_contra_exemplo, p2_testemunhas_sim, validatraco_z3,
    verifica_invariante_p1,
)
from Auxiliares import (
    BLOCO_INICIAL, N, NORMAIS,
    avanca, conj_vivas, grelha_de, lits_normais, m_async, m_sync,
)


def test_inv_p1_e_exatamente_existe_normal_viva():
    gz = grelha_z3(N, 0)
    s = z3.Solver()
    s.add(inv_p1(gz, N), *lits_normais(grelha_de(m_sync, []), 0))
    assert s.check() == z3.unsat                      # todas mortas viola Inv
    for c in [(1, 1), (9, 9), (N, N)]:
        s = z3.Solver()
        s.add(inv_p1(gz, N), *lits_normais(grelha_de(m_sync, [c]), 0))
        assert s.check() == z3.sat

def test_invariante_candidato_tem_base_valida_mas_nao_e_indutivo_nos_dois_modos():
    for modo in ("SYNC", "ASYNC"):
        r = verifica_invariante_p1(N, modo)
        assert r["base"] == z3.unsat and r["base_ok"]
        assert r["passo"] == z3.sat and not r["passo_ok"]
        assert not r["invariante_valido"]

def test_bmc_sync_encontra_erro_ao_passo_3_com_traco_valido():
    estado, k, traco = bmc_erro_p1(N, "SYNC", 9)
    assert (estado, k) == ("SAT", 3)
    assert [m_sync.c_vivas(g) for g in traco] == [9, 3, 1, 0]
    assert validatraco_z3(m_sync, traco)
    assert m_sync.estado_erro(traco[-1])
    assert not any(m_sync.estado_erro(g) for g in traco[:-1])

def test_bmc_sync_com_limite_insuficiente_nao_encontra():
    assert bmc_erro_p1(N, "SYNC", 2) == ("UNSAT_LIMIT", None, None)
    assert bmc_erro_p1(N, "SYNC", 0) == ("UNSAT_LIMIT", None, None)

def test_bmc_async_precisa_de_9_passos_para_matar_as_9_celulas():
    estado, k, traco = bmc_erro_p1(N, "ASYNC", 9)
    assert (estado, k) == ("SAT", 9)
    assert [m_async.c_vivas(g) for g in traco] == [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    assert validatraco_z3(m_async, traco)

def test_bmc_async_com_8_passos_nao_chega():
    assert bmc_erro_p1(N, "ASYNC", 8) == ("UNSAT_LIMIT", None, None)


def test_p2_contra_exemplo_sync_erro_absorvente_ao_passo_3():
    k, traco = p2_contra_exemplo(N, "SYNC")
    assert k == 3 and validatraco_z3(m_sync, traco)
    assert m_sync.estado_erro(traco[-1])
    assert m_sync.sucessores(traco[-1])[0] == traco[-1]      # sumidouro

def test_p2_contra_exemplo_async_erro_absorvente_ao_passo_9():
    k, traco = p2_contra_exemplo(N, "ASYNC")
    assert k == 9 and validatraco_z3(m_async, traco)
    assert m_async.estado_erro(traco[-1])
    assert all(h == traco[-1] for h in m_async.sucessores(traco[-1]))

def test_p2_contra_exemplo_com_limite_curto_devolve_none():
    assert p2_contra_exemplo(N, "SYNC", kmax=2) is None
    assert p2_contra_exemplo(N, "ASYNC", kmax=8) is None

def test_p2_testemunhas_sim_estrutura_e_estado_inicial():
    bordas = (1, 0, None, None)
    viva, morta, iniciais = p2_testemunhas_sim(N, "SYNC", bordas=bordas, passos=5)
    assert len(iniciais) == len(bordas)
    assert set(viva) | set(morta) == set(NORMAIS)
    assert all(conj_vivas(g) == BLOCO_INICIAL for g in iniciais)
    for c in NORMAIS:
        for dic in (viva, morta):
            if c in dic:
                b, t = dic[c]
                assert 0 <= b < len(bordas) and t >= 0
    assert all(viva[c] == (0, 0) for c in BLOCO_INICIAL)     # vivas já no instante 0
    assert all(morta[c] == (0, 0) for c in NORMAIS if c not in BLOCO_INICIAL)

def test_p2_testemunhas_sim_e_deterministica_com_a_mesma_semente():
    a = p2_testemunhas_sim(N, "SYNC", bordas=(None, None), passos=10, seed=4)
    b = p2_testemunhas_sim(N, "SYNC", bordas=(None, None), passos=10, seed=4)
    assert a == b

def test_p2_testemunhos_sync_sao_reproduziveis_no_motor():
    viva, morta, iniciais = p2_testemunhas_sim(
        N, "SYNC", bordas=(1, 0, None, None, None), passos=30, seed=1)
    for dic, valor in ((viva, 1), (morta, 0)):
        for (i, j), (b, t) in dic.items():
            g = avanca(m_sync, iniciais[b], t)
            assert g[i][j] == valor, ((i, j), b, t)

def test_p2_testemunhos_async_sao_reproduziveis_no_motor():
    viva, morta, iniciais = p2_testemunhas_sim(
        N, "ASYNC", bordas=(1, 0, None), passos=2, seed=1)
    for dic, valor in ((viva, 1), (morta, 0)):
        for (i, j), (b, t) in dic.items():
            g = [linha[:] for linha in iniciais[b]]
            for k in range(t):                       # varrimento linha a linha
                a, c = NORMAIS[k % len(NORMAIS)]
                g[a][c] = m_async.proximo_valor(g, a, c)
            assert g[i][j] == valor, ((i, j), b, t)

def test_alcanca_viva_encontra_celula_viva_e_o_traco_e_valido():
    r = alcanca_viva(N, "SYNC", (2, 4), 3)
    assert r is not None and r[0] != "UNKNOWN"
    k, traco = r
    assert traco[k][2][4] == 1 and validatraco_z3(m_sync, traco)
    assert all(traco[t][2][4] == 0 for t in range(k))        # é o primeiro instante

def test_alcanca_viva_devolve_none_quando_a_celula_e_inalcancavel_no_limite():
    assert alcanca_viva(N, "SYNC", (N, N), 5) is None

def test_alcanca_viva_com_viva_false_procura_celula_morta():
    k, traco = alcanca_viva(N, "SYNC", (2, 2), 3, viva=False)
    assert k == 1 and traco[1][2][2] == 0 and validatraco_z3(m_sync, traco)

def test_alcanca_viva_async_uma_celula_so_muda_uma_por_passo():
    assert alcanca_viva(N, "ASYNC", (4, 4), 1) is None       # 1 passo não chega
    k, traco = alcanca_viva(N, "ASYNC", (2, 2), 1, viva=False)
    assert k == 1 and validatraco_z3(m_async, traco)
