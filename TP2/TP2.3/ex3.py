import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    from pysmt.shortcuts import Symbol, BV, And, Equals, get_model, Int, GE, Or, GT, BVSGT, BVSLE, BVSLT, BVSGE, Not, BVSRem, BVLShl, BVLShr, BVSub, BVAdd, Solver, BVURem, BVUGE, BVULT, BVMul, NotEquals, Ite, Bool, BVUGT
    from pysmt.typing import BVType, INT

    return (
        And,
        BV,
        BVAdd,
        BVLShl,
        BVLShr,
        BVMul,
        BVSGE,
        BVSLT,
        BVSRem,
        BVSub,
        BVType,
        BVULT,
        BVURem,
        Equals,
        GE,
        GT,
        INT,
        Int,
        Not,
        NotEquals,
        Or,
        Solver,
        Symbol,
        mo,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Variáveis globais
    """)
    return


@app.cell(hide_code=True)
def _():
    N = 8
    SIGNAL = False
    pcA = {0:4, 1:3, 2:2, 3:1, 4:0, 4:0, 5:-1}
    return N, SIGNAL, pcA


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercício 3
    Considere o problema descrito no documento [+Lógica Computacional: Multiplicação de Inteiros](https://www.dropbox.com/scl/fi/zozzuriwaw7db9abpewyh/Logica-Computacional-Multiplicacao-de-Inteiros.paper?rlkey=j92tgvb8emq3ybb0aiv8jz33q&dl=0) . Nesse documento usa-se um “Control Flow Automaton” como  modelo do programa imperativo que calcula a multiplicação de  inteiros positivos representados por vetores de bits.

    ![image](public/p.png)



    *    a.  Construir um SFOTS, usando BitVec’s de tamanho $n$ , que descreva o comportamento deste autómato; para isso identifique e codifique em `Z3` , as variáveis do modelo, o estado inicial , a relação de transição e o estado de erro.
    *    b. Usando $k$-indução verifique nesse SFOTS se a propriedade $x \times y + z = a \times b$ é um invariante do seu comportamento.
    *    c. Usando $k$-indução no SFOTS acima e adicionando ao estado inicial  a condição  $a < 2^{n/2} \land b < 2^{n/2}$, verifique a segurança do programa; nomeadamente  prove que, com tal estado inicial, o estado de erro nunca é acessível.
    *    d. Codifique a propriedade de animação que exprime que o programa termina quaisquer que sejam os valores iniciais de $a$ e $b$ e prove que ela se verifica no SFOTS  que construiu.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Estados
    ```python
    assert a >= 0 and b >= 0
    x , y, z = a , b , 0
    0: while not y == 0:
    1:   if even(y):
    2:       x , y , z = x << 1 , y >> 1 , z
         else:
    3:       x , y , z = x , y - 1, z + x
    4: stop
    5: erro
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Parte a
    ## Construção do SFOTS
    Começamos pela declaração dos estados e a inicialização do primeiro estado, de acordo com as regras indicadas no início do programa.
    """)
    return


