import sys

def preproc(str):
    l = []
    for c in str:
      if c.isalpha():
        l.append(c.upper())
    return "".join(l)  

def cesar(op, key, str):
    deslocamento = ord(key.upper()) - ord('A')
    result = []
    message = preproc(str)

    for char in message:
        char_idx = ord(char) - ord('A')
        
        if op == 'enc':
            new_idx = (char_idx + deslocamento) % 26
        elif op == 'dec':
            new_idx = (char_idx - deslocamento) % 26
        else:
            print("Operação inválida. Use 'enc' ou 'dec'.")
            sys.exit(1)
            
        new_char = chr(new_idx + ord('A'))
        result.append(new_char)
        
    return "".join(result)
    
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Use: python3 cesar.py <enc|dec> <chave> <mensagem>")
        sys.exit(1)

    operacao = sys.argv[1]   
    chave = sys.argv[2]      
    mensagem = sys.argv[3] 
    
    resultado = cesar(operacao, chave, mensagem)
    
    print(resultado)