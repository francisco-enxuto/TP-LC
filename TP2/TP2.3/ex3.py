import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    from pysmt.shortcuts import Symbol, BV, And, Equals, get_model, Int, GE, Or, GT, BVSGT, BVSLE, BVSLT, BVSGE, Not, BVSRem, BVLShl, BVLShr, BVSub, BVAdd, Solver, BVURem, BVUGE, BVULT
    from pysmt.typing import BVType, INT

    return (
        And,
        BV,
        BVAdd,
        BVLShl,
        BVLShr,
        BVSLT,
        BVSRem,
        BVSub,
        BVType,
        BVULT,
        BVURem,
        Equals,
        GE,
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
    # declaração de variáveis
    N = 16
    return (N,)


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
def _(And, BV, BVType, Equals, INT, Int, N, Symbol):
    def declare(i):
        state = {}
        state['pc'] = Symbol('pc'+str(i),INT)
        state['x'] = Symbol('x'+str(i),BVType(N))
        state['y'] = Symbol('y'+str(i),BVType(N))
        state['z'] = Symbol('z'+str(i),BVType(N))
        state['a'] = Symbol('a'+str(i),BVType(N))
        state['b'] = Symbol('b'+str(i),BVType(N))
        return state

    def init(state, i):
        return And(
            Equals(state['pc'], Int(0)),
            Equals(state['x'], i['a']),
            Equals(state['y'], i['b']),
            Equals(state['z'], BV(0, N)),
            Equals(state['a'], i['a']),
            Equals(state['b'], i['b'])
        )

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
):
    def equal(curr, prox, list_symbol):
        return [Equals(prox[c], curr[c]) for c in list_symbol]

    def error(state):
        return Equals(state['pc'], Int(5))

    def trans(curr,prox, signal):
        return Or(
            # casos de erro
            And(
                Equals(curr['pc'], Int(2)),
                BVSLT(BVLShl(curr['x'], 1), BV(0,N)) if signal else BVULT(BVLShl(curr['x'], 1), curr['x']),
                error(prox),
                *equal(curr, prox, ['x', 'y', 'z', 'a', 'b'])
    
            ),
            And(
                Equals(curr['pc'], Int(3)),
                BVSLT(BVAdd(curr['z'], curr['x']), BV(0,N)) if signal else BVULT(BVAdd(curr['z'], curr['x']), curr['z']),
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
                Equals(BVSRem(curr['y'], BV(2, N)), BV(0, N)) if signal else Equals(BVURem(curr['y'], BV(2, N)), BV(0, N)),
                Equals(prox['pc'], Int(2)),
                *equal(curr, prox, ['x', 'y', 'z', 'a', 'b'])
            ),
            And(
                Equals(curr['pc'], Int(2)),
                Equals(prox['pc'], Int(0)),
                Not(BVSLT(BVLShl(curr['x'], 1), BV(0,N))) if signal else Not(BVULT(BVLShl(curr['x'], 1), curr['x'])),
                Equals(prox['x'], BVLShl(curr['x'], 1)),
                Equals(prox['y'], BVLShr(curr['y'], 1)),
                *equal(curr, prox, ['z', 'a', 'b'])
            ),
            # caso em que y é ímpar
            And(
                Equals(curr['pc'], Int(1)),
                Equals(BVSRem(curr['y'], BV(2, N)), BV(1, N)) if signal else Equals(BVURem(curr['y'], BV(2, N)), BV(1, N)),
                Equals(prox['pc'], Int(3)),
                *equal(curr, prox, ['x', 'y', 'z', 'a', 'b'])
            ),
            And(
                Equals(curr['pc'], Int(3)),
                Equals(prox['pc'], Int(0)),
                Not(BVSLT(BVAdd(curr['z'], curr['x']), BV(0,N))) if signal else Not(BVULT(BVAdd(curr['z'], curr['x']), curr['z'])),
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
    def gera_traco(initial, signal=False, kmax=300):

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
                s.add_assertion(trans(states[c], states[c+1], signal))

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
    i = {'pc': Int(0), 'a' : BV(5, N), 'b' : BV(50, N)}
    gera_traco(i)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Parte b
    ## Indução $x \times y + z = a \times b$
    """)
    return


@app.cell
def _(And, GE, Int, Not, Solver, declare, init, trans, w):
    def bmc_always(declare,init,trans,inv,K):
        for k in range(1,K+1):
            with Solver(name="z3") as s:
            
                states = [declare(i) for i in range(k)]

                constraints = []

                s.add_assertion(init(states[0]))
            
                for i in range(k-1):
                    constraints.add_assertion(trans(states[i], states[i+1]))

                constraints.add_assertion(Not(inv(states[-1])))

                s.add_assertion(And(constraints))

                if s.solve():
                    model = s.get_model()
                    for i, st in enumerate(states):
                        pc_val = model.get_value(st['pc']).constant_value()
                        x_val = model.get_value(st['x']).constant_value()
                        y_val = model.get_value(st['y']).constant_value()
                        z_val = model.get_value(st['z']).constant_value()
                        a_val = model.get_value(st['a']).constant_value()
                        b_val = model.get_value(st['b']).constant_value()
                        print(f"Estado {i:>3} : pc = {pc_val:>1}, "
                              f"x = {x_val:>{w}}, "
                              f"y = {y_val:>{w}}, "
                              f"z = {z_val:>{w}}, "
                              f"x * y + z = {x_val * y_val + z_val}, "
                              f"a * b = {a_val * b_val}"
                        )
                    return False 
        print("Nenhum contra-exemplo encontrado")
        return


    def nonnegative(state):
        return GE(state['x'], Int(0))

    bmc_always(declare,init,trans,nonnegative,20)
    return


if __name__ == "__main__":
    app.run()