@app.cell
def _(And, BV, BVSGE, BVType, Equals, INT, Int, N, SIGNAL, Symbol):
    def declare(i):
        state = {}
        state['pc'] = Symbol('pc'+str(i),INT)
        state['x'] = Symbol('x'+str(i),BVType(N))
        state['y'] = Symbol('y'+str(i),BVType(N))
        state['z'] = Symbol('z'+str(i),BVType(N))
        state['a'] = Symbol('a'+str(i),BVType(N))
        state['b'] = Symbol('b'+str(i),BVType(N))
        return state

    def init(state, i=None):
        constraints = [
            Equals(state['pc'], Int(0)),
            Equals(state['x'], state['a']),
            Equals(state['y'], state['b']),
            Equals(state['z'], BV(0, N))
        ]

        if SIGNAL:
            constraints.append(BVSGE(state['a'], BV(0,N)))
            constraints.append(BVSGE(state['b'], BV(0,N)))

        if i is not None:
            constraints.append(Equals(state['a'], i['a']))
            constraints.append(Equals(state['b'], i['b']))

        return And(constraints)

    return declare, init


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Transições
    """)
    return


@app.cell
def _(
    And,
    BV,
    BVAdd,
    BVLShl,
    BVLShr,
    BVSLT,
    BVSRem,
    BVSub,
    BVULT,
    BVURem,
    Equals,
    Int,
    N,
    Not,
    Or,
    SIGNAL,
):
    def equal(curr, prox, list_symbol):
        return [Equals(prox[c], curr[c]) for c in list_symbol]

    def error(state):
        return Equals(state['pc'], Int(5))

    def stop(state):
        return Equals(state['pc'], Int(4))

    def trans(curr,prox):
        return Or(
            # casos de erro
            And(
                Equals(curr['pc'], Int(2)),
                BVSLT(BVLShl(curr['x'], 1), BV(0,N)) if SIGNAL else BVULT(BVLShl(curr['x'], 1), curr['x']),
                error(prox),
                *equal(curr, prox, ['x', 'y', 'z', 'a', 'b'])

            ),
            And(
                Equals(curr['pc'], Int(3)),
                BVSLT(BVAdd(curr['z'], curr['x']), BV(0,N)) if SIGNAL else BVULT(BVAdd(curr['z'], curr['x']), curr['z']),
                error(prox),
                *equal(curr, prox, ['x', 'y', 'z', 'a', 'b'])
            ),
            # loop
            And(
                Equals(curr['pc'], Int(0)),
                Not(Equals(curr['y'], BV(0, N))),
                Equals(prox['pc'], Int(1)),
                *equal(curr, prox, ['x', 'y', 'z', 'a', 'b'])
            ),
            # caso em que y é par
            And(
                Equals(curr['pc'], Int(1)),
                Equals(BVSRem(curr['y'], BV(2, N)), BV(0, N)) if SIGNAL else Equals(BVURem(curr['y'], BV(2, N)), BV(0, N)),
                Equals(prox['pc'], Int(2)),
                *equal(curr, prox, ['x', 'y', 'z', 'a', 'b'])
            ),
            And(
                Equals(curr['pc'], Int(2)),
                Equals(prox['pc'], Int(0)),
                Not(BVSLT(BVLShl(curr['x'], 1), BV(0,N))) if SIGNAL else Not(BVULT(BVLShl(curr['x'], 1), curr['x'])),
                Equals(prox['x'], BVLShl(curr['x'], 1)),
                Equals(prox['y'], BVLShr(curr['y'], 1)),
                *equal(curr, prox, ['z', 'a', 'b'])
            ),
            # caso em que y é ímpar
            And(
                Equals(curr['pc'], Int(1)),
                Equals(BVSRem(curr['y'], BV(2, N)), BV(1, N)) if SIGNAL else Equals(BVURem(curr['y'], BV(2, N)), BV(1, N)),
                Equals(prox['pc'], Int(3)),
                *equal(curr, prox, ['x', 'y', 'z', 'a', 'b'])
            ),
            And(
                Equals(curr['pc'], Int(3)),
                Equals(prox['pc'], Int(0)),
                Not(BVSLT(BVAdd(curr['z'], curr['x']), BV(0,N))) if SIGNAL else Not(BVULT(BVAdd(curr['z'], curr['x']), curr['z'])),
                Equals(prox['y'], BVSub(curr['y'], BV(1, N))),
                Equals(prox['z'], BVAdd(curr['z'], curr['x'])),
                *equal(curr, prox, ['x', 'a', 'b'])
            ),
            # caso de terminação
            And(
                Equals(curr['pc'], Int(0)),
                Equals(curr['y'], BV(0, N)),
                Equals(prox['pc'], Int(4)),
                *equal(curr, prox, ['x', 'y', 'z', 'a', 'b'])
            ),
            And(
                Equals(curr['pc'], Int(4)),
                Equals(prox['pc'], Int(4)),
                *equal(curr, prox, ['x', 'y', 'z', 'a', 'b'])
            ),
            And(
                error(curr),
                error(prox),
                *equal(curr, prox, ['x', 'y', 'z', 'a', 'b'])
            )
        )

    return (trans,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Gera traço
    """)
    return


