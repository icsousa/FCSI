import sys
import os

def main(inp):
    """ 
    Função que emula uma versão simplificada do comando wc do Unix.
    Conta linhas, palavras e caracteres de um ficheiro.
    """
    
    # Valida se foi passado o argumento do nome do ficheiro
    # inp[0] é o nome do script, inp[1] deve ser o ficheiro
    if len(inp) < 2:
        print("Erro: Indique o nome do ficheiro.")
        print("Exemplo: python wc.py exemplo.txt")
        return

    file_path = inp[1]

    try:
        # Abre o ficheiro em modo de leitura de texto (utf-8)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Contagem de linhas
            # O método splitlines divide o conteúdo por quebras de linha
            # Nota: 'wc' unix conta '\n', mas para versão simplificada splitlines é adequado.
            lines_list = content.splitlines()
            num_lines = len(lines_list)
            
            # Se o ficheiro terminar com uma quebra de linha e estiver vazio depois,
            # o splitlines pode variar, mas geralmente esta contagem é a esperada em exercícios.
            # Alternativa estrita: num_lines = content.count('\n')

            # Contagem de palavras
            # O método split() sem argumentos divide por qualquer espaço em branco (espaço, tab, enter)
            words_list = content.split()
            num_words = len(words_list)

            # Contagem de caracteres
            num_chars = len(content)

            # Impressão formatada para alinhar à direita (similar ao exemplo dado: 580    3518   21268)
            # Utiliza-se f-strings com largura fixa (ex: :8) para emular as colunas
            print(f"{num_chars:8} {num_words:8} {num_lines:8}")

    except FileNotFoundError:
        print(f"Erro: O ficheiro '{file_path}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao processar o ficheiro: {e}")

# Se for chamada como script...
if __name__ == "__main__":
    main(sys.argv)