# Cifra de Vigenère

Script em Python para criptografar e decriptografar textos com a **Cifra de
Vigenère**, feito para estudo da disciplina de Segurança da Informação.

## Uso

```bash
# decriptografar
python3 vigenere.py -d -t "LBMCOC IA AALVTEQPZ" -k LIMAO

# criptografar
python3 vigenere.py -c -t "ATACAR AO AMANHECER" -k LIMAO

# modo interativo (sem argumentos, pergunta tudo)
python3 vigenere.py
```

Veja [`vigenere_documentacao.md`](vigenere_documentacao.md) para uma
explicação detalhada do código, método por método.
