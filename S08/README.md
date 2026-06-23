# 📝 Guião 4
## Relatório de Implementação: `pbenc_aes_ctr_hmac.py`

### 📌 Objetivo

> Defina o programa `pbenc_aes_ctr.py` que combine a utilização da cifra por blocos [`AES`](https://cryptography.io/en/stable/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.algorithms.AES) no modo [`CTR`](https://cryptography.io/en/stable/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.modes.CTR), com um **Código de Autenticação (MAC)** (e.g. [HMAC](https://cryptography.io/en/latest/hazmat/primitives/mac/hmac/)) segundo a estratégia **encrypt-then-MAC**.
>
> A chave deve ser derivada a partir de uma *passphrase** usando uma KDF apropriada.
>
> Note que irá precisar de uma nova chave simétrica para o MAC (__em criptografia, nunca se devem reutilizar chaves criptográficas para fins distintos__). Mas isso pode ser facilmente ultrapassado solicitando "mais bytes" à KDF utilizada para derivar a chave.


### 🛠️ Estrutura Lógica do Código

O programa `pbenc_aes_ctr_hmac.py` implementa cifra autenticada de ficheiros, garantindo:
* Confidencialidade (AES em modo CTR)
* Integridade e autenticidade (HMAC-SHA256)
* Derivação segura de chaves a partir de uma password (PBKDF2)

Segue a estratégia encrypt-then-MAC.

#### Argumentos:
* `enc <password> <ficheiro>`
* `dec <password> <ficheiro>`

##### `enc <password> <ficheiro>`
1. Deriva duas chaves (AES e HMAC) a partir da password.
2. Gera um salt e um nonce aleatórios.
3. Cifra o ficheiro com AES-CTR.
4. Depois de cifrar o ficheiro com AES-CTR, calcula-se um HMAC sobre os dados cifrados, `salt || nonce || ciphertext`.
5. O resultado é guardado num ficheiro com extensão .enc, `<ficheiro>.enc`.
6. O ficheiro final contém, por ordem: `| salt | nonce | ciphertext | tag(HMAC) |`, permitindo verificar a integridade antes da descifra.

##### `dec <password> <ficheiro>`
1. Lê o salt, nonce, ciphertext e tag.
2. Deriva novamente as mesmas chaves.
3. Recalcula o HMAC e verifica a integridade.
4. Se o MAC for válido, descifra com AES-CTR.
5. Guarda o ficheiro original (removendo .enc).
6. Se a verificação falhar, o programa termina sem descifrar.

#### Estrutura Lógica
* PBKDF2 → gera 64 bytes:
  * 32 bytes para AES
  * 32 bytes para HMAC
* AES-CTR → cifra simétrica
* HMAC-SHA256 → autenticação
* Verificação do MAC é feita antes da descifra

### 📊 Resultado

![1](1.png)

<sup> *Password: 123* </sup>

---

## Relatório de Implementação: `pbenc_chacha20_poly1305.py`

### 📌 Objetivo

> Adapte uma das soluções realizadas (baseada na cifra sequencial ou por blocos) para fazer uso de uma **cifras autenticada**. Pode considerar uma das seguintes primitivas de cifra autenticada: [ChaCha20Poly1305](https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305)

### 🛠️ Estrutura Lógica do Código

O programa `pbenc_chacha20_poly1305.py` garante **confidencialidade** e a **integridade** de ficheiros, utiliza uma abordagem baseada em *Password-Based Encryption* (PBE). 

A lógica do código divide-se em três blocos principais:

#### Derivação da Chave (`get_key`)
Como as chaves criptográficas não devem ser memorizadas por humanos, o programa pede uma *password* e utiliza a KDF (Key Derivation Function) **PBKDF2HMAC** com o algoritmo SHA-256. 
* O sistema aplica **20.000 iterações** e um ***Salt*** aleatório de 16 bytes. Isto atrasa propositadamente o processo para o computador, tornando ataques de força-bruta impraticáveis.

#### Operação de Cifra (`enc`)
O fluxo de cifra segue os seguintes passos:
1. Lê o conteúdo do ficheiro em texto limpo.
2. Pede a *password* ao utilizador e gera um *Salt* (16 bytes) e um *Nonce* (12 bytes) aleatórios.
3. Deriva a chave de 32 bytes e inicializa a primitiva `ChaCha20Poly1305`.
4. Ao invocar o método `encrypt()`, o algoritmo cifra os dados e gera automaticamente uma ***Tag* de autenticação** de 16 bytes (Poly1305), apensando-a ao final do criptograma.
5. O programa guarda os dados no ficheiro `.enc` com a seguinte estrutura linear:
   `[ Salt (16 bytes) | Nonce (12 bytes) | Criptograma | Tag (16 bytes) ]`

#### Operação de Decifra e Verificação (`dec`)
O fluxo de decifra atua também como validador de integridade:
1. Lê o ficheiro `.enc` e "fatia" os bytes exatos para recuperar o *Salt*, o *Nonce* e o Criptograma.
2. Deriva novamente a chave usando a *password* fornecida pelo utilizador e o *Salt* lido do ficheiro.
3. Inicializa o `ChaCha20Poly1305` e invoca o método `decrypt()`. 
4. **Mecanismo de Segurança:** Antes de libertar o texto limpo, o algoritmo recalcula o MAC (Tag) e compara-o com a Tag guardada no ficheiro. Se houver divergência (devido a password errada ou manipulação do ficheiro), é despoletada a exceção `InvalidTag`, impedindo que dados corrompidos sejam consumidos.

### 📊 Resultado

![2](2.png)

<sup> *Password: 1234* </sup>

---

>**QUESTÃO: Q1**
>* Qual será o impacto de executar o programa `chacha20_int_attck.py` sobre um criptograma produzido pelo seu programa? Justifique.

O ataque vai falhar.

Se usarmos o script de ataque da semana passada para trocar um bit no ficheiro .enc, o método `chacha.decrypt()` vai detetar imediatamente a adulteração. A tag de autenticação embutida deixará de corresponder ao criptograma manipulado, e o programa vai lançar a exceção `InvalidTag`, abortando a operação em vez de devolver texto corrompido. Esta é a grande vantagem da Cifra Autenticada.


---

## Relatório de Implementação: `cbc_mac.py` e `cbc_mac_rnd.py`

### 📌 Objetivo

> Escreva o programa `cbc_mac.py` que calcule o *tag* de autenticação CBC_MAC para uma dada mensagem. Esse programa deve aceitar como argumentos:
>
> - `tag <key> <file>` -- gera o *tag* de autenticação para o ficheiro <file>, e chave <key>. O resultado deve ser escrito no ficheiro `<file>.tag`;
> - `verify <key> <file> <tag>` -- verifica se <tag> é um código de autenticação válido para <file>. Se a verificação falhar, o programa deve despoletar a excepção `InvalidTag`.
> Ao contrário do modo CBC onde um IV aleatório deve ser use, o CBC-MAC adopta um IV fixo (bloco com zeros).
De facto, __esse aspecto é determinante para a sua segurança__, mas por forma a melhor percebermos o que está em jogo, vamos codificar uma versão com IV aleatório.
>
> Escreva o programa `cbc_mac_rnd.py` que adapte o cálculo do CBC-MAC para considerar um IV aleatório (i.e. o *tag* de autenticação passa a ser o par `IV/last-ctxt-block`).

### 🛠️ Estrutura Lógica do Código

**`cbc_mac.py`**:
- Este programa implementa o funcionamento clássico do algoritmo CBC-MAC utilizando a cifra AES. A sua característica principal é o uso de um Vetor de Inicialização (IV) fixo, preenchido inteiramente com zeros. O ficheiro é cifrado e o programa extrai apenas o último bloco resultante (16 bytes), que funciona como a assinatura (MAC) que garante a integridade dos dados.

**`cbc_mac_rnd.py`**: 
- Esta versão adapta o cálculo anterior, substituindo o bloco de zeros por um Vetor de Inicialização (IV) gerado de forma aleatória a cada execução. Como o IV é imprevisível, o programa anexa-o publicamente ao último bloco cifrado para que o recetor consiga fazer a verificação. A assinatura final resulta na junção destas duas partes (totalizando 32 bytes).

### 📊 Resultado

![3](3.png)

![4](4.png)

---

>**QUESTÃO: Q2**
>* Um ataque a um MAC consiste em, após ter acesso pares de *mensagem/tag* válidos, 
conseguir produzir um novo par *msg/tag* válido sem conhecer a chave respectiva.
Mostre como é possível atacar a versão do MAC que inclui o vector aleatório.


Um ataque a um MAC procura gerar um novo par `(mensagem, tag)` válido sem conhecer a chave, apenas com acesso a pares válidos.

Se o MAC inclui um vetor aleatório (`nonce` ou `IV`) que é enviado em claro, ele deixa de depender apenas da chave e da mensagem. Um atacante, ao conhecer vários pares `(nonce || mensagem, tag)`, pode manipular ou combinar nonces e mensagens anteriores para criar um novo par `(nonce', mensagem')` que produz uma tag válida, explorando a previsibilidade ou linearidade da função MAC.

Portanto, incluir um vetor aleatório no cálculo do MAC não garante segurança adicional e permite ataques, porque o nonce público pode ser usado para enganar o MAC. Por isso, a prática segura é calcular o MAC apenas sobre os dados cifrados e com a chave secreta, como no método encrypt-then-MAC.
