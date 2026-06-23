# 📝 Guião 3
## Relatório de Implementação: `cfich_chacha20.py`

### 📌 Objetivo

> Defina o programa `cfich_chacha20.py` que cifra um ficheiro usando a cifra sequencial [`ChaCha20`](https://cryptography.io/en/stable/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.algorithms.ChaCha20). O programa receba como argumentos:
> - o tipo de operação a realizar: `setup`, `enc` ou `dec`
> - `setup <fkey>` cria ficheiro contendo uma chave apropriada para a cifra `Chacha20` (com nome `<fkey>`)
> - `enc <fich> <fkey>` cifra ficheiro passado como argumento `<fich>`, usando a chave lida do ficheiro `<fkey>`. O criptograma resultante deverá ser gravado `<fich>.enc` (i.e. adiciona a extensão `.enc` ao nome do ficheiro de texto-limpo).
> - `dec <fich> <fkey>` decifra criptograma contido em `<fich>`, usando a chave lida do ficheiro `<fkey>`. Armazena o texto-limpo recuperado num ficheiro com nome `<fich>.dec`.

### 🛠️ Estrutura Lógica do Código

-

### 📊 Resultado

![]()

---

>**QUESTÃO: Q2**
>* Qual o impacto de se considerar um *NONCE* fixo (e.g. tudo `0`)? Que implicações terá essa prática na segurança da cifra?

---

>**QUESTÃO: Q3**
>* Pode todo o conteúdo do ficheiro ser adulterado por troca de um único bit do criptograma (i.e. do conteúdo do ficheiro `<fich>.enc`)? Justifique.

---

## Relatório de Implementação: `chacha20_int_attck.py`

### 📌 Objetivo

> O propósito do programa `chacha20_int_attck.py` é ilustrar como pode ser manipulada a informação cifrada pelo programa anterior -- se soubermos um fragmento do conteúdo de uma dada posição do texto-limpo, podemos alterar essa informação. O programa `chacha20_int_attck.py`deve então receber os seguintes argumentos: `<fctxt> <pos> <ptxtAtPos> <newPtxtAtPos>`, sendo que `<fctxt>` é o nome do ficheiro contendo o criptograma; `<pos>` é a posição onde sabemos ter sido cifrado `<ptxtAtPos>`, e `<newPtxtAtPos>` é o que se pretende vir a obter quando se decifrar o ficheiro. O criptograma manipulado deve ser gravado no ficheiro com nome `<fctxt>.attck`.

### 🛠️ Estrutura Lógica do Código

-

### 📊 Resultado

![]()

---

## Relatório de Implementação: `pbenc_chacha20.py`

### 📌 Objetivo

> Armazenar segredos cryptográficas em ficheiros sem estarem devidamente protegidas **é uma má prática**. Em vez disso, deve-se:
> 1. Derivar os segredos a partir de uma *pass-phrase* com recurso a uma [Key Derivation Functions (KDF)](https://cryptography.io/en/stable/hazmat/primitives/key-derivation-functions/#module-cryptography.hazmat.primitives.kdf) -- o que se designa por **Password-Based Encryption**, ou
> 2. Armazenar esses segredos em ficheiros devidamente protegidos (aka *keystore*), esta por sua vez construída recorrendo a *Password-Based Encryption* para a sua própria protecção.
>
> Pretende-se assim alterar o programa `cfich_chacha20.py` para suportar *Password-Based Encryption*. Deixa portanto de existir o comando para gerar uma nova chave, e as opções `enc` e `dec` deixam de receber o nome do ficheiro da chave como argumento. Em vez disso, leem de `stdin` a *pass-phrase* que permitirá derivar a chave usada na cifra. Sugere-se a utilização da KDF [`PBKDF2`](https://cryptography.io/en/stable/hazmat/primitives/key-derivation-functions/#cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC).

### 🛠️ Estrutura Lógica do Código

-

### 📊 Resultado

![]()
