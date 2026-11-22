# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.24.2",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Trabalho Prático 3 — Exercício 2: Raiz quadrada inteira

    ## Contexto

    O programa seguinte calcula a raiz quadrada inteira $\lfloor\sqrt{n}\rfloor$
    usando apenas somas. Baseia-se no facto de os quadrados perfeitos
    $1, 4, 9, 16, \dots$ se obterem somando os ímpares consecutivos
    $1, 3, 5, 7, \dots$

    ```python
    INPUT  n
    assume 0 <= n < B
    r, s, t = 0, 1, 1
    while s <= n:
        r, t = r + 1, t + 2
        s = s + t
    OUTPUT r
    assert r^2 <= n < (r+1)^2
    ```

    As variáveis são inteiros **sem sinal de $w$ bits** ($w$ par), ou seja,
    representam valores em $[0, 2^w-1]$. Considera-se **estado de erro** o
    "overflow" na soma $s+t$, isto é, quando o resultado dessa soma excede
    $2^w-1$.

    O programa tem duas propriedades a verificar:

    - **correção parcial:** se termina sem erro, o valor de `r` satisfaz a
      pós-condição;
    - **segurança:** o erro de "overflow" nunca ocorre.

    A segurança depende do limite $B$ imposto aos "inputs". Com $B$
    demasiado grande, `s` acaba por ultrapassar a capacidade das variáveis
    antes de o ciclo terminar.

    Este exercício aplica as técnicas da 2ª e 3ª partes do **Capítulo 4**:
    CFAs, transformadores de predicados e **CHCs** (*Constrained Horn
    Clauses*) resolvidas com o **Spacer** do Z3.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Pretende-se

    1. Identificar o CFA que representa o programa: os locais, as guardas, o
       transformador de predicados "weakest pre-condition" de cada local e
       os locais `error` e `stop`.
    2. Escrever os dois sistemas de CHCs, o orientado às pré-condições e o
       orientado às pós-condições. Tentar resolvê-los com o Spacer em
       `BitVec`, para $w$ pequeno, e em `Int`; documentar os limites
       encontrados.
    3. Determinar o maior $B$, em função de $w$, para o qual o local `error`
       é inacessível. Provar que o programa é seguro para esse $B$ e
       inseguro para $B+1$.
    4. Provar que o programa termina sempre, usando uma função de "ranking"
       codificada em CHCs ou a metodologia dos "look-aheads".
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Requisitos obrigatórios

    O teu notebook tem de expor os elementos seguintes, com o comportamento
    indicado. Os nomes são sugestões que facilitam a correção; podes usar
    outros, desde que documentes a correspondência.

    ### O CFA (R1, alínea 1)

    Uma estrutura de dados, por exemplo um dicionário ou uma classe `CFA`,
    que descreve:

    - os locais, incluindo o local inicial `system` e os locais terminais
      `stop` e `error`;
    - os ramos $\ell \to \ell'$, cada um com a sua guarda
      $\mathsf{sw}_{\ell,\ell'}$;
    - a relação de transição $\mathsf{T}_\ell(\mathsf{X},\mathsf{X}')$ de
      cada local.

    Inclui também uma função `wp(l, Q)` que devolve o predicado
    $\mathsf{wp}_\ell(Q)$ para cada local $\ell$. O notebook deve
    apresentar o CFA também em forma de diagrama ou de tabela.

    A estrutura deve ser parametrizada por $w$ e $B$ e pelo tipo das
    variáveis (`BitVec` ou `Int`). A mesma descrição tem de servir as
    alíneas 2, 3 e 4.

    ### Os dois sistemas de CHCs (R2, alínea 2)

    Duas funções, `chcs_pre(cfa)` e `chcs_pos(cfa)`. Cada uma gera, a partir
    do CFA, o sistema de CHCs correspondente:

    - **orientado às pré-condições:** uma variável de predicado $P_\ell$ por
      local;
    - **orientado às pós-condições:** uma variável de predicado $Q_\ell$ por
      local.

    Ambos os sistemas incluem a pós-condição do programa (no local `stop`)
    e a inacessibilidade de `error`. Uma função `spacer(chcs, timeout)`
    resolve o sistema e devolve:

    - `sat`, com o modelo, isto é, uma asserção por local;
    - `unsat`, quando possível com o contra-exemplo;
    - `unknown`.

    ### Limite de segurança (R3, alínea 3)

    - Uma função `B_max(w)`, com a fórmula que deduzires e a respetiva
      justificação.
    - Para cada $w$ testado, duas provas:
        - a **segurança** com $B = $ `B_max(w)`: o sistema de CHCs tem
          modelo, ou outra técnica do Capítulo 4, justificada;
        - a **insegurança** com $B+1$: o sistema não tem modelo e há um
          traço concreto até `error`.

    ### Terminação (R4, alínea 4)

    Uma função de "ranking" $\rho(\mathsf{X})$ e a sua verificação. Tem de
    ficar provado que, em todo o estado acessível do local do ciclo em que
    a guarda do ciclo é verdadeira, se verifica:

    - $\rho(\mathsf{X}) \ge 0$;
    - $\rho(\mathsf{X}') < \rho(\mathsf{X})$ depois de uma iteração.

    A verificação pode usar CHCs, reaproveitando o invariante obtido nas
    alíneas anteriores, ou a metodologia dos "look-aheads". Em qualquer dos
    casos, explica por que razão a condição provada garante a terminação.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Notas técnicas

    - **"Overflow" em `BitVec`.** Com vetores de $w$ bits, a soma "dá a
      volta" silenciosamente e o erro deixa de ser observável. Há duas
      alternativas: usar vetores com alguns bits a mais do que $w$, ou usar
      os predicados `BVAddNoOverflow` do Z3. Justifica a escolha e garante
      que nenhuma outra operação (incluindo `r^2` na pós-condição) dá a
      volta antes de o teste de "overflow" a detetar.
    - **"Overflow" em `Int`.** Com inteiros matemáticos, o erro é a condição
      explícita $s + t > 2^w - 1$. A pós-condição é não-linear, por isso o
      Spacer pode responder `unknown`. Documenta o que acontece e a partir
      de que valores de $w$.
    - **Ordem das atribuições.** No corpo do ciclo, `s = s + t` usa o valor
      de `t` **já atualizado** na linha anterior. O CFA e as CHCs têm de
      respeitar esta ordem.

    ## Como testar/validar

    O notebook tem de verificar automaticamente:

    - por execução direta do programa em Python, para todos os
      $0 \le n < 2^w$ com $w$ pequeno (por exemplo $w \le 12$):
        - que, quando não há "overflow", o resultado coincide com
          `math.isqrt(n)`;
        - que o menor $n$ que provoca "overflow" é consistente com
          `B_max(w)`;
    - que o modelo devolvido pelo Spacer (quando `sat`) satisfaz cada CHC
      do sistema. Cada cláusula, depois de substituídas as incógnitas pelo
      modelo, deve ser uma fórmula válida;
    - que o traço de erro com $B+1$ é um traço do CFA: respeita as guardas
      e as transições e termina em `error`.

    ## O que é deixado ao teu critério

    Desde que justificadas no notebook, ficam ao teu critério:

    - os nomes e o número de locais do CFA (por exemplo, se o corpo do ciclo
      é um único local ou dois);
    - a codificação do "overflow" em `BitVec`;
    - os valores de $w$ e os limites de tempo usados nos testes;
    - a técnica usada na prova de terminação.

    ## Extensões opcionais (bónus)

    - **Escala.** Estende a prova de segurança a $w = 32$ ou $w = 64$ e
      discute o que limita cada abordagem.
    - **Variante com sinal.** Repete a análise com inteiros com sinal em
      complemento para dois. Estuda o que muda em `B_max(w)`.
    """)
    return


if __name__ == "__main__":
    app.run()
