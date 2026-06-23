import sys
import os
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def setup(fkey):
    """
    Gera uma chave de 32 bytes e guarda no ficheiro fkey.
    """
    key = os.urandom(32)
    with open(fkey, 'wb') as f:
        f.write(key)
    print(f"Chave gerada e guardada em: {fkey}")

def enc(fich, fkey):
    """
    Cifra o ficheiro usando a chave lida de fkey e guarda como .enc.
    """
    with open(fkey, 'rb') as f:
        key = f.read()
    
    with open(fich, 'rb') as f:
        plaintext = f.read()
        
    counter = 0
    nonce = os.urandom(8)
    full_nonce = struct.pack("<Q", counter) + nonce
    
    algorithm = algorithms.ChaCha20(key, full_nonce)
    cipher = Cipher(algorithm, mode=None)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext)
    
    out_filename = fich + ".enc"
    with open(out_filename, 'wb') as f:
        f.write(full_nonce + ciphertext)
        
    print(f"Ficheiro cifrado com sucesso. Guardado como: {out_filename}")

def dec(fich, fkey):
    """
    Decifra o criptograma e guarda como .dec.
    """
    with open(fkey, 'rb') as f:
        key = f.read()
        
    with open(fich, 'rb') as f:
        file_content = f.read()
        
    full_nonce = file_content[:16]
    ciphertext = file_content[16:]
    
    algorithm = algorithms.ChaCha20(key, full_nonce)
    cipher = Cipher(algorithm, mode=None)
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext)
    
    out_filename = fich + ".dec"
    with open(out_filename, 'wb') as f:
        f.write(plaintext)
        
    print(f"Ficheiro decifrado com sucesso. Guardado como: {out_filename}")

def main():
    if len(sys.argv) < 3:
        print("Use: python3 cfich_chacha20.py <operação> <argumentos...>")
        print("  setup <fkey>")
        print("  enc <fich> <fkey>")
        print("  dec <fich> <fkey>")
        sys.exit(1)

    op = sys.argv[1]

    if op == "setup" and len(sys.argv) == 3:
        setup(sys.argv[2])
    elif op == "enc" and len(sys.argv) == 4:
        enc(sys.argv[2], sys.argv[3])
    elif op == "dec" and len(sys.argv) == 4:
        dec(sys.argv[2], sys.argv[3])
    else:
        print("Erro: Número de argumentos inválido para a operação solicitada.")

if __name__ == "__main__":
    main()