import sys
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

class InvalidTag(Exception):
    pass

def cbc_mac_rnd_generate(key, data):
    # IV Aleatório
    iv = os.urandom(16)
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    ctxt = encryptor.update(padded_data) + encryptor.finalize()
    
    last_block = ctxt[-16:]
    # MAC agora é o par (IV, last-ctxt-block) concatenado
    return iv + last_block

def cbc_mac_rnd_verify(key, data, provided_mac):
    # separa o IV do último bloco
    iv = provided_mac[:16]
    expected_last_block = provided_mac[16:]
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    ctxt = encryptor.update(padded_data) + encryptor.finalize()
    calculated_last_block = ctxt[-16:]
    
    return expected_last_block == calculated_last_block

def main():
    if len(sys.argv) < 4:
        print("Uso:")
        print("  python cbc_mac_rnd.py tag <key_hex> <file>")
        print("  python cbc_mac_rnd.py verify <key_hex> <file> <tag_file>")
        sys.exit(1)

    command = sys.argv[1]
    key = bytes.fromhex(sys.argv[2])
    filename = sys.argv[3]

    with open(filename, 'rb') as f:
        data = f.read()

    if command == "tag":
        mac = cbc_mac_rnd_generate(key, data)
        tag_filename = f"{filename}.tag"
        with open(tag_filename, 'wb') as f:
            f.write(mac)
        print(f"Tag (com IV aleatório) gerado e guardado em {tag_filename}")

    elif command == "verify":
        if len(sys.argv) != 5:
            print("Erro: Falta o argumento do ficheiro de tag.")
            sys.exit(1)
        
        tag_filename = sys.argv[4]
        with open(tag_filename, 'rb') as f:
            provided_mac = f.read()
            
        if cbc_mac_rnd_verify(key, data, provided_mac):
            print("Verificação com sucesso: A tag é VÁLIDA.")
        else:
            raise InvalidTag("A tag fornecida é INVÁLIDA.")

if __name__ == "__main__":
    main()
