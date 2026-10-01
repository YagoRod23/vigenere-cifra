# Cifra de Vigenère

Script em Python para criptografar e decriptografar textos com a **Cifra de
Vigenère**, feito para estudo da disciplina de Segurança da Informação.

## Uso

```bash
# decriptografar
python3 vigenere.py -d -t "LBMCOC IA AALVTEQPZ" -k LIMAO

# criptografar
python3 vigenere.py -c -t "ATACAR AO AMANHECER" -k LIMAO

# quebrar os criptogramas Vigenere da atividade (sem a chave)
# le criptogramas2.txt e dicionario2.txt de ~/Área de trabalho/SegurancaDaInformacao
# e gera respostas_vigenere.csv (texto criptografado; senha; texto descriptografado)
python3 vigenere.py -q
python3 vigenere.py -q --pasta /outra/pasta

# modo interativo (sem argumentos, pergunta tudo)
python3 vigenere.py
```

Veja [`vigenere_documentacao.md`](vigenere_documentacao.md) para uma
explicação detalhada do código, método por método.
