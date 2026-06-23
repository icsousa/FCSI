import sys

def cesar_attack():
    cifra = sys.argv[1]
    candidates = [word.upper() for word in sys.argv[2:]]

    for shift in range(26):
        current_key_char = chr(ord('A') + shift)
        
        plaintext_chars = []
        for char in cifra:
            if char.isalpha():
                curr_val = ord(char.upper()) - ord('A')
                plain_val = (curr_val - shift) % 26
                plaintext_chars.append(chr(plain_val + ord('A')))

            else:
                plaintext_chars.append(char)
        
        candidate_plaintext = "".join(plaintext_chars)

        found = False
        for word in candidates:
            if word in candidate_plaintext:
                found = True
                break
        
        if found:
            # print("A palavra encontrada foi: " + word)
            print(current_key_char)
            print(candidate_plaintext)
            return

if __name__ == "__main__":
    cesar_attack()
