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

        def estado_erro(self,grid):
            return self.c_vivas(grid) == 0
                
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
    # processar o motor vizualizar o jogo 
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
    nao cumpre as regras do enenciado, apenas usado para mostrar que a engine simula corretamente o game of life utilizando estruturas de celulas conhecidas 
    glider = [(2, 3), (3, 4), (4, 2), (4, 3), (4, 4)]
    blinker=[(4, 4), (4, 5), (4, 6)]

    g_final, vivas = simulacao(engine, 30,0,glider) 
    g_final, vivas = simulacao(engine, 30,0,blinker) 
    """
    print(vivas)
    return


@app.cell
def _():
    import z3

    def grelha_z3(N,t):

        g_z3 = [[0] * (N + 2) for _ in range(N + 2)]

        for i in range(len(g_z3)):
            for j in range(len(g_z3)):
                if max(i,j) == N+1:
                    g_z3[i][j] = z3.BoolVal(False)
                elif min(i, j) == 0:         
                    g_z3[i][j] = z3.Bool(f"Cons_{i}_{j}") 
                else:
                    g_z3[i][j] = z3.Bool(f"n_{i}_{j}_{t}")
    
        return g_z3


    def c_vizinhos (g,i,j):
        vizinhos = []
    
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (dx, dy) != (0, 0):
                    vizinhos.append(g[i + dx][j + dy])
              

        return vizinhos

    def c_contagem(vizinhos):
        return z3.Sum([z3.If(v, 1, 0) for v in vizinhos])

    def proximo_z3(x, vizinhos):
        """Regra B3/S23 com restrições pseudo-booleanas."""
        exatamente_3 = z3.PbEq([(v, 1) for v in vizinhos], 3)
        exatamente_2 = z3.PbEq([(v, 1) for v in vizinhos], 2)
        return z3.Or(exatamente_3, z3.And(x, exatamente_2))

    def regra_z3(g, i, j):
        return proximo_z3(g[i][j], c_vizinhos(g, i, j))


    def T_sync(N, t):
        g  = grelha_z3(N, t)       
        gp = grelha_z3(N, t + 1)  
        restricoes = []

        for i in range(1,N+1):              
            for j in range(1,N+1):
       
                prox= regra_z3 (g,i,j)
                restricoes.append(gp[i][j] == prox )

        return z3.And(restricoes)


    def sel_z3(N, t):
        return {(i, j): z3.Bool(f"sel_{t}_{i}_{j}")
                for i in range(1, N + 1) for j in range(1, N + 1)}

    def T_async(N, t):
        g = grelha_z3(N, t)
        gp = grelha_z3(N, t + 1)
        restricoes = []

        # Um único inteiro identifica a célula selecionada (0 .. N*N-1).
        # Evita criar N*N variáveis booleanas sel e uma restrição one-hot.
        sel = z3.Int(f"selidx_{t}")
        restricoes.extend([sel >= 0, sel < N * N])

        for i in range(1, N + 1):
            for j in range(1, N + 1):
                indice = (i - 1) * N + (j - 1)
                escolhida = (sel == indice)
                prox = regra_z3(g, i, j)

                # A selecionada atualiza; todas as outras mantêm o valor.
                restricoes.append(
                    gp[i][j] == z3.If(escolhida, prox, g[i][j])
                )

        return z3.And(restricoes)

    def T_main(N, t, MODO):
        if MODO == "SYNC":
            return T_sync(N, t)
        elif MODO == "ASYNC":
            return T_async(N, t)
        else:
            raise ValueError("Modo inválido")
    def I_z3(N):
        """Estado inicial: bloco 3x3 vivo, resto das normais morto; iniciais livres (aleatórias)."""
        g = grelha_z3(N, 0)
        return z3.And([g[i][j] == z3.BoolVal(i <= 3 and j <= 3)
                       for i in range(1, N + 1) for j in range(1, N + 1)])
 
    def erro_z3(N, t):
        g = grelha_z3(N, t)
        return z3.Not(z3.Or([g[i][j] for i in range(1, N + 1) for j in range(1, N + 1)]))
              

    return I_z3, T_main, erro_z3, grelha_z3, z3


@app.cell
def _(grelha_z3, z3):
    # funcoes de apoio as propriedades 
    def extrair(m, N, k):
        tr = []
        for t in range(k + 1):
            g = grelha_z3(N, t)
            tr.append([[int(z3.is_true(m.eval(g[i][j], model_completion=True)))
                        for j in range(N + 2)] for i in range(N + 2)])
        return tr
 
    def valida_traco(engine, tr):
        """Re-executa o contra-exemplo no motor concreto."""
        N = engine.N
        assert tr[0] == engine.estado_inicial(borda={(i, j): tr[0][i][j]
                  for i in range(N + 2) for j in range(N + 2) if engine.tipo(i, j) == "inicial"})
        for t in range(len(tr) - 1):
            assert tr[t + 1] in engine.sucessores(tr[t]), f"passo {t} inválido"
        return True

    return extrair, valida_traco


@app.cell
def _(GameOfLife_Engine, I_z3, T_main, erro_z3, extrair,
      grelha_z3, valida_traco, z3):
    # ------------------------------------------------------------
    # PROPRIEDADE 1: invariante + bounded model checking (BMC)
    # ------------------------------------------------------------

    def inv_p1(g, N):
        """Candidato: existe pelo menos uma célula normal viva."""
        return z3.Or([
            g[i][j]
            for i in range(1, N + 1)
            for j in range(1, N + 1)
        ])

    def verifica_invariante_p1(N, MODO):
        """Verifica base e preservação do candidato Inv.

        Base:       I(s) AND NOT Inv(s) é UNSAT.
        Preservação: Inv(s) AND T(s,s') AND NOT Inv(s') é UNSAT.

        O passo é testado sobre todos os estados que satisfazem Inv,
        não apenas sobre estados já alcançáveis.
        """
        g0 = grelha_z3(N, 0)
        g1 = grelha_z3(N, 1)

        # 1. Base: todos os estados iniciais satisfazem Inv?
        solver_base = z3.Solver()
        solver_base.add(I_z3(N))
        solver_base.add(z3.Not(inv_p1(g0, N)))
        resultado_base = solver_base.check()

        # 2. Passo: qualquer sucessor de um estado Inv também satisfaz Inv?
        solver_passo = z3.Solver()
        solver_passo.add(inv_p1(g0, N))
        solver_passo.add(T_main(N, 0, MODO))
        solver_passo.add(z3.Not(inv_p1(g1, N)))
        resultado_passo = solver_passo.check()

        return {
            "base": resultado_base,
            "passo": resultado_passo,
            "base_ok": resultado_base == z3.unsat,
            "passo_ok": resultado_passo == z3.unsat,
            "invariante_valido": (
                resultado_base == z3.unsat
                and resultado_passo == z3.unsat
            ),
        }

    def bmc_erro_p1(N, MODO, kmax):
        """Procura um estado de erro em 0..kmax transições.

        Devolve:
          ("SAT", k, traco)         se encontrou contraexemplo;
          ("UNSAT_LIMIT", None, None) se não encontrou até kmax;
          ("UNKNOWN", k, motivo)    se o Z3 não conseguiu decidir.
        """
        solver = z3.Solver()
        solver.add(I_z3(N))

        for k in range(kmax + 1):
            solver.push()
            solver.add(erro_z3(N, k))
            resultado = solver.check()

            if resultado == z3.sat:
                modelo = solver.model()
                traco = extrair(modelo, N, k)
                solver.pop()
                return "SAT", k, traco

            if resultado == z3.unknown:
                motivo = solver.reason_unknown()
                solver.pop()
                return "UNKNOWN", k, motivo

            solver.pop()

            if k < kmax:
                solver.add(T_main(N, k, MODO))

        return "UNSAT_LIMIT", None, None

    def p1_main(N, kmax=9):
        """Executa a P1 nos dois modos: invariante e procura de contraexemplo."""
        resultados = {}

        for modo in ("SYNC", "ASYNC"):
            print("\n" + "=" * 58)
            print(f"PROPRIEDADE 1 — MODO {modo}")
            print("=" * 58)

            # Vertente A: teste do candidato a invariante.
            inv = verifica_invariante_p1(N, modo)
            print("\n[1] Verificação do candidato Inv = existe uma célula viva")
            print("Base:", inv["base"])
            print("Passo indutivo:", inv["passo"])

            if inv["base_ok"]:
                print("  Base válida: todos os estados iniciais satisfazem Inv.")
            else:
                print("  Base inválida: existe um estado inicial que viola Inv.")

            if inv["passo_ok"]:
                print("  Preservação válida: todos os sucessores preservam Inv.")
            elif inv["passo"] == z3.sat:
                print("  Preservação falhou: existe uma transição Inv -> NOT Inv.")
                print("  Nota: esse estado pode não ser alcançável desde I.")
            else:
                print("  Preservação inconclusiva: o Z3 devolveu UNKNOWN.")

            print(
                "  Candidato indutivo:",
                "SIM" if inv["invariante_valido"] else "NÃO"
            )

            # Vertente B: BMC a partir dos estados iniciais do enunciado.
            print(f"\n[2] BMC: procura de estado de erro até ao passo {kmax}")
            status, k, detalhe = bmc_erro_p1(N, modo, kmax)

            traco = None
            if status == "SAT":
                traco = detalhe
                motor = GameOfLife_Engine(N, modo)
                valido = valida_traco(motor, traco)
                contagens = [motor.c_vivas(g) for g in traco]

                print("  CONTRAEXEMPLO ENCONTRADO.")
                print("  Primeiro passo de erro encontrado:", k)
                print("  Células normais vivas por instante:", contagens)
                print("  Traço validado no motor concreto:", valido)
                print("  Conclusão: a propriedade 1 é FALSA neste modo.")

            elif status == "UNSAT_LIMIT":
                print(f"  Nenhum erro encontrado até {kmax} transições.")
                print("  Conclusão: INCONCLUSIVO (BMC limitado não é uma prova global).")

            else:
                print("  O Z3 devolveu UNKNOWN no passo:", k)
                print("  Motivo:", detalhe)
                print("  Conclusão: INCONCLUSIVO.")

            resultados[modo] = {
                "invariante": inv,
                "bmc_status": status,
                "passo_erro": k,
                "traco": traco,
            }

        return resultados

    return inv_p1, verifica_invariante_p1, bmc_erro_p1, p1_main


@app.cell
def _(I_z3, T_main, extrair, grelha_z3, random, z3):
    # ------------------------------------------------------------
    # PROPRIEDADE 2: testemunhos de células vivas e mortas
    # ------------------------------------------------------------

    def testemunhas(N, MODO, kmax, verbose=False, timeout_ms=None):
        """Procura testemunhos vivos/mortos usando consultas agregadas.

        Otimizações:
          1. Regista diretamente os 289 valores já conhecidos no estado inicial.
          2. Pesquisa apenas o valor oposto ao inicial de cada célula.
          3. Usa uma única disjunção para procurar testemunhos vivos E mortos.
          4. Um modelo pode fornecer testemunhos para muitas células ao mesmo tempo.
          5. Mantém o mesmo solver incremental entre instantes.

        Devolve:
          viva[(i,j)]  = primeiro instante encontrado em que a célula está viva;
          morta[(i,j)] = primeiro instante encontrado em que a célula está morta.

        Células em falta após kmax ficam inconclusivas; não são provadas impossíveis.
        """
        import time

        if MODO not in ("SYNC", "ASYNC"):
            raise ValueError("MODO tem de ser 'SYNC' ou 'ASYNC'")
        if kmax < 0:
            raise ValueError("kmax tem de ser >= 0")

        inicio = time.perf_counter()
        cels = [
            (i, j)
            for i in range(1, N + 1)
            for j in range(1, N + 1)
        ]

        # O estado inicial das células normais é fixo pelo enunciado:
        # bloco 3x3 vivo; todas as restantes mortas.
        vivas_iniciais = {
            (i, j) for i in range(1, 4) for j in range(1, 4)
        }
        mortas_iniciais = set(cels) - vivas_iniciais

        viva = {cel: 0 for cel in vivas_iniciais}
        morta = {cel: 0 for cel in mortas_iniciais}

        pendentes_vivas = set(mortas_iniciais)   # precisam de ficar vivas
        pendentes_mortas = set(vivas_iniciais)  # precisam de ficar mortas

        solver = z3.Solver()
        if timeout_ms is not None:
            solver.set(timeout=int(timeout_ms))
        solver.add(I_z3(N))

        houve_unknown = False
        consultas = 0
        modelos = 0

        if verbose:
            print(
                f"Inicial: {len(viva)} testemunhos vivos e "
                f"{len(morta)} testemunhos mortos já conhecidos."
            )

        # k=0 já foi tratado diretamente. Cada iteração acrescenta uma
        # transição e procura testemunhos no estado seguinte.
        for k in range(1, kmax + 1):
            solver.add(T_main(N, k - 1, MODO))
            g = grelha_z3(N, k)

            while pendentes_vivas or pendentes_mortas:
                termos = (
                    [g[i][j] for (i, j) in pendentes_vivas]
                    + [z3.Not(g[i][j]) for (i, j) in pendentes_mortas]
                )
                if not termos:
                    break

                solver.push()
                solver.add(z3.Or(termos))
                resultado = solver.check()
                consultas += 1

                if resultado == z3.unsat:
                    solver.pop()
                    # Neste instante não existe outro testemunho. Avançar k.
                    break

                if resultado == z3.unknown:
                    motivo = solver.reason_unknown()
                    solver.pop()
                    houve_unknown = True
                    if verbose:
                        print(f"  Z3 UNKNOWN no passo {k}: {motivo}")
                    # Não inferir impossibilidade; tentar o instante seguinte.
                    break

                modelo = solver.model()
                modelos += 1
                novas_vivas = []
                novas_mortas = []

                for i, j in tuple(pendentes_vivas):
                    if z3.is_true(modelo.eval(g[i][j], model_completion=True)):
                        novas_vivas.append((i, j))

                for i, j in tuple(pendentes_mortas):
                    if z3.is_false(modelo.eval(g[i][j], model_completion=True)):
                        novas_mortas.append((i, j))

                solver.pop()

                # O modelo representa um percurso válido; todas estas
                # observações são testemunhos válidos no mesmo percurso.
                for cel in novas_vivas:
                    viva[cel] = k
                    pendentes_vivas.remove(cel)
                for cel in novas_mortas:
                    morta[cel] = k
                    pendentes_mortas.remove(cel)

                if not novas_vivas and not novas_mortas:
                    # Defesa contra eventual inconsistência do modelo/consulta.
                    houve_unknown = True
                    if verbose:
                        print("  Aviso: o modelo não acrescentou testemunhos.")
                    break

            if verbose:
                print(
                    f"k={k}: vivas {len(viva)}/{len(cels)} | "
                    f"mortas {len(morta)}/{len(cels)} | "
                    f"por encontrar: {len(pendentes_vivas) + len(pendentes_mortas)}",
                    flush=True,
                )

            if not pendentes_vivas and not pendentes_mortas:
                break

        duracao = time.perf_counter() - inicio
        if verbose:
            print(
                f"Tempo: {duracao:.2f}s | consultas Z3: {consultas} | "
                f"modelos: {modelos}"
            )
            if houve_unknown:
                print("Aviso: houve UNKNOWN; resultados em falta são inconclusivos.")

        # Metadados para medição, sem alterar a interface de retorno existente.
        testemunhas.ultima_execucao = {
            "modo": MODO,
            "kmax": kmax,
            "tempo_segundos": duracao,
            "consultas": consultas,
            "modelos": modelos,
            "unknown": houve_unknown,
            "pendentes_vivas": sorted(pendentes_vivas),
            "pendentes_mortas": sorted(pendentes_mortas),
        }
        return viva, morta

    def alcanca_viva(N, MODO, cel, kmax):
        """Procura um percurso em que a célula cel está viva até kmax."""
        i, j = cel
        solver = z3.Solver()
        solver.add(I_z3(N))

        for k in range(kmax + 1):
            resultado = solver.check(grelha_z3(N, k)[i][j])
            if resultado == z3.sat:
                return k, extrair(solver.model(), N, k)
            if resultado == z3.unknown:
                return "UNKNOWN", k, solver.reason_unknown()
            if k < kmax:
                solver.add(T_main(N, k, MODO))

        return None

    def cobertura_sim(motor, amostras=500, passos=60, seed=0):
        """Cobertura experimental de células vistas vivas por simulação.

        É auxiliar; não substitui a pesquisa simbólica testemunhas().
        """
        random.seed(seed)
        N = motor.N
        vistas = set()

        for _ in range(amostras):
            g = motor.estado_inicial()
            for _ in range(passos):
                for i in range(1, N + 1):
                    for j in range(1, N + 1):
                        if g[i][j]:
                            vistas.add((i, j))
                g = motor.passo(g)

        return vistas

    def p2_main(N, kmax=20, timeout_ms=None):
        """Executa a procura otimizada de testemunhos da P2 nos dois modos."""
        todos = [
            (i, j)
            for i in range(1, N + 1)
            for j in range(1, N + 1)
        ]
        resultados = {}

        for modo in ("SYNC", "ASYNC"):
            print("\n" + "=" * 58)
            print(f"PROPRIEDADE 2 — MODO {modo}")
            print("=" * 58)

            viva, morta = testemunhas(
                N, modo, kmax=kmax, verbose=True, timeout_ms=timeout_ms
            )
            sem_viva = [c for c in todos if c not in viva]
            sem_morta = [c for c in todos if c not in morta]

            print("\nResumo:")
            print(f"  Com testemunho vivo:  {len(viva)}/{N*N}")
            print(f"  Com testemunho morto: {len(morta)}/{N*N}")
            print("  Sem testemunho vivo:", sem_viva)
            print("  Sem testemunho morto:", sem_morta)

            completa = not sem_viva and not sem_morta
            if completa:
                print("  Conclusão: P2 VERIFICADA na interpretação existencial.")
            else:
                print(
                    f"  Conclusão: INCONCLUSIVA para as células em falta "
                    f"(pesquisa até {kmax} transições)."
                )

            resultados[modo] = {
                "desempenho": dict(getattr(testemunhas, "ultima_execucao", {})),
                "viva": viva,
                "morta": morta,
                "sem_viva": sem_viva,
                "sem_morta": sem_morta,
                "verificada": completa,
            }

        return resultados

    return testemunhas, alcanca_viva, cobertura_sim, p2_main


@app.cell
def _(N, p1_main, p2_main):
    # ------------------------------------------------------------
    # EXECUÇÃO FINAL DOS TESTES
    # ------------------------------------------------------------
    # A P1 tem contraexemplos conhecidos até ao passo 9 nos dois modos.
    KMAX_P1 = 9

    # Começar com 20 passos para a P2. Se sobrarem células sem testemunho,
    # aumentar este valor (por exemplo, para 30, 40 ou 60) e voltar a executar.
    KMAX_P2 = 20
    TIMEOUT_P2_MS = 60000  # limite por consulta Z3; None desativa o limite

    print("\n########## TESTES DA PROPRIEDADE 1 ##########")
    resultados_p1 = p1_main(N, kmax=KMAX_P1)

    print("\n########## TESTES DA PROPRIEDADE 2 ##########")
    resultados_p2 = p2_main(
        N, kmax=KMAX_P2, timeout_ms=TIMEOUT_P2_MS
    )

    return resultados_p1, resultados_p2


if __name__ == "__main__":
    app.run()
