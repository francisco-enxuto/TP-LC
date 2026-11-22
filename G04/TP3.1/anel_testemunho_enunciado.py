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
    # Trabalho Prático 3 — Exercício 1: Exclusão mútua num anel com testemunho

    ## Contexto

    Um dos protocolos mais simples de **exclusão mútua** distribuída organiza
    os processos num anel e faz circular entre eles um único **testemunho**
    (*token*). Um processo só pode entrar na secção crítica quando tem o
    testemunho. Ao sair, passa-o ao vizinho seguinte.

    Como há um só testemunho, nunca podem estar dois processos na secção
    crítica ao mesmo tempo. Este argumento informal apoia-se em factos que
    não estão escritos em nenhuma das regras de transição. Para provar a
    segurança, um algoritmo de verificação tem de descobrir sozinho um
    invariante suficientemente forte.

    Este exercício usa o protocolo para comparar as técnicas de verificação
    de segurança do **Capítulo 4**:

    - a $k$-indução, já usada no TP2;
    - o algoritmo **PDR** (*Property Directed Reachability*);
    - o algoritmo de **interpolantes e invariantes** da 1ª parte;
    - o **Spacer**, o *solver* de CHCs do Z3.

    ## O sistema

    Há $N$ processos, numerados $0,1,\dots,N-1$ e dispostos em anel: o
    sucessor do processo $i$ é o processo $i+1 \bmod N$. O estado do
    processo $i$ é dado por três variáveis booleanas:

    | variável | significado |
    |---|---|
    | $w_i$ | o processo está **à espera** de entrar na secção crítica |
    | $c_i$ | o processo está **na secção crítica** |
    | $t_i$ | o processo **tem o testemunho** |

    Um processo está **inativo** quando $\neg w_i \land \neg c_i$.

    **Estado inicial.** Todos os processos estão inativos e só o processo
    $0$ tem o testemunho:

    $$\mathsf{I} \;\equiv\; \bigwedge_{i}\big(\neg w_i \land \neg c_i\big)\;\land\; t_0 \;\land\; \bigwedge_{i\neq 0}\neg t_i$$

    **Transições.** Em cada transição move-se **um único** processo $i$,
    segundo uma das quatro regras seguintes. As variáveis que a regra não
    menciona mantêm o seu valor.

    | regra | condição | efeito |
    |---|---|---|
    | **pedir** | processo $i$ inativo | $w_i' = \mathtt{True}$ |
    | **entrar** | $w_i \land t_i$ | $w_i' = \mathtt{False}$, $c_i' = \mathtt{True}$ |
    | **sair** | $c_i$ | $c_i' = \mathtt{False}$, $t_i' = \mathtt{False}$, $t_{i+1 \bmod N}' = \mathtt{True}$ |
    | **passar** | processo $i$ inativo e $t_i$ | $t_i' = \mathtt{False}$, $t_{i+1 \bmod N}' = \mathtt{True}$ |

    **Estado de erro.** Dois processos na secção crítica:

    $$\mathsf{E} \;\equiv\; \bigvee_{i<j}\, c_i \land c_j$$

    **Variante com regeneração** (alínea 4). Acrescenta-se uma quinta regra,
    que modela a recuperação de um testemunho perdido:

    | regra | condição | efeito |
    |---|---|---|
    | **regenerar** | $w_i \land \neg t_i$ | $t_i' = \mathtt{True}$ |
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Pretende-se

    1. Construir o SFOTS proposicional em Z3, parametrizado por $N$.
    2. Mostrar que a $k$-indução usada no TP2 falha para valores pequenos
       de $k$, mesmo com traços simples. Apresentar o contra-exemplo ao passo
       indutivo e explicar por que não é acessível.
    3. Verificar a segurança do sistema com dois algoritmos:
        - o PDR, usando a implementação `pdr_lia.py` que está no
          [repositório LC](https://github.com/jmvalenca/LC.git);
        - o algoritmo de interpolantes e invariantes da 1ª parte, com os
          interpolantes calculados via CHCs.

        Em ambos os casos extrair o invariante indutivo obtido e verificá-lo
        de forma independente.
    4. Considerar a variante em que um processo à espera e sem testemunho
       pode regenerar um testemunho (recuperação de perda). Ambos os
       algoritmos da alínea anterior devem detetar a insegurança; apresentar
       um traço de erro obtido com BMC.
    5. Comparar, para $N$ crescente, o comportamento do PDR, do algoritmo de
       interpolantes e invariantes e do Spacer: tempo de execução, número de
       iterações e dimensão do invariante obtido.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Requisitos obrigatórios

    O teu notebook tem de expor os elementos seguintes, com o comportamento
    indicado. Os nomes são sugestões que facilitam a correção; podes usar
    outros, desde que documentes a correspondência.

    ### `anel(N, regenera=False)` — o SFOTS (R1, alínea 1)

    Uma função que devolve o SFOTS $\Sigma = \langle \mathsf{X}, \mathsf{I}, \mathsf{T}, \mathsf{E}\rangle$
    do anel com $N$ processos. O resultado deve dar acesso a:

    - o vetor de variáveis de estado $\mathsf{X}$ e o vetor $\mathsf{X}'$ dos seus "clones";
    - os predicados $\mathsf{I}(\mathsf{X})$ e $\mathsf{E}(\mathsf{X})$;
    - a relação de transição $\mathsf{T}(\mathsf{X},\mathsf{X}')$.

    Deve também ser possível instanciar estes predicados sobre outras
    cópias das variáveis (por exemplo $\mathsf{X}_0,\dots,\mathsf{X}_k$),
    porque o BMC, a $k$-indução e o algoritmo de interpolantes precisam
    delas. Com `regenera=True` a relação de transição inclui a regra
    **regenerar**.

    ### `k_inducao(S, k)` — $k$-indução (R2, alínea 2)

    Devolve o resultado do caso base e do passo indutivo para o SFOTS `S`.
    Quando o passo indutivo falha, devolve também o contra-exemplo, isto é,
    a sequência de $k+1$ estados. O notebook deve mostrar esse
    contra-exemplo de forma legível e explicar por que não é acessível a
    partir de $\mathsf{I}$.

    ### PDR e interpolantes (R3, alínea 3)

    - **PDR.** Usa o `PDR` de `pdr_lia.py`, sem o reimplementar. Esse código
      trabalha com variáveis inteiras e com CFAs. Cabe-te construir a
      tradução do teu SFOTS para esse formato e justificá-la.
    - **Interpolantes e invariantes.** Uma função `itp_mc(S, ...)` que
      implementa o algoritmo da 1ª parte do Capítulo 4, incluindo a rotina
      de procura do majorante. Os interpolantes são calculados com a função
      `interpolate` (CHCs/Spacer) da 3ª parte. A função devolve `safe`,
      com o invariante, ou `unsafe`, com o par de índices $(n,m)$ em que a
      insegurança foi detetada.
    - **Verificação independente.** Uma função `e_invariante(S, inv)` que
      verifica, sem recorrer a nenhum dos algoritmos acima, que `inv` é um
      invariante indutivo que separa $\mathsf{I}$ de $\mathsf{E}$. São três
      testes de insatisfazibilidade:
      $\mathsf{I}\land\neg\mathsf{inv}$,
      $\mathsf{inv}\land\mathsf{T}\land\neg\mathsf{inv}'$ e
      $\mathsf{inv}\land\mathsf{E}$.

    ### `bmc(S, K)` — traço de erro (R4, alínea 4)

    Devolve o traço mais curto, de comprimento $\le K$, de um estado inicial
    até um estado de erro, ou `None` se não existir. O traço deve ser
    apresentado indicando, em cada passo, **qual a regra** e **qual o
    processo** que se moveram.

    ### Comparação (R5, alínea 5)

    Uma tabela, com $N = 2, 3, 4, \dots$, que regista para cada algoritmo:

    - o resultado;
    - o tempo de execução;
    - o número de iterações (frames do PDR, pares $(n,m)$ do algoritmo de
      interpolantes);
    - a dimensão do invariante (por exemplo, o número de lemas ou de
      cláusulas).

    A tabela inclui a versão segura e a variante com regeneração.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Notas técnicas

    - **`pdr_lia.py` e variáveis booleanas.** O PDR do repositório só
      aceita variáveis `Int`. Uma tradução possível representa cada
      booleano por um inteiro restringido a $\{0,1\}$. As restrições de
      domínio têm de estar nas relações $\tau$ de **todos** os ramos que
      escrevem em $\mathsf{X}'$. O SFOTS cabe num CFA com um só local de
      trabalho: `system → do` (inicialização), `do → do` (transição) e
      `do → error` (guarda $\mathsf{E}$).
    - **Interpolantes quantificados.** O interpolante devolvido pelo Spacer
      através de `interpolate` pode conter quantificadores. Quando é
      reutilizado numa nova chamada (por exemplo, na rotina do majorante),
      o Spacer responde muitas vezes `unknown`. Num domínio finito, como
      este, os quantificadores podem ser eliminados com `z3.Tactic('qe')`.
    - **Escala.** O PDR de `pdr_lia.py` é didático. Para este problema,
      conta com tempos da ordem de minutos a partir de $N=5$. A comparação
      deve parar num $N$ em que todos os algoritmos ainda respondam num
      tempo razoável, e o notebook deve dizer onde fica esse limite.

    ## Como testar/validar

    O notebook tem de verificar automaticamente:

    - que, para pequenos $N$ (por exemplo $N\le 3$), a resposta de cada
      algoritmo coincide com uma exploração exaustiva dos estados
      acessíveis. Basta uma pesquisa em largura, que serve de referência
      independente;
    - que todo o invariante devolvido passa em `e_invariante`;
    - que o traço de erro devolvido por `bmc` é de facto um traço do SFOTS:
      começa num estado inicial, cada passo satisfaz $\mathsf{T}$ e acaba
      num estado de erro;
    - que os três algoritmos concordam entre si em todos os casos da tabela
      da alínea 5.

    ## O que é deixado ao teu critério

    Desde que justificadas no notebook, ficam ao teu critério:

    - a representação do SFOTS (classe, dicionário, funções sobre listas de
      variáveis…);
    - a estratégia de incremento dos índices $(n,m)$ no algoritmo de
      interpolantes e o limite de iterações da rotina do majorante;
    - os limites de tempo e de iterações usados em cada algoritmo;
    - a forma de apresentar os invariantes. Por exemplo, podes simplificá-los
      e explicar o que dizem sobre o protocolo.

    ## Extensões opcionais (bónus)

    - **Invariante à mão.** Escreve à mão um invariante indutivo que
      traduza o argumento informal da secção "Contexto". Mostra que é
      indutivo e compara-o com os invariantes que os algoritmos encontram.
    - **$k$-indução reforçada.** Mostra que a $k$-indução passa a funcionar
      quando se reforça a propriedade com esse invariante.
    - **Outras variantes.** Por exemplo, dois testemunhos com dois recursos
      distintos, ou um anel bidirecional. Discute quais continuam seguras.
    - **PDR proposicional.** Compara o `pdr_lia.py` com a implementação
      `pysmt` da 2ª parte do Capítulo 4. Explica por que é que esta última
      não termina neste problema e o que lhe falta.
    """)
    return


if __name__ == "__main__":
    app.run()
