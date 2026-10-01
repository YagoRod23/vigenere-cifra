# Documentação do script `vigenere.py`

Este documento explica em detalhes o funcionamento do script `vigenere.py`
(localizado em `/home/yago/vigenere.py`), que implementa a **Cifra de
Vigenère** para fins de estudo da disciplina de Segurança da Informação.

---

## 1. Contexto teórico rápido

A Cifra de Vigenère é uma cifra de substituição polialfabética. Diferente da
Cifra de César (que desloca todas as letras do texto pela mesma quantidade),
a Vigenère usa uma **palavra-chave** cujas letras definem deslocamentos
diferentes para cada posição do texto.

- Cada letra do alfabeto é mapeada para um número: `A=0, B=1, C=2, ..., Z=25`.
- Para **criptografar**: `letra_cifrada = (letra_texto + letra_chave) mod 26`
- Para **decriptografar**: `letra_texto = (letra_cifrada - letra_chave) mod 26`
- A chave é repetida (concatenada com ela mesma) até cobrir o tamanho do
  texto. Por isso ela é chamada de polialfabética: a mesma letra do texto
  claro pode virar letras diferentes na cifra, dependendo da posição.

Exemplo: texto `ATACAR`, chave `LIMAO` → a chave se expande para `LIMAOL`
(repete até cobrir as 6 letras do texto).

---

## 2. Estrutura geral do arquivo

```
vigenere.py
├── Constantes globais (ALFABETO, TAMANHO)
├── _expandir_chave(texto, chave)   -> função auxiliar (privada)
├── criptografar(texto_claro, chave) -> função pública
├── decriptografar(texto_cifrado, chave) -> função pública
└── main()                          -> ponto de entrada (CLI)
```

O script foi dividido assim de propósito: as funções `criptografar` e
`decriptografar` são **puras** (não leem nem imprimem nada, só recebem
texto/chave e devolvem o resultado). Isso facilita testar, reutilizar em
outro script, ou importar (`from vigenere import criptografar`) sem rodar o
menu. Quem lida com entrada/saída do usuário é só a `main()`.

---

## 3. Constantes globais

```python
ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
TAMANHO = len(ALFABETO)
```

- `ALFABETO`: string com as 26 letras maiúsculas. Ela funciona como uma
  "tabela de conversão": a **posição** de uma letra dentro dessa string é o
  seu valor numérico (`ALFABETO.index("A")` é `0`, `ALFABETO.index("B")` é
  `1`, e assim por diante até `ALFABETO.index("Z")` ser `25`).
- `TAMANHO`: guarda `26`. É usado nas operações de módulo (`% TAMANHO`) para
  garantir que o resultado sempre "dê a volta" dentro do alfabeto (depois do
  `Z` volta para o `A`).

> Nota: o alfabeto não inclui acentos (á, ç, ã, etc.). Se o texto tiver
> essas letras, elas são tratadas como caracteres "fora do alfabeto" e
> passam direto sem cifrar (ver seção 4).

---

## 4. Função `_expandir_chave(texto, chave)`

```python
def _expandir_chave(texto, chave):
    chave = [c for c in chave.upper() if c in ALFABETO]
    if not chave:
        raise ValueError("A chave precisa ter pelo menos uma letra (A-Z).")

    chave_expandida = []
    i = 0
    for letra in texto.upper():
        if letra in ALFABETO:
            chave_expandida.append(chave[i % len(chave)])
            i += 1
        else:
            chave_expandida.append(None)
    return chave_expandida
```

**Propósito:** gerar uma lista do mesmo tamanho do texto, onde cada posição
contém a letra da chave que deve ser usada para cifrar/decifrar aquela
posição específica do texto. É a parte mais importante do algoritmo, porque
é aqui que a chave "se repete" corretamente, inclusive quando o texto tem
espaços ou pontuação.

**Linha a linha:**

