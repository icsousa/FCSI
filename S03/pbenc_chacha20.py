import sys
import os
import struct
from getpass import getpass
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

def derive_key(passphrase, salt):
    """
    Deriva uma chave de 32 bytes a partir da passphrase e salt usando PBKDF2.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,  # número elevado de iterações para segurança
    )
    return kdf.derive(passphrase.encode())

def enc(fich):
    """
    Cifra o ficheiro usando uma passphrase lida do stdin e guarda como .enc.
    """
    passphrase = getpass("Introduza a passphrase: ")
    
    with open(fich, 'rb') as f:
        plaintext = f.read()
        
    counter = 0
    nonce = os.urandom(8)
    full_nonce = struct.pack("<Q", counter) + nonce
    salt = os.urandom(16)  # salt aleatório para PBKDF2

    key = derive_key(passphrase, salt)

    algorithm = algorithms.ChaCha20(key, full_nonce)
    cipher = Cipher(algorithm, mode=None)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext)
    
    out_filename = fich + ".enc"
    with open(out_filename, 'wb') as f:
        # Guardamos salt + full_nonce + ciphertext
        f.write(salt + full_nonce + ciphertext)
        
    print(f"Ficheiro cifrado com sucesso. Guardado como: {out_filename}")

def dec(fich):
    """
    Decifra o criptograma usando a passphrase lida do stdin e guarda como .dec.
    """
    passphrase = getpass("Introduza a passphrase: ")
    
    with open(fich, 'rb') as f:
        file_content = f.read()
        
    salt = file_content[:16]
    full_nonce = file_content[16:32]
    ciphertext = file_content[32:]
    
    key = derive_key(passphrase, salt)

    algorithm = algorithms.ChaCha20(key, full_nonce)
    cipher = Cipher(algorithm, mode=None)
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext)
    
    out_filename = fich + ".dec"
    with open(out_filename, 'wb') as f:
        f.write(plaintext)
        
    print(f"Ficheiro decifrado com sucesso. Guardado como: {out_filename}")

def main():
    if len(sys.argv) != 3:
        print("Usa: python3 pbenc_chacha20.py <operação> <ficheiro>")
        print("  enc <ficheiro>        # para cifrar, ex: mensagem.txt")
        print("  dec <ficheiro>        # para decifrar, ex: mensagem.txt.enc")
        sys.exit(1)

    op = sys.argv[1]
    fich = sys.argv[2]

    if op == "enc":
        enc(fich)
    elif op == "dec":
        dec(fich)
    else:
        print("Erro: Operação inválida.")

if __name__ == "__main__":
    main()