@app.cell
def _(Equals, Int, Or, Solver, pcA):
    def gera_traco(declare,init,trans,initial, kmax=300):

        with Solver(name="z3") as s:

            # states = [declare(i) for i in range(k)]
            states = [declare(0)]
            s.add_assertion(init(states[0], initial))

            for c in range(kmax):
                s.push()
                s.add_assertion(Or(Equals(states[-1]['pc'], Int(4)), Equals(states[-1]['pc'], Int(5))))


                if s.solve():
                    model = s.get_model()
                    w = len(str(model.get_value(states[-1]['x']).constant_value()))
                    a_val = model.get_value(states[0]['a']).constant_value()
                    b_val = model.get_value(states[0]['b']).constant_value()
                    for i, st in enumerate(states):
                        pc_val = model.get_value(st['pc']).constant_value()
                        x_val = model.get_value(st['x']).constant_value()
                        y_val = model.get_value(st['y']).constant_value()
                        z_val = model.get_value(st['z']).constant_value()
                        inv = 2 * a_val * b_val - x_val + y_val + pcA[pc_val] - z_val
                        print(f"Estado {i:>3} : pc = {pc_val:>1}, x = {x_val:>{w}}, y = {y_val:>{w}}, z = {z_val:>{w}}, inv = {inv:>{w}}")
                    s.pop()
                    return

                s.pop()
                states.append(declare(c+1))
                s.add_assertion(trans(states[c], states[c+1]))

            print("Não foi encontrado um traço válido")

    return (gera_traco,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Teste
    """)
    return


@app.cell
def _(BV, Int, N, declare, gera_traco, init, trans):
    i = {'pc': Int(0), 'a' : BV(0, N), 'b' : BV(8, N)}
    gera_traco(declare,init,trans,i)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Parte b
    ## Indução $x \times y + z = a \times b$
    """)
    return


@app.cell
def _(And, BVAdd, BVMul, Equals, Not, Or, Solver, pcA):
    def k_inducao(declare,init,trans,inv,K):
        for k in range(1, K):
            with Solver(name="z3") as solver:
                states = [declare(i) for i in range(k)]
                base = [init(states[0])]
                for i in range(k-1):
                    base.append(trans(states[i], states[i+1]))

                caso_base = And(And(base), Or([Not(inv(s)) for s in states]))
                solver.add_assertion(caso_base)
    
                if solver.solve():
                    print(f"Falha caso base com k = {k}")
                    model = solver.get_model()
                    w = len(str(model.get_value(states[-1]['x']).constant_value()))
                    a_val = model.get_value(states[0]['a']).constant_value()
                    b_val = model.get_value(states[0]['b']).constant_value()
                    for i, st in enumerate(states):
                        pc_val = model.get_value(st['pc']).constant_value()
                        x_val = model.get_value(st['x']).constant_value()
                        y_val = model.get_value(st['y']).constant_value()
                        z_val = model.get_value(st['z']).constant_value()
                        inv = 2 * a_val * b_val - x_val + y_val + pcA[pc_val] - z_val
                        print(f"Estado {i:>3} : pc = {pc_val:>1}, x = {x_val:>{w}}, y = {y_val:>{w}}, z = {z_val:>{w}}, inv = {inv:>{w}}")
                    return False
                solver.reset_assertions()
                states = [declare(i) for i in range(k+1)]
                inductive = []
                for i in range(k):
                    inductive.append(inv(states[i]))
                    inductive.append(trans(states[i], states[i+1]))

                inductive.append(Not(inv(states[k])))
                step_case = And(inductive)

                solver.add_assertion(step_case)
    
                if solver.solve():
                    print(f"Falha caso indutivo k = {k}")

                else:
                    print(f"Invariante válido para k = {k}")
                    return True

        return False



    def inv(state):
        return Equals(BVAdd(BVMul(state['x'], state['y']), state['z']), BVMul(state['a'], state['b']))

    return inv, k_inducao


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Teste
    """)
    return


@app.cell
def _(declare, init, inv, k_inducao, trans):
    k_inducao(declare,init,trans,inv,10)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Parte c
    $k$-indução com a condição $a < 2^{n/2} \land b < 2^{n/2}$ da propriedade NotEquals(state['pc'], Int(5))

    ## Teste para mostrar a inseguraça do programa antes da restrição.
    """)
    return