- `chave = [c for c in chave.upper() if c in ALFABETO]`
  Essa é uma *list comprehension*. Ela transforma a chave (ex.: `"limao"`)
  em maiúsculas (`"LIMAO"`) e depois filtra **apenas** os caracteres que
  existem em `ALFABETO`. Resultado: `['L', 'I', 'M', 'A', 'O']`. Isso evita
  que, se o usuário digitar uma chave com espaço ou número por engano, o
  programa quebre ou gere um deslocamento errado.

- `if not chave: raise ValueError(...)`
  Validação: se depois do filtro a lista ficou vazia (ex.: usuário digitou
  `"123"` como chave), o programa não tem como continuar — não existe
  deslocamento possível. Em vez de deixar o erro acontecer mais adiante de
  forma confusa (como um `IndexError`), o código já avisa o problema real
  com uma mensagem clara.

- `chave_expandida = []` e `i = 0`
  `chave_expandida` vai guardar o resultado final (uma letra da chave — ou
  `None` — para cada caractere do texto). `i` é o "ponteiro" que indica qual
  letra da chave usar a seguir, mas **só avança quando encontra uma letra
  do alfabeto** no texto.

- `for letra in texto.upper():`
  Percorre o texto original, caractere por caractere, já convertido para
  maiúsculas (facilita a comparação com `ALFABETO`, que só tem maiúsculas).

- `if letra in ALFABETO:`
  Testa se o caractere atual é uma letra válida (A-Z).
  - `chave_expandida.append(chave[i % len(chave)])`: pega a i-ésima letra da
    chave, usando `% len(chave)` para "dar a volta" na chave quando ela
    acabar (é exatamente isso que faz a chave se repetir: `LIMAO`, `LIMAO`,
    `LIMAO`...).
  - `i += 1`: avança o ponteiro da chave **somente** porque essa posição
    consumiu uma letra da chave.
- `else: chave_expandida.append(None)`
  Se o caractere **não** é uma letra (é espaço, vírgula, número...), a
  chave não avança (`i` não aumenta) e é guardado `None` nessa posição —
  é um "marcador" dizendo "aqui não tem deslocamento, ignore".

**Por que isso importa:** sem essa lógica de "só avançar a chave em
letras", uma frase como `"ATACAR AO"` (com espaço) desalinharia a chave em
relação ao texto. Esse é um detalhe clássico de implementações de Vigenère:
decidir se espaços/pontuação contam ou não como posição da chave. Aqui a
escolha foi **não contar**, que é o comportamento mais comum nos exercícios
de sala de aula.

---

## 5. Função `criptografar(texto_claro, chave)`

```python
def criptografar(texto_claro, chave):
    chave_expandida = _expandir_chave(texto_claro, chave)
    resultado = []

    for letra, k in zip(texto_claro.upper(), chave_expandida):
        if letra in ALFABETO:
            desloc_texto = ALFABETO.index(letra)
            desloc_chave = ALFABETO.index(k)
            nova_letra = ALFABETO[(desloc_texto + desloc_chave) % TAMANHO]
            resultado.append(nova_letra)
        else:
            resultado.append(letra)

    return "".join(resultado)
```

**Propósito:** aplicar a fórmula de criptografia da Vigenère
(`C = (P + K) mod 26`) em cada letra do texto claro.

**Linha a linha:**

- `chave_expandida = _expandir_chave(texto_claro, chave)`
  Reaproveita a função explicada na seção 4 para já ter, para cada posição
  do texto, qual letra da chave (ou `None`) usar.

- `for letra, k in zip(texto_claro.upper(), chave_expandida):`
  `zip()` percorre **duas listas ao mesmo tempo**, em paralelo: a posição 0
  do texto com a posição 0 da chave expandida, a posição 1 com a 1, etc.
  Isso garante que `letra` e `k` sempre correspondem à mesma posição.

