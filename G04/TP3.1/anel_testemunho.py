# /// script
# dependencies = [
#     "marimo",
#     "pysmt==0.10.0",
#     "z3-solver",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    from pysmt.shortcuts import Symbol, And, Equals, get_model, Int, GE, Or, GT, Not, Solver, NotEquals, Ite, Bool
    from pysmt.typing import INT, BOOL


@app.cell
def _(c):
    class Anel:
        def __init__(self, N):
            self.N = N
            self.states = []

        def declare(self, i):
            state = {}
            state['pc'] = Symbol('pc'+str(i), INT)
            state['ws'] = [Symbol('w_'+str(i)+'_'+str(c), BOOL) for c in range(self.N)]
            state['cs'] = [Symbol('c_'+str(i)+'_'+str(c), BOOL) for c in range(self.N)]
            state['ts'] = [Symbol('t_'+str(i)+'_'+str(c), BOOL) for c in range(self.N)]
            return state

        def init(self):
            contraints = []
            And(Not(self.states[0]['ws'][0]),Not(self.states[0]['cs'][0]))
            contraints.append(self.states[0]['ts'][c])
        
            for c in range(1, self.N):
                contraints.append(And(Not(self.states[0]['ws'][c]),Not(self.states[0]['cs'][c])))
                contraints.append(Not(self.states[0]['ts'][c]))
            return And(contraints)

        def declarar_n_estados(self, n):
            for c in range(n):
                self.states.append(declare(n))
            init(self.states[0])

    return


if __name__ == "__main__":
    app.run()
