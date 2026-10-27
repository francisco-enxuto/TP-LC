import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from pysmt.shortcuts import Symbol, BV, And, Equals, get_model, Int, GE, Or, GT, BVSGT, BVSLE, BVSLT, BVSGE, Not, BVSRem, BVLShl, BVLShr, BVSub, BVAdd, Solver
    from pysmt.typing import BVType, INT

    return (
        And,
        BV,
        BVAdd,
        BVLShl,
        BVLShr,
        BVSGE,
        BVSRem,
        BVSub,
        BVType,
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
    # declaração de variáveis
    N = 32
    return (N,)


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
    3:   else:
    4:       x , y , z = x , y - 1, z + x
    5: stop
    ```
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
        return state

    def init(state, i):
        return And(
            Equals(state['pc'], Int(0)),
            Equals(state['x'], i['x']),
            Equals(state['y'], i['y']),
            Equals(state['z'], BV(0, N))
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
    BVSGE,
    BVSRem,
    BVSub,
    Equals,
    Int,
    N,
    Not,
    Or,
):
    def trans(curr,prox):
        # completar
        return Or(
            # casos de erro
            And(
                Equals(curr['pc'], Int(2)),
                BVSGE(curr['x'], BVLShl(curr['x'], 1)),
                Equals(prox['pc'], Int(5)),
                Equals(prox['x'], curr['x']),
                Equals(prox['y'], curr['y']),
                Equals(prox['z'], curr['z'])
            ),
            And(
                Equals(curr['pc'], Int(3)),
                BVSGE(curr['z'], BVAdd(curr['z'], curr['x'])),
                Equals(prox['pc'], Int(5)),
                Equals(prox['x'], curr['x']),
                Equals(prox['y'], curr['y']),
                Equals(prox['z'], curr['z'])
            ),
            # loop
            And(
                Equals(curr['pc'], Int(0)),
                Not(Equals(curr['y'], BV(0, N))),
                Equals(prox['pc'], Int(1)),
                Equals(prox['x'], curr['x']),
                Equals(prox['y'], curr['y']),
                Equals(prox['z'], curr['z'])
            ),
            # caso em que y é par
            And(
                Equals(curr['pc'], Int(1)),
                Equals(BVSRem(curr['y'], BV(2, N)), BV(0, N)),
                Equals(prox['pc'], Int(2)),
                Equals(prox['x'], curr['x']),
                Equals(prox['y'], curr['y']),
                Equals(prox['z'], curr['z'])
            ),
            And(
                Equals(curr['pc'], Int(2)),
                Equals(prox['pc'], Int(0)),
                Equals(prox['x'], BVLShl(curr['x'], 1)),
                Equals(prox['y'], BVLShr(curr['y'], 1)),
                Equals(prox['z'], curr['z'])
            ),
            # caso em que y é ímpar
            And(
                Equals(curr['pc'], Int(1)),
                Equals(BVSRem(curr['y'], BV(2, N)), BV(1, N)),
                Equals(prox['pc'], Int(3)),
                Equals(prox['x'], curr['x']),
                Equals(prox['y'], curr['y']),
                Equals(prox['z'], curr['z'])
            ),
            And(
                Equals(curr['pc'], Int(3)),
                Equals(prox['pc'], Int(0)),
                Equals(prox['x'], curr['x']),
                Equals(prox['y'], BVSub(curr['y'], BV(1, N))),
                Equals(prox['z'], BVAdd(curr['z'], curr['x']))
            ),
            # caso de terminação
            And(
                Equals(curr['pc'], Int(0)),
                Equals(curr['y'], BV(0, N)),
                Equals(prox['pc'], Int(4)),
                Equals(prox['x'], curr['x']),
                Equals(prox['y'], curr['y']),
                Equals(prox['z'], curr['z'])
            ),
            And(
                Equals(curr['pc'], Int(4)),
                Equals(prox['pc'], Int(4)),
                Equals(prox['x'], curr['x']),
                Equals(prox['y'], curr['y']),
                Equals(prox['z'], curr['z'])
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
def _(Equals, Int, Or, Solver):
    def gera_traco(declare, init, trans, initial, kmax=300):

        with Solver(name="z3") as s:

            # states = [declare(i) for i in range(k)]
            states = [declare(0)]
            s.add_assertion(init(states[0], initial))

            for c in range(kmax):
                s.push()
                s.add_assertion(Or(Equals(states[-1]['pc'], Int(4)), Equals(states[-1]['pc'], Int(5))))
        

                if s.solve():
                    model = s.get_model()
                    for i, st in enumerate(states):
                        pc_val = model.get_value(st['pc'])
                        x_val = model.get_value(st['x']).constant_value()
                        y_val = model.get_value(st['y']).constant_value()
                        z_val = model.get_value(st['z']).constant_value()
                        print(f"Estado {i} : pc = {pc_val}, x = {x_val}, y = {y_val}, z = {z_val}")
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
    i = {'pc': Int(0), 'x' : BV(33, N), 'y' : BV(10, N)}
    gera_traco(declare, init, trans, i)
    return


if __name__ == "__main__":
    app.run()
