import sys

PT_FREQ = {
    'A': 14.63, 'E': 12.57, 'O': 10.73, 'S': 7.81, 'R': 6.53, 
    'I': 6.18, 'N': 5.05, 'D': 4.99, 'M': 4.74, 'U': 4.63, 
    'T': 4.34, 'C': 3.88, 'L': 2.78, 'P': 2.52, 'V': 1.67, 
    'G': 1.30, 'H': 1.28, 'Q': 1.20, 'B': 1.04, 'F': 1.02, 
    'Z': 0.47, 'J': 0.40, 'X': 0.21, 'K': 0.02, 'Y': 0.01, 'W': 0.01
}

def get_score(text):
    """
    Calcula o 'erro' estatístico (Chi-Square) comparando o texto
    com a frequência esperada do Português.
    """
    text_len = len(text)
    if text_len == 0: return float('inf')
    
    counts = {}
    for char in text:
        counts[char] = counts.get(char, 0) + 1
    
    score = 0.0
    for char_code in range(ord('A'), ord('Z') + 1):
        char = chr(char_code)
        observed = counts.get(char, 0)
        expected = PT_FREQ.get(char, 0) * text_len / 100.0
        if expected > 0:
            score += ((observed - expected) ** 2) / expected
    return score

def decrypt_caesar_char(char, key_char):
    if not char.isalpha(): return char
    c_val = ord(char) - ord('A')
    k_val = ord(key_char) - ord('A')
    p_val = (c_val - k_val) % 26
    return chr(p_val + ord('A'))

def solve_slice(text_slice):
    """
    Descobre a letra da chave mais provável para esta coluna.
    """
    best_char = 'A'
    min_score = float('inf')
    
    for k in range(26):
        key_char = chr(ord('A') + k)
        decrypted_slice = "".join([decrypt_caesar_char(c, key_char) for c in text_slice])
        current_score = get_score(decrypted_slice)
        
        if current_score < min_score:
            min_score = current_score
            best_char = key_char
    return best_char

def vigenere_decrypt(ciphertext, key):
    plaintext = []
    key_len = len(key)
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            k_char = key[i % key_len]
            plaintext.append(decrypt_caesar_char(char, k_char))
        else:
            plaintext.append(char)
    return "".join(plaintext)

def main():
    if len(sys.argv) < 4:
        print("Use: python3 vigenere_attack.py <tamanho_chave> <criptograma> <palavras...>")
        return

    try:
        key_len = int(sys.argv[1])
    except ValueError:
        print("Erro: O primeiro argumento deve ser o tamanho da chave (inteiro).")
        return

    ciphertext = sys.argv[2].upper()
    candidates = [w.upper() for w in sys.argv[3:]]
    
    clean_cipher = "".join([c for c in ciphertext if c.isalpha()])

    found_key_chars = []
    
    for i in range(key_len):
        slice_text = clean_cipher[i::key_len]
        
        best_char = solve_slice(slice_text)
        found_key_chars.append(best_char)
    
    candidate_key = "".join(found_key_chars)
    
    candidate_plaintext = vigenere_decrypt(ciphertext, candidate_key)
    
    found_match = False
    for word in candidates:
        if word in candidate_plaintext:
            found_match = True
            break
            
    if found_match:
        print(candidate_key)
        print(candidate_plaintext)
    else:
       pass 

if __name__ == "__main__":
    main()