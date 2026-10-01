"""
Cifra de Vigenere - criptografar e decriptografar
Uso:
    python3 vigenere.py -d -t "LBMCOC IA AALVTEQPZ" -k LIMAO   # decriptografar
    python3 vigenere.py -c -t "ATACAR AO AMANHECER" -k LIMAO   # criptografar
    python3 vigenere.py -q                                     # quebrar os criptogramas da atividade
    python3 vigenere.py                                        # sem argumentos: pergunta tudo
"""

import argparse
import csv
import time
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
TAMANHO = len(ALFABETO)


def _expandir_chave(texto, chave):
    """Repete a chave para cobrir apenas as letras do texto (ignora espacos/pontuacao)."""
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
            chave_expandida.append(None)  # mantem posicao de nao-letras
    return chave_expandida


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
            resultado.append(letra)  # mantem espacos, pontuacao, numeros

    return "".join(resultado)


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


# =====================================================================
# Quebra dos criptogramas da atividade (criptogramas2.txt)
# =====================================================================

PASTA_ATIVIDADE = Path.home() / "Área de trabalho" / "SegurancaDaInformacao"

# Informacoes dadas no enunciado
CRIPTOGRAMAS_VIGENERE = [7, 11, 17, 22, 27, 33, 37, 44, 47, 55, 57, 66, 67]
PARES = {11: 10, 22: 21, 33: 32, 44: 43, 55: 54, 66: 65}  # vigenere -> monoalfabetico

# Frequencia das letras em portugues (%)
FREQ_PT = {
    "A": 14.63, "B": 1.04, "C": 3.88, "D": 4.99, "E": 12.57, "F": 1.02, "G": 1.30,
    "H": 1.28, "I": 6.18, "J": 0.40, "K": 0.02, "L": 2.78, "M": 4.74, "N": 5.05,
    "O": 10.73, "P": 2.52, "Q": 1.20, "R": 6.53, "S": 7.81, "T": 4.34, "U": 4.63,
    "V": 1.67, "W": 0.01, "X": 0.21, "Y": 0.01, "Z": 0.47,
}

MAX_CHAVE = 20          # maior tamanho de chave testado
TEMPO_MONO = 30         # segundos coletando solucoes do monoalfabetico do par
TEMPO_DICIONARIO = 10   # segundos de busca com dicionario por tamanho de chave


def ler_criptogramas(pasta):
    linhas = (pasta / "criptogramas2.txt").read_text().splitlines()
    cripto = {}
    for i, linha in enumerate(linhas):
        if linha.startswith("Criptograma #"):
            num = int(linha.split("#")[1].split(",")[0])
            cripto[num] = linhas[i + 1].strip().upper()
    return cripto


class Dicionario:
    def __init__(self, pasta):
        texto = (pasta / "dicionario2.txt").read_text()
        palavras = {p.strip().upper() for p in texto.splitlines() if p.strip()}
        self.conjunto = palavras
        self.maior = max(map(len, palavras))
        # palavras longas primeiro: restringem mais a busca e acham boas solucoes cedo
        self.lista = sorted(palavras, key=len, reverse=True)
        self.por_padrao = defaultdict(list)
        for p in self.lista:
            self.por_padrao[padrao(p)].append(p)

    def segmentar(self, texto):
        """Divide o texto em palavras do dicionario (menor numero de palavras) ou None."""
        @lru_cache(None)
        def f(i):
            if i == len(texto):
                return ()
            melhor = None
            for j in range(min(len(texto), i + self.maior), i, -1):
                if texto[i:j] in self.conjunto:
                    resto = f(j)
                    if resto is not None and (melhor is None or len(resto) + 1 < len(melhor)):
                        melhor = (texto[i:j],) + resto
            return melhor
        r = f(0)
        return list(r) if r is not None else None

    def cobertura(self, texto):
        """Maximo de letras do texto que podem ser cobertas por palavras do dicionario."""
        n = len(texto)
        melhor = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            melhor[i] = melhor[i + 1]
            for j in range(i + 1, min(n, i + self.maior) + 1):
                if texto[i:j] in self.conjunto:
                    melhor[i] = max(melhor[i], j - i + melhor[j])
        return melhor[0]


def padrao(palavra):
    """'CASA' -> (0, 1, 2, 1): formato de repeticao das letras."""
    vistos = {}
    return tuple(vistos.setdefault(c, len(vistos)) for c in palavra)


def fluxo_da_chave(texto_cifrado, texto_claro):
    """Letra da chave usada em cada posicao: cifra - claro."""
    return "".join(ALFABETO[(ALFABETO.index(c) - ALFABETO.index(p)) % TAMANHO]
                   for c, p in zip(texto_cifrado, texto_claro))


def menor_periodo(s):
    return next(L for L in range(1, len(s) + 1) if all(s[i] == s[i % L] for i in range(len(s))))