- `if letra in ALFABETO:`
  Só aplica a fórmula se o caractere for uma letra válida.
  - `desloc_texto = ALFABETO.index(letra)`: converte a letra do texto no seu
    valor numérico (ex.: `A` → `0`).
  - `desloc_chave = ALFABETO.index(k)`: converte a letra correspondente da
    chave no seu valor numérico (ex.: `L` → `11`).
  - `nova_letra = ALFABETO[(desloc_texto + desloc_chave) % TAMANHO]`: essa é
    **a fórmula da cifra**. Soma os dois deslocamentos e usa `% 26` para
    garantir que o resultado "dê a volta" se passar de 25 (por exemplo,
    `Z` + `B` não pode virar posição 27 — tem que voltar para o começo do
    alfabeto). O resultado numérico é usado como índice para buscar a letra
    correspondente em `ALFABETO`.
  - `resultado.append(nova_letra)`: guarda a letra cifrada.

- `else: resultado.append(letra)`
  Se não é uma letra (espaço, vírgula etc.), copia o caractere original sem
  alterar — é por isso que a formatação do texto (espaços, pontuação)
  permanece igual no resultado final.

- `return "".join(resultado)`
  `resultado` é uma lista de caracteres (ex.: `['L', 'B', 'M', ...]`).
  `"".join(...)` junta tudo em uma única string, sem separador, formando o
  texto cifrado final.

---

## 6. Função `decriptografar(texto_cifrado, chave)`

```python
def decriptografar(texto_cifrado, chave):
    chave_expandida = _expandir_chave(texto_cifrado, chave)
    resultado = []

    for letra, k in zip(texto_cifrado.upper(), chave_expandida):
        if letra in ALFABETO:
            desloc_texto = ALFABETO.index(letra)
            desloc_chave = ALFABETO.index(k)
            nova_letra = ALFABETO[(desloc_texto - desloc_chave) % TAMANHO]
            resultado.append(nova_letra)
        else:
            resultado.append(letra)

    return "".join(resultado)
```

**Propósito:** fazer o processo inverso — aplicar `P = (C - K) mod 26` para
recuperar o texto original a partir do texto cifrado.

É estruturalmente **idêntica** à função `criptografar`, com uma única
diferença crucial:

```python
nova_letra = ALFABETO[(desloc_texto - desloc_chave) % TAMANHO]
```

Aqui o deslocamento da chave é **subtraído**, não somado. Isso desfaz
exatamente a operação feita na criptografia. Por exemplo: se na cifra
`A (0) + L (11) = L (11)`, na decifra fazemos `L (11) - L (11) = A (0)`,
recuperando a letra original.

**Por que o `% TAMANHO` aqui também é essencial:** em Python, o operador
`%` já trata números negativos de forma que o resultado fica sempre
positivo (diferente de outras linguagens como C ou Java). Por exemplo,
`(2 - 11) % 26` dá `17` em Python (não `-9`). Isso é o que permite que a
subtração "dê a volta" para trás no alfabeto corretamente quando o
resultado seria negativo — sem esse detalhe, o código quebraria para várias
combinações de texto/chave.

---

## 7. Função `main()` — interface de linha de comando

```python
def main():
    parser = argparse.ArgumentParser(
        description="Cifra de Vigenere - criptografar ou decriptografar um texto."
    )
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument(
        "-d", "--decriptografar", action="store_true", help="decriptografar o texto"
    )
    modo.add_argument(
        "-c", "--criptografar", action="store_true", help="criptografar o texto"
    )
    parser.add_argument("-t", "--texto", help="texto a ser processado")
    parser.add_argument("-k", "--chave", help="chave da cifra")

    args = parser.parse_args()
```

**Propósito:** permitir que o script seja usado tanto via **argumentos de
linha de comando** (ex.: `python3 vigenere.py -d -t "..." -k LIMAO`) quanto
de forma **interativa** (perguntando tudo pelo terminal), sem duplicar
código.

**Linha a linha:**

- `argparse.ArgumentParser(...)`: cria o "leitor" de argumentos. É a
  biblioteca padrão do Python para scripts de linha de comando — ela
  automaticamente gera a opção `-h`/`--help` com uma mensagem de uso.
