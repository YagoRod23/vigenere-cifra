"""
Cifra de Vigenere - criptografar e decriptografar
Uso:
    python3 vigenere.py -d -t "LBMCOC IA AALVTEQPZ" -k LIMAO   # decriptografar
    python3 vigenere.py -c -t "ATACAR AO AMANHECER" -k LIMAO   # criptografar
    python3 vigenere.py                                        # sem argumentos: pergunta tudo
"""

import argparse

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

    # se nao disse o modo pela linha de comando, pergunta
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
