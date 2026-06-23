import sys
import os
import random

def seed_expand(x):
    r = x
    for _ in range(14):
        y = x >> 8
        x ^= y
        r ^= x
        x = y
    return r

def my_prng(n):
    """ a ?SECURE? pseudo-random number generator """
    myseed = os.urandom(16)
    random.seed(seed_expand(int.from_bytes(myseed, byteorder='little')))
    return random.randbytes(n)

def xor_bytes(data, key):
    if len(key) < len(data):
        print(f"Erro: A chave (tamanho {len(key)}) é menor que a mensagem (tamanho {len(data)}).")
        sys.exit(1)
    
    return bytes([b ^ k for b, k in zip(data, key)])

def main():
    if len(sys.argv) < 2:
        print("Use: python otp.py <setup|enc|dec> [args...]")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "setup":
        if len(sys.argv) != 4:
            print("Use: python otp.py setup <num_bytes> <arquivo_chave>")
            sys.exit(1)
            
        try:
            num_bytes = int(sys.argv[2])
            key_filename = sys.argv[3]
            
            random_data = my_prng(num_bytes)
            
            with open(key_filename, "wb") as f:
                f.write(random_data)
            print(f"Gerada chave com {num_bytes} bytes em '{key_filename}'.")
            
        except ValueError:
            print("Erro: O número de bytes deve ser um inteiro.")

    elif mode == "enc":
        if len(sys.argv) != 4:
            print("Use: python otp.py enc <arquivo_msg> <arquivo_chave>")
            sys.exit(1)
            
        msg_filename = sys.argv[2]
        key_filename = sys.argv[3]
        
        try:
            with open(msg_filename, "rb") as f_msg:
                msg_data = f_msg.read()
            with open(key_filename, "rb") as f_key:
                key_data = f_key.read()
                
            encrypted_data = xor_bytes(msg_data, key_data)
            
            out_filename = msg_filename + ".enc"
            with open(out_filename, "wb") as f_out:
                f_out.write(encrypted_data)
            print(f"Mensagem cifrada salva em '{out_filename}'.")
            
        except FileNotFoundError:
            print("Erro: Arquivo não encontrado.")

    elif mode == "dec":
        if len(sys.argv) != 4:
            print("Use: python otp.py dec <arquivo_criptograma> <arquivo_chave>")
            sys.exit(1)
            
        cipher_filename = sys.argv[2]
        key_filename = sys.argv[3]
        
        try:
            with open(cipher_filename, "rb") as f_cipher:
                cipher_data = f_cipher.read()
            with open(key_filename, "rb") as f_key:
                key_data = f_key.read()
            
            decrypted_data = xor_bytes(cipher_data, key_data)
            
            out_filename = cipher_filename + ".dec"
            with open(out_filename, "wb") as f_out:
                f_out.write(decrypted_data)
            print(f"Mensagem decifrada salva em '{out_filename}'.")
            
        except FileNotFoundError:
            print("Erro: Arquivo não encontrado.")

    else:
        print("Modo desconhecido. Use setup, enc, ou dec.")

if __name__ == "__main__":
    main()