- `parser.add_mutually_exclusive_group()`: cria um grupo onde **só uma**
  das opções pode ser usada por vez. Isso impede que o usuário passe `-d` e
  `-c` ao mesmo tempo (o que não faria sentido — seria uma ambiguidade
  entre criptografar e decriptografar no mesmo comando).
- `modo.add_argument("-d", "--decriptografar", action="store_true", ...)`:
  define a flag `-d` (ou `--decriptografar`). `action="store_true"` quer
  dizer que é uma flag *booleana*: se o usuário passar `-d`, o valor de
  `args.decriptografar` vira `True`; se não passar, fica `False`. Não
  recebe um valor depois, é só "presença ou ausência".
- O mesmo vale para `-c`/`--criptografar`.
- `parser.add_argument("-t", "--texto", help=...)`: define uma opção que
  **espera um valor** depois dela (ex.: `-t "ATACAR"`). Fica guardado em
  `args.texto`.
- `parser.add_argument("-k", "--chave", help=...)`: mesma ideia, para a
  chave (`args.chave`).
- `args = parser.parse_args()`: efetivamente lê os argumentos passados pelo
  usuário no terminal (`sys.argv`) e os organiza no objeto `args`, onde
  cada argumento vira um atributo (`args.texto`, `args.chave`, etc.).

```python
    if args.criptografar:
        modo_escolhido = "criptografar"
    elif args.decriptografar:
        modo_escolhido = "decriptografar"
    else:
        print("=== Cifra de Vigenere ===")
        print("1 - Decriptografar (tenho o texto cifrado e a chave)")
        print("2 - Criptografar (tenho o texto claro e a chave)")
        opcao = input("Escolha uma opcao (1/2): ").strip()
        if opcao == "1":
            modo_escolhido = "decriptografar"
        elif opcao == "2":
            modo_escolhido = "criptografar"
        else:
            print("Opcao invalida.")
            return
```

**Propósito:** decidir se o script vai criptografar ou decriptografar.

- Primeiro verifica se o usuário já disse isso via `-c` ou `-d` na linha de
  comando. Se sim, não precisa perguntar nada — `modo_escolhido` já é
  definido direto.
- Se **nenhuma das duas flags** foi passada (`else`), o script cai no modo
  interativo: imprime um menu numerado e usa `input()` para ler a escolha
  do usuário pelo teclado.
- `opcao.strip()`: remove espaços em branco acidentais que o usuário possa
  ter digitado antes/depois do número (ex.: `" 1 "` vira `"1"`).
- Se a opção digitada não for `"1"` nem `"2"`, imprime erro e `return`
  (sai da função `main()` imediatamente, sem tentar processar nada).

```python
    texto = args.texto if args.texto else input(
        "Digite o texto cifrado: " if modo_escolhido == "decriptografar" else "Digite o texto claro: "
    )
    chave = args.chave if args.chave else input("Digite a chave: ")
```

**Propósito:** obter o texto e a chave, dando prioridade ao que já foi
passado por argumento — e perguntando por `input()` apenas o que estiver
faltando.

- `args.texto if args.texto else input(...)`: isso é um *operador
  ternário*. Lê-se "use `args.texto` se ele existir (não for `None`/vazio);
  caso contrário, chame `input(...)` para perguntar". Isso é o que permite
  **misturar** os dois modos: por exemplo, rodar `python3 vigenere.py -d`
  (só informando o modo) e o script perguntar apenas o texto e a chave que
  faltaram.
- A mensagem do `input()` muda dinamicamente dependendo do modo
  (`"Digite o texto cifrado:"` para decriptografar, `"Digite o texto
  claro:"` para criptografar) — isso ajuda o usuário a não se confundir
  sobre qual texto ele deveria estar colando.
- A mesma lógica se repete para a `chave`.

