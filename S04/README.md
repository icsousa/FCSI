# 📝 Guião 4
## Relatório de Implementação: `pbenc_aes_ctr_hmac.py`

### 📌 Objetivo

> Defina o programa `pbenc_aes_ctr.py` que combine a utilização da cifra por blocos [`AES`](https://cryptography.io/en/stable/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.algorithms.AES) no modo [`CTR`](https://cryptography.io/en/stable/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.modes.CTR), com um **Código de Autenticação (MAC)** (e.g. [HMAC](https://cryptography.io/en/latest/hazmat/primitives/mac/hmac/)) segundo a estratégia **encrypt-then-MAC**.
>
> A chave deve ser derivada a partir de uma *passphrase** usando uma KDF apropriada.
>
> Note que irá precisar de uma nova chave simétrica para o MAC (__em criptografia, nunca se devem reutilizar chaves criptográficas para fins distintos__). Mas isso pode ser facilmente ultrapassado solicitando "mais bytes" à KDF utilizada para derivar a chave.


### 🛠️ Estrutura Lógica do Código

-

### 📊 Resultado

![]()

---

## Relatório de Implementação: `pbenc_chacha20_poly1305.py`

### 📌 Objetivo

> Adapte uma das soluções realizadas (baseada na cifra sequencial ou por blocos) para fazer uso de uma **cifras autenticada**. Pode considerar uma das seguintes primitivas de cifra autenticada: [ChaCha20Poly1305](https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305)

### 🛠️ Estrutura Lógica do Código

-

### 📊 Resultado

![]()

---

>**QUESTÃO: Q1**
>* Qual será o impacto de executar o programa `chacha20_int_attck.py` sobre um criptograma produzido pelo seu programa? Justifique.



---

## Relatório de Implementação: `cbc_mac_rnd.py`

### 📌 Objetivo

> Ao contrário do modo CBC onde um IV aleatório deve ser use, o CBC-MAC adopta um IV fixo (bloco com zeros).
De facto, __esse aspecto é determinante para a sua segurança__, mas por forma a melhor percebermos o que está em jogo, vamos codificar uma versão com IV aleatório.
>
> Escreva o programa `cbc_mac_rnd.py` que adapte o cálculo do CBC-MAC para considerar um IV aleatório (i.e. o *tag* de autenticação passa a ser o par `IV/last-ctxt-block`).

### 🛠️ Estrutura Lógica do Código

-

### 📊 Resultado

![]()

---

>**QUESTÃO: Q2**
>* Um ataque a um MAC consiste em, após ter acesso pares de *mensagem/tag* válidos, 
conseguir produzir um novo par *msg/tag* válido sem conhecer a chave respectiva.
Mostre como é possível atacar a versão do MAC que inclui o vector aleatório.