@app.cell
def _(Int, NotEquals, declare, init, k_inducao, trans):
    def noterror(state):
        return NotEquals(state['pc'], Int(5))

    k_inducao(declare,init,trans,noterror,10)
    return (noterror,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Função init com a condição $a < 2^{n/2} \land b < 2^{n/2}$
    """)
    return


@app.cell
def _(And, BV, BVSGE, BVSLT, BVULT, Equals, Int, N, SIGNAL):
    def init2(state, i=None):
        constraints = [
            Equals(state['pc'], Int(0)),
            Equals(state['x'], state['a']),
            Equals(state['y'], state['b']),
            Equals(state['z'], BV(0, N))
        ]

        if SIGNAL:
            constraints.append(BVSGE(state['a'], BV(0,N)))
            constraints.append(BVSGE(state['b'], BV(0,N)))
            constraints.append(BVSLT(state['a'], BV(2**(N/2),N)))
            constraints.append(BVSLT(state['b'], BV(2**(N/2),N)))

        else:
            constraints.append(BVULT(state['a'], BV(2**int(N/2),N)))
            constraints.append(BVULT(state['b'], BV(2**int(N/2),N)))

        if i is not None:
            constraints.append(Equals(state['a'], i['a']))
            constraints.append(Equals(state['b'], i['b']))

        return And(constraints)

    return (init2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Teste com a condição
    """)
    return


@app.cell
def _(declare, init2, k_inducao, noterror, trans):
    # k_inducao2(noterror, 100)

    k_inducao(declare,init2,trans,noterror, 100)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Parte d
    ## Propriedade de animação
    """)
    return


@app.cell
def _(And, Not, Solver):
    def animacao(declare, init, trans, P_estrela, K=10):
        for k in range(1, K + 1):
            s = [declare(i) for i in range(k + 2)]

            with Solver(name="z3") as solver:
                solver.add_assertion(init(s[0]))
                for i in range(k):
                    solver.add_assertion(trans(s[i], s[i + 1]))
                solver.add_assertion(Not(And([P_estrela(s[i], s[i + 1]) for i in range(k)])))
                if solver.solve():
                    print("Falha no caso base")
                    return False

                solver.reset_assertions()
            
                for i in range(k):
                    solver.add_assertion(P_estrela(s[i], s[i + 1]))
                for i in range(k + 1):
                    solver.add_assertion(trans(s[i], s[i + 1]))
                solver.add_assertion(Not(P_estrela(s[k], s[k + 1])))
                if not solver.solve():
                    print(f"Provado com k={k}")
                    return True
                else:
                    print(f"Falha caso indutivo com k = {k}")


        print(f"Inconclusivo até {K}")
        return None    

    return (animacao,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Teste
    """)
    return


@app.cell
def _(And, BVULT, Equals, GE, GT, Int, Or, animacao, declare, init, trans):
    def P_estrela(curr, prox):
        y_desce   = BVULT(prox['y'], curr['y'])
        y_igual   = Equals(prox['y'], curr['y'])
        pc_avanca = GT(prox['pc'], curr['pc'])
        parado    = And(Equals(prox['pc'], curr['pc']), GE(curr['pc'], Int(4)))
        return Or(y_desce, And(y_igual, pc_avanca), And(y_igual, parado))

    animacao(declare, init, trans, P_estrela)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Uso de LLM
    Neste trabalho, usamos o Claude como apoio neste trabalho. Em
    concreto:
    * Explicação de funções relacinais para BitVecs, com e sem sinal;
    * Debug de código: BV(1,N) trocado com Int(1), índices e chaves erradas em listas e dicionários, k-indução(parte b), função gera_traco, etc;
    * Explicação do push e pop do solver e modificação função gera_traco com push e pop.

    Link para o chat: https://claude.ai/share/ffbc0723-fcc8-422f-8036-22b39d82a36d
    """)
    return


if __name__ == "__main__":
    app.run()
