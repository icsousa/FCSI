import sys
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

class InvalidTag(Exception):
    pass

def cbc_mac_generate(key, data):
    # IV fixo (bloco com zeros)
    iv = b'\x00' * 16
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    
    # aplicação de padding PKCS7
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    # cifragem
    ctxt = encryptor.update(padded_data) + encryptor.finalize()
    
    # MAC é o último bloco (16 bytes)
    return ctxt[-16:]

def main():
    if len(sys.argv) < 4:
        print("Uso:")
        print("  python cbc_mac.py tag <key_hex> <file>")
        print("  python cbc_mac.py verify <key_hex> <file> <tag_file>")
        sys.exit(1)

    command = sys.argv[1]
    key = bytes.fromhex(sys.argv[2])
    filename = sys.argv[3]

    with open(filename, 'rb') as f:
        data = f.read()

    if command == "tag":
        tag = cbc_mac_generate(key, data)
        tag_filename = f"{filename}.tag"
        with open(tag_filename, 'wb') as f:
            f.write(tag)
        print(f"Tag gerado com sucesso e guardado em {tag_filename}")

    elif command == "verify":
        if len(sys.argv) != 5:
            print("Erro: Falta o argumento do ficheiro de tag.")
            sys.exit(1)
        
        tag_filename = sys.argv[4]
        with open(tag_filename, 'rb') as f:
            provided_tag = f.read()
            
        expected_tag = cbc_mac_generate(key, data)
        
        if provided_tag == expected_tag:
            print("Verificação com sucesso: A tag é VÁLIDA.")
        else:
            raise InvalidTag("A tag fornecida é INVÁLIDA.")

if __name__ == "__main__":
    main()