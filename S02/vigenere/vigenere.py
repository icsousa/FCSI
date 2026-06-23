import sys

def preproc(str):
    l = []
    for c in str:
      if c.isalpha():
        l.append(c.upper())
    return "".join(l)  

def vigenere(op, key, str):
    n = 0
    skip = []
    for c in key:
        skip.append(ord(c.upper()) - ord('A'))
    
    result = []
    message = preproc(str)

    for char in message:
        char_idx = ord(char) - ord('A')
        
        if op == 'enc':
            idx = n % len(skip)
            new_idx = (char_idx + skip[idx]) % 26
            n += 1
        elif op == 'dec':
            idx = n % len(skip)
            new_idx = (char_idx - skip[idx]) % 26
            n += 1
        else:
            print("Operação inválida. Use 'enc' ou 'dec'.")
            sys.exit(1)
            
        new_char = chr(new_idx + ord('A'))
        result.append(new_char)
        
    return "".join(result)
    
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Use: python3 vigenere.py <enc|dec> <chave> <mensagem>")
        sys.exit(1)

    operacao = sys.argv[1]   
    chave = sys.argv[2]      
    mensagem = sys.argv[3] 
    
    resultado = vigenere(operacao, chave, mensagem)
    
    print(resultado)