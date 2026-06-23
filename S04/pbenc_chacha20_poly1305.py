import sys
import os
import getpass
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag

def get_key(password: bytes, salt: bytes) -> bytes:
    """
    Deriva a chave a partir da password usando PBKDF2HMAC.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=20000,
    )
    return kdf.derive(password)

def main():
    if len(sys.argv) != 3:
        print("Uso: python3 pbenc_chacha20_poly1305.py <enc|dec> <ficheiro>")
        sys.exit(1)

    op = sys.argv[1]
    fich = sys.argv[2]
    aad = b"authenticated but unencrypted data"

    if op == "enc":
        # ler data
        with open(fich, 'rb') as f:
            data = f.read()

        # em vez de generate_key(), derivamos a chave da password
        password = getpass.getpass("Password: ").encode()
        salt = os.urandom(16)
        key = get_key(password, salt)

        # inicializar cifra e gerar nonce
        chacha = ChaCha20Poly1305(key)
        nonce = os.urandom(12)

        # cifrar
        ct = chacha.encrypt(nonce, data, aad)

        # guardar salt + nonce + ct no novo ficheiro
        with open(fich + ".enc", 'wb') as f:
            f.write(salt + nonce + ct)
        print(f"Cifrado com sucesso: {fich}.enc")

    elif op == "dec":
        # ler o ficheiro e dividir em partes
        with open(fich, 'rb') as f:
            content = f.read()
        
        salt = content[:16]
        nonce = content[16:28]
        ct = content[28:]

        # pedir a pass e derivar
        password = getpass.getpass("Password: ").encode()
        key = get_key(password, salt)

        # para inicializar
        chacha = ChaCha20Poly1305(key)

        # tentamos decifrar
        try:
            data = chacha.decrypt(nonce, ct, aad)
            
            # guardarmos
            with open(fich + ".dec", 'wb') as f:
                f.write(data)
            print(f"Decifrado com sucesso: {fich}.dec")
            
        except InvalidTag:
            print("ERRO: A autenticação falhou! Ficheiro corrompido, atacado ou password errada.")

if __name__ == "__main__":
    main()