def reduzir_chave(chave):
    """Chave que e repeticao de um pedaco menor vira esse pedaco: URCAURCA -> URCA."""
    n = len(chave)
    return next(chave[:d] for d in range(1, n + 1) if n % d == 0 and chave[:d] * (n // d) == chave)


# ---------------------------------------------------------------- 1. pares

def solucoes_monoalfabetica(cifra, dic, tempo_max=TEMPO_MONO):
    """
    Gera textos claros possiveis para um criptograma monoalfabetico: cada palavra
    precisa ter o mesmo padrao de letras repetidas do trecho cifrado e o mapeamento
    cifra -> claro precisa continuar consistente.
    """
    n = len(cifra)
    cif_para_claro, claro_para_cif = {}, {}
    atual = []
    inicio = time.time()

    def rec(i):
        if time.time() - inicio > tempo_max:
            return
        if i == n:
            yield list(atual)
            return
        for j in range(min(n, i + dic.maior), i, -1):
            for palavra in dic.por_padrao.get(padrao(cifra[i:j]), ()):
                novos = []
                ok = True
                for c, l in zip(cifra[i:j], palavra):
                    if c in cif_para_claro:
                        ok = cif_para_claro[c] == l
                    elif l in claro_para_cif:
                        ok = False
                    else:
                        cif_para_claro[c] = l
                        claro_para_cif[l] = c
                        novos.append(c)
                    if not ok:
                        break
                if ok:
                    atual.append(palavra)
                    yield from rec(j)
                    atual.pop()
                for c in novos:
                    del claro_para_cif[cif_para_claro.pop(c)]

    yield from rec(0)


def quebrar_pelo_par(cifra_vig, cifra_mono, dic):
    """
    Os dois criptogramas tem o mesmo texto claro. Para cada texto claro possivel do
    monoalfabetico, calcula o fluxo da chave (cifra - claro) do Vigenere; a chave
    verdadeira se repete, entao fica com o texto claro de menor periodo.
    """
    melhor = None
    for palavras in solucoes_monoalfabetica(cifra_mono, dic):
        fluxo = fluxo_da_chave(cifra_vig, "".join(palavras))
        periodo = menor_periodo(fluxo)
        if melhor is None or (periodo, len(palavras)) < (len(melhor[0]), len(melhor[1])):
            melhor = (fluxo[:periodo], palavras)
    return melhor


# ---------------------------------------------------------------- 2. IC + frequencia

def indice_coincidencia(s):
    n = len(s)
    if n < 2:
        return 0.0
    return sum(v * (v - 1) for v in Counter(s).values()) / (n * (n - 1))


def tamanhos_por_ic(cifra):
    """Tamanhos de chave ordenados pelo IC medio das colunas (maior = mais provavel)."""
    tamanhos = range(1, min(MAX_CHAVE, len(cifra) // 2) + 1)
    def ic_medio(L):
        return sum(indice_coincidencia(cifra[i::L]) for i in range(L)) / L
    return sorted(tamanhos, key=ic_medio, reverse=True)


def letra_por_frequencia(coluna):
    """Letra da chave que minimiza o qui-quadrado entre a coluna decifrada e o portugues."""
    n = len(coluna)
    def qui2(k):
        cont = Counter(ALFABETO[(ALFABETO.index(c) - k) % TAMANHO] for c in coluna)
        return sum((cont[l] - n * f / 100) ** 2 / (n * f / 100) for l, f in FREQ_PT.items())
    return ALFABETO[min(range(TAMANHO), key=qui2)]


def quebrar_por_frequencia(cifra, L, dic):
    """
    Estima cada letra da chave pela frequencia e depois corrige letra por letra:
    troca uma posicao da chave se isso aumentar a parte do texto que vira palavras
    do dicionario. So aceita se o texto inteiro virar palavras.
    """
    chave = [letra_por_frequencia(cifra[i::L]) for i in range(L)]
    nota = dic.cobertura(decriptografar(cifra, "".join(chave)))
    melhorou = True
    while melhorou and nota < len(cifra):
        melhorou = False
        for pos in range(L):
            for letra in ALFABETO:
                tentativa = chave[:pos] + [letra] + chave[pos + 1:]
                n = dic.cobertura(decriptografar(cifra, "".join(tentativa)))
                if n > nota:
                    chave, nota, melhorou = tentativa, n, True
    if nota < len(cifra):
        return None
    chave = "".join(chave)
    return chave, dic.segmentar(decriptografar(cifra, chave))


# ---------------------------------------------------------------- 3. busca com dicionario

def quebrar_por_dicionario(cifra, L, dic, tempo_max=TEMPO_DICIONARIO):
    """
    Monta o texto claro palavra por palavra. Cada palavra testada fixa letras da chave
    nas posicoes i mod L, que nao podem contradizer as letras ja fixadas.
    Usada quando o texto e curto demais para a analise de frequencia funcionar.
    """
    n = len(cifra)
    chave = [None] * L
    atual = []
    inicio = time.time()

    def rec(i):
        if i == n:
            return True
        if time.time() - inicio > tempo_max:
            return False
        for palavra in dic.lista:
            if i + len(palavra) > n:
                continue
            fixadas = []
            ok = True
            for j, l in enumerate(palavra):
                k = (ALFABETO.index(cifra[i + j]) - ALFABETO.index(l)) % TAMANHO
                pos = (i + j) % L
                if chave[pos] is None:
                    chave[pos] = k
                    fixadas.append(pos)
                elif chave[pos] != k:
                    ok = False
                    break
            if ok:
                atual.append(palavra)
                if rec(i + len(palavra)):
                    return True
                atual.pop()
            for pos in fixadas:
                chave[pos] = None
        return False

    if not rec(0):
        return None
    return "".join(ALFABETO[k] for k in chave), list(atual)


# ---------------------------------------------------------------- orquestracao

def quebrar(num, cripto, dic):
    """Devolve (chave, palavras, metodo) ou None."""
    cifra = cripto[num]

    if num in PARES:
        r = quebrar_pelo_par(cifra, cripto[PARES[num]], dic)
        if r:
            return r[0], r[1], f"par com o #{PARES[num]}"

    tamanhos = tamanhos_por_ic(cifra)
    for L in tamanhos:
        r = quebrar_por_frequencia(cifra, L, dic)
        if r:
            return r[0], r[1], f"IC (L={L}) + frequencia"
    for L in tamanhos:
        r = quebrar_por_dicionario(cifra, L, dic)
        if r:
            return r[0], r[1], f"busca com dicionario (L={L})"
    return None


def quebrar_atividade(pasta=PASTA_ATIVIDADE):
    cripto = ler_criptogramas(pasta)
    dic = Dicionario(pasta)
    destino = pasta / "respostas_vigenere.csv"

    with open(destino, "w", newline="", encoding="utf-8") as arq:
        saida = csv.writer(arq, delimiter=";")
        saida.writerow(["Texto criptografado", "Senha", "Texto descriptografado"])
        for num in CRIPTOGRAMAS_VIGENERE:
            r = quebrar(num, cripto, dic)
            if r:
                chave, palavras, metodo = r
                chave = reduzir_chave(chave)
                claro = " ".join(palavras)
                assert decriptografar(cripto[num], chave) == "".join(palavras)
            else:
                chave, claro, metodo = "?", "(nao resolvido)", "sem solucao"
            saida.writerow([cripto[num], chave, claro])
            print(f"#{num:<3} {chave:<18} {claro}   [{metodo}]", flush=True)

    print(f"\nRespostas gravadas em {destino}")


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
    modo.add_argument(
        "-q", "--quebrar", action="store_true",
        help="quebrar os criptogramas Vigenere de criptogramas2.txt e gerar respostas_vigenere.csv",
    )
    parser.add_argument(
        "--pasta", type=Path, default=PASTA_ATIVIDADE,
        help="pasta com criptogramas2.txt e dicionario2.txt",
    )
    parser.add_argument("-t", "--texto", help="texto a ser processado")
    parser.add_argument("-k", "--chave", help="chave da cifra")

    args = parser.parse_args()

    # se nao disse o modo pela linha de comando, pergunta
    if args.quebrar:
        modo_escolhido = "quebrar"
    elif args.criptografar:
        modo_escolhido = "criptografar"
    elif args.decriptografar:
        modo_escolhido = "decriptografar"
    else:
        print("=== Cifra de Vigenere ===")
        print("1 - Decriptografar (tenho o texto cifrado e a chave)")
        print("2 - Criptografar (tenho o texto claro e a chave)")
        print("3 - Quebrar os criptogramas da atividade (sem a chave)")
        opcao = input("Escolha uma opcao (1/2/3): ").strip()
        if opcao == "1":
            modo_escolhido = "decriptografar"
        elif opcao == "2":
            modo_escolhido = "criptografar"
        elif opcao == "3":
            modo_escolhido = "quebrar"
        else:
            print("Opcao invalida.")
            return

    if modo_escolhido == "quebrar":
        quebrar_atividade(args.pasta)
        return

    texto = args.texto if args.texto else input(
        "Digite o texto cifrado: " if modo_escolhido == "decriptografar" else "Digite o texto claro: "
    )
    chave = args.chave if args.chave else input("Digite a chave: ")

    try:
        if modo_escolhido == "decriptografar":
            print("\nTexto claro:")
            print(decriptografar(texto, chave))
        else:
            print("\nTexto cifrado:")
            print(criptografar(texto, chave))
    except ValueError as erro:
        print(f"Erro: {erro}")


if __name__ == "__main__":
    main()
