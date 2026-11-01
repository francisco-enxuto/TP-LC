import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    from pysmt.shortcuts import Symbol, BV, And, Equals, get_model, Int, GE, Or, GT, BVSGT, BVSLE, BVSLT, BVSGE, Not, BVSRem, BVLShl, BVLShr, BVSub, BVAdd, Solver, BVURem, BVUGE, BVULT, BVMul
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
        INT,
        Int,
        Not,
        Or,
        Solver,
        Symbol,
        mo,
    )


@app.cell(hide_code=True)
def _():
    N = 8
    SIGNAL = False
    return N, SIGNAL


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Problema proposto
    Considere o problema descrito no documento +Lógica Computacional: Multiplicação de Inteiros . Nesse documento usa-se um “Control Flow Automaton” como  modelo do programa imperativo que calcula a multiplicação de  inteiros positivos representados por vetores de bits.


        a. Construir um SFOTS, usando BitVec’s de tamanho $$n$$ , que descreva o comportamento deste autómato; para isso identifique e codifique em `Z3` , as variáveis do modelo, o estado inicial , a relação de transição e o estado de erro.
        b. Usando $$k$$-indução verifique nesse SFOTS se $$\;$$a propriedade $$\;(x*y + z = a*b)\;$$ $$\;$$é um invariante do seu comportamento.
        c. Usando $$k$$-indução no SFOTS acima e adicionando ao estado inicial  a condição  $$\,$$ $$\,(a < 2^{n/2})\land(b < 2^{n/2})\,$$, verifique a segurança do programa; nomeadamente  prove que, com tal estado inicial, o estado de erro nunca é acessível.
        d. Codifique a propriedade de animação que exprime que o programa termina quaisquer que sejam os valores iniciais de $$\,a\,$$ e $$\,b\,$$ e prove que ela se verifica no SFOTS  que construiu.
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
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Declaração de estados
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
def _(Equals, Int, Or, Solver, declare, init, trans):
    def gera_traco(initial, kmax=300):

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
                    for i, st in enumerate(states):
                        pc_val = model.get_value(st['pc']).constant_value()
                        x_val = model.get_value(st['x']).constant_value()
                        y_val = model.get_value(st['y']).constant_value()
                        z_val = model.get_value(st['z']).constant_value()
                        print(f"Estado {i:>3} : pc = {pc_val:>1}, x = {x_val:>{w}}, y = {y_val:>{w}}, z = {z_val:>{w}}")
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
def _(BV, Int, N, gera_traco):
    i = {'pc': Int(0), 'a' : BV(2, N), 'b' : BV(1, N)}
    gera_traco(i)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Parte b
    ## Indução $x \times y + z = a \times b$

    ## 0-Indução

    > Para todo o estado $$\,x\,$$
    >        (a) $$\quad \neg\,P(x)\quad$$  é  inconsistente

    $$1$$-Indução

    > Para todo par de estados $$\,x,y\,$$ deve-se verificar
    >        (a) $$\quad\mathsf{init}(x)\,\land\,\neg P(x)\quad$$  é  inconsistente
    >        (b) $$\quad\mathsf{trans}(x,y) \,\land\, P(x)\,\land\,\neg\,P(y)\quad$$ é inconsistente
    """)
    return


@app.cell
def _(BVAdd, BVMul, Equals, Not, Or, Solver, declare, init, trans):
    def k_inducao(inv, K, initial=None):
        w = 6
        for k in range(1, K + 1):
        
            with Solver(name="z3") as s:
                states = [declare(i) for i in range(k)]
                s.add_assertion(init(states[0], initial))
            
                for i in range(k - 1):
                    s.add_assertion(trans(states[i], states[i + 1]))
                
                s.add_assertion(Or([Not(inv(st)) for st in states]))
            
                if s.solve():
                    print(f"Falso. Contra-exemplo no caso base, k = {k}")
                    return False
                
            with Solver(name="z3") as s:
            
                states = [declare(i) for i in range(k + 1)]
            
                for i in range(k):
                    s.add_assertion(trans(states[i], states[i + 1]))
                    s.add_assertion(inv(states[i]))
            
                s.add_assertion(Not(inv(states[-1])))
            
                if not s.solve():
                    print(f"Provado com k = {k}")
                    return True

        print(f"Nenhum k até {K} prova a propriedade")
        return None


    def inv(state):
        return Equals(BVAdd(BVMul(state['x'], state['y']), state['z']), BVMul(state['a'], state['b']))

    k_inducao(inv,6)
    return


if __name__ == "__main__":
    app.run()
