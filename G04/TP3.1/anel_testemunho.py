# /// script
# dependencies = [
#     "marimo",
#     "pysmt==0.10.0",
#     "z3-solver",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")

with app.setup:
    import marimo as mo
    from z3 import Bool, And, Not, Solver, Or, sat


@app.function
# ==================== funções auxiliares da função transição ====================

def inativo(state, i):
    return And(Not(state[f'w{i}']), Not(state[f'c{i}']))


@app.class_definition
class Anel:
    def __init__(self, N=10, regenera=False):
        self.N = N
        self.vars = [f'{v}{i}' for v in 'wct' for i in range(N)]
        self.regenera = regenera

# ==================== declare ====================
    def declare(self, i):
        return {v : Bool(f'{v}_{i}') for v in self.vars}

# ==================== init ====================
    def init(self, state):
        constraints = []

        for i in range(self.N):
            constraints.append(And(Not(state[f'w{i}']), Not(state[f'c{i}'])))
            if(i != 0):
                constraints.append(Not(state[f'w{i}']))
        constraints.append(state['t0'])

        return And(constraints)

# ==================== transições ====================
    def igual(self, curr, prox, *ignorar):
        return And([prox[v] == curr[v] for v in self.vars if v not in ignorar])

    def trans(self, curr, prox):
        mov = []
        for i in range(self.N):
            next = (i+1) % self.N

            # pedir-
            mov.append(
                And(
                    inativo(curr,i),
                    prox[f'w{i}'],
                    self.igual(curr, prox, f'w{i}')
                )
            )

            # entrar
            mov.append(
                And(
                    curr[f'w{i}'],
                    curr[f't{i}'],
                    Not(prox[f'w{i}']),
                    prox[f'c{i}'],
                    self.igual(curr, prox, f'w{i}', f'c{i}')
                )
            )

            # sair
            mov.append(
                And(
                    curr[f'c{i}'],
                    Not(prox[f'c{i}']),
                    Not(prox[f't{i}']),
                    prox[f't{next}'],
                    self.igual(curr, prox, f'c{i}', f't{i}', f't{next}')     
                )
            )

            # passar
            mov.append(
                And(
                    inativo(curr,i),
                    curr[f't{i}'],
                    Not(prox[f't{i}']),
                    prox[f't{next}'],
                    self.igual(curr, prox, f't{i}', f't{next}')
                )
            )

            # regenera
            if self.regenera:
                mov.append(
                    And(
                        And(curr[f'w{i}'], Not(curr[f't{i}'])),
                        prox[f't{i}'],
                        self.igual(curr, prox, f't{i}')
                    )
                )

        return(Or(mov))

    def prop(self, state):
        mov = []
        for i in range(self.N - 1):
            for j in range(i + 1, self.N):
                mov.append(
                    And(
                        state[f'c{i}'],
                        state[f'c{j}']
                    )
                )
        return Or(mov)


@app.function
def k_inducao(declare,init,trans,inv,K):
    solver = Solver()
    for k in range(1, K):
        states = [declare(i) for i in range(k)]
        base = [init(states[0])]
        for i in range(k-1):
            base.append(trans(states[i], states[i+1]))

        caso_base = And(And(base), Or([Not(inv(s)) for s in states]))
        solver.add(caso_base)

        if solver.check() == sat:
            print(f"Falha caso base com k = {k}")
            model = solver.model()
            print(model)
            return False
        solver.reset()
        states = [declare(i) for i in range(k+1)]
        inductive = []
        for i in range(k):
            inductive.append(inv(states[i]))
            inductive.append(trans(states[i], states[i+1]))

        inductive.append(Not(inv(states[k])))
        step_case = And(inductive)

        solver.add(step_case)

        if solver.check() == sat:
            print(f"Falha caso indutivo k = {k}")

        else:
            print(f"Invariante válido para k = {k}")
            return True

    return False


@app.cell
def _():
    a = Anel(2, regenera=False)

    k_inducao(a.declare,a.init,a.trans,lambda s: Not(a.prop(s)), 20)
    return


if __name__ == "__main__":
    app.run()