```python
    try:
        if modo_escolhido == "decriptografar":
            print("\nTexto claro:")
            print(decriptografar(texto, chave))
        else:
            print("\nTexto cifrado:")
            print(criptografar(texto, chave))
    except ValueError as erro:
        print(f"Erro: {erro}")
```

**Propósito:** executar de fato a operação escolhida e mostrar o
resultado, tratando o caso de erro (chave inválida).

- O bloco `try/except` captura o `ValueError` que pode ser lançado lá
  dentro de `_expandir_chave` (seção 4), caso a chave não tenha nenhuma
  letra válida. Em vez de o programa travar com uma mensagem técnica feia
  (um *traceback* do Python), ele mostra uma mensagem de erro amigável:
  `"Erro: A chave precisa ter pelo menos uma letra (A-Z)."`.
- Dependendo do `modo_escolhido`, chama `decriptografar(...)` ou
  `criptografar(...)` (as funções explicadas nas seções 5 e 6) e imprime o
  resultado.

```python
if __name__ == "__main__":
    main()
```

**Propósito:** esse é um padrão clássico em Python. `__name__` é uma
variável especial que o Python define automaticamente: ela vale
`"__main__"` quando o arquivo é executado diretamente (ex.: `python3
vigenere.py`), mas vale o nome do módulo (`"vigenere"`) quando o arquivo é
**importado** por outro script (ex.: `from vigenere import criptografar`).

Isso significa: se alguém importar `vigenere.py` só para usar as funções
`criptografar`/`decriptografar` em outro programa, o menu/CLI (`main()`)
**não** é executado automaticamente — só roda quando o arquivo é chamado
diretamente pelo terminal. É uma boa prática que torna o script reutilizável
como biblioteca também.

---

## 8. Resumo do fluxo completo (exemplo prático)

Comando: `python3 vigenere.py -d -t "LBMCOC IA AALVTEQPZ" -k LIMAO`

1. `argparse` lê `-d` → `args.decriptografar = True`.
2. `args.texto = "LBMCOC IA AALVTEQPZ"`, `args.chave = "LIMAO"`.
3. Como `args.decriptografar` é `True`, `modo_escolhido = "decriptografar"`
   — não pergunta nada no menu.
4. `texto` e `chave` já vêm preenchidos pelos argumentos, não chama
   `input()`.
5. Entra no `try`, chama `decriptografar("LBMCOC IA AALVTEQPZ", "LIMAO")`.
6. Dentro de `decriptografar`:
   - `_expandir_chave` gera a chave expandida letra a letra, pulando os
     espaços (ex.: `L, I, M, A, O, L, I, A, A, L, I, M, A, O, L, I, M, A`).
   - Para cada letra do texto cifrado, subtrai o deslocamento da chave
     correspondente, módulo 26.
   - Espaços são copiados sem alteração.
7. Resultado final: `"ATACAR AO AMANHECER"`, impresso na tela.

---

## 9. Possíveis pontos de atenção para a disciplina

- **Não trata acentos/cedilha**: como `ALFABETO` só tem A-Z, caracteres
  como `Ã`, `Ç`, `É` são tratados como "fora do alfabeto" e passam direto
  sem cifrar (igual espaço/pontuação). Se o exercício exigir alfabeto
  estendido, a constante `ALFABETO` precisaria ser expandida e `TAMANHO`
  ajustado.
- **Espaços/pontuação não avançam a chave**: essa é uma escolha de design
  (a mais comum nos exercícios). Algumas variantes de Vigenère tratam o
  espaço como mais um símbolo do "alfabeto" e fazem a chave avançar mesmo
  nele — vale conferir qual convenção o professor está usando.
- **Caixa (maiúscula/minúscula)**: o script converte tudo para maiúsculas
  no resultado. Se for necessário preservar a caixa original do texto
  (ex.: `"Ataque"` → `"Lbmcoc"` em vez de `"LBMCOC"`), seria preciso um
  ajuste adicional guardando se cada letra era maiúscula ou minúscula antes
  de converter.
