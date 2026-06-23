# 📝 Guião 1
## Relatório de Implementação: `wc.py`

### 📌 Objetivo
"Para testar o ambiente de desenvolvimento e a instalação do `Python`, escreva um pequeno programa `wc.py` que emule uma versão simplificada do comando `wc` do *Unix*, que conta o número de linhas, palavras e caracteres de um ficheiro passado como argumento."

### 🛠️ Estrutura Lógica do Código
A implementação segue o template sugerido, preservando a estrutura da função main(inp) e a utilização de sys.argv para capturar os argumentos da linha de comando.

#### Tratamento de Argumentos
O script verifica a lista de argumentos `sys.argv`.
O índice `0` da lista contém o nome do script `wc.py`, enquanto o índice `1` deve conter o caminho do ficheiro alvo. Foi implementada uma verificação de segurança (`if len(inp) < 2`) para garantir que o utilizador forneceu o nome do ficheiro.

#### Leitura e Processamento do Ficheiro
O ficheiro é aberto em modo de leitura de texto (`'r'`) com codificação `utf-8` para garantir a correta interpretação de caracteres.

- **Contagem de Linhas**: `content.splitlines()`
  
  O conteúdo total do ficheiro é dividido numa lista sempre que ocorre uma quebra de linha. O número total de linhas corresponde ao tamanho (`len`) desta lista.

- **Contagem de Palavras**: `content.split()`

  O método `split()` sem argumentos separa o texto sempre que encontra "espaços em branco" (espaços, tabs ou `\n`). O tamanho da lista resultante equivale ao número de palavras.

- **Contagem de Caracteres**: `len(content)`

  Contabiliza o comprimento total da string lida do ficheiro, incluindo espaços e caracteres especiais.

#### Formatação de Saída (Output)
Foram utilizadas *f-strings* com formatação de largura fixa (ex: `{var:8}`) para alinhar os números à direita, criando colunas visuais organizadas sem a necessidade de bibliotecas externas complexas.

#### Tratamento de Erros
Incluímos um bloco `try...except`:
1. **FileNotFoundError**: Captura o erro específico caso o ficheiro indicado não exista.
2. **Exception Genérica**: Captura outros erros de leitura.
