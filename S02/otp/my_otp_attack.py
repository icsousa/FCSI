import sys
import random

def seed_expand(x):
    r = x
    for _ in range(14):
        y = x >> 8
        x ^= y
        r ^= x
        x = y
    return r

def xor_bytes(data, key):
    return bytes([b ^ k for b, k in zip(data, key)])

def my_otp_attack():
    if len(sys.argv) < 3:
        print("Use: python3 my_otp_attack.py <arquivo_criptograma> <palavra1> [palavra2 ...]")
        return

    cipher_filename = sys.argv[1]
    candidates = [w.upper() for w in sys.argv[2:]]

    try:
        with open(cipher_filename, "rb") as f:
            cipher_data = f.read()
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")
        return

    msg_len = len(cipher_data)

    for i in range(65536):
        expanded_seed = seed_expand(i)
        random.seed(expanded_seed)
        
        keystream = random.randbytes(msg_len)

        plaintext_bytes = xor_bytes(cipher_data, keystream)
        try:
            plaintext = plaintext_bytes.decode('utf-8', errors='ignore')
            plaintext_upper = plaintext.upper()

            for word in candidates:
                if word in plaintext_upper:
                    print(plaintext)
                    return 

        except Exception:
            continue

    print("\nNenhuma chave encontrada com as palavras fornecidas.")

if __name__ == "__main__":
    my_otp_attack()