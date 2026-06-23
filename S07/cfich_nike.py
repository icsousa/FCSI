import sys
import os
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

P_HEX = "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF"
p = int(P_HEX, 16)
g = 2

def mkpair(x, y):
    """ Produz uma byte-string contendo o tuplo '(x,y)' ('x' e 'y' são byte-strings) """
    len_x = len(x)
    len_x_bytes = len_x.to_bytes(2, 'little')
    return len_x_bytes + x + y

def unpair(xy):
    """ Extrai componentes de um par codificado com 'mkpair' """
    len_x = int.from_bytes(xy[:2], 'little')
    x = xy[2:len_x+2]
    y = xy[len_x+2:]
    return x, y

def get_dh_parameters():
    """ Retorna o objeto DHParameters usando os valores p e g """
    pn = dh.DHParameterNumbers(p, g)
    return pn.parameters()

def derive_session_key(shared_secret):
    """ Usa o HKDF para transformar o segredo DH numa chave AES de 32 bytes """
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'nike-file-encryption'
    ).derive(shared_secret)

def setup(user):
    print(f"A gerar chaves para o utilizador '{user}'...")
    params = get_dh_parameters()
    sk = params.generate_private_key()
    pk = sk.public_key()

    # gravar a chave privada PEM
    with open(f"{user}.sk", "wb") as f:
        f.write(sk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # gravar a chave pública PEM
    with open(f"{user}.pk", "wb") as f:
        f.write(pk.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    
    print(f"Ficheiros gerados: {user}.sk e {user}.pk")

def enc(user, filename):
    # aceder à chave pública de Bob
    try:
        with open(f"{user}.pk", "rb") as f:
            pkBob = serialization.load_pem_public_key(f.read())
    except FileNotFoundError:
        print(f"Erro: Não foi possível encontrar a chave pública de '{user}' ({user}.pk).")
        sys.exit(1)

    # gerar chaves (skAlice, pkAlice)
    params = get_dh_parameters()
    skAlice = params.generate_private_key()
    pkAlice = skAlice.public_key()

    # derivar chave de sessão K
    shared_secret = skAlice.exchange(pkBob)
    k = derive_session_key(shared_secret)

    # cifrar mensagme em AES-GCM requer um nonce de 12 bytes
    try:
        with open(filename, "rb") as f:
            msg = f.read()
    except FileNotFoundError:
        print(f"Erro: O ficheiro '{filename}' não existe.")
        sys.exit(1)

    aesgcm = AESGCM(k)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, msg, None)

    # gravar em DER para pkAlice
    pkAlice_bytes = pkAlice.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # criptograma inclui o nonce + ciphertext
    cryptogram_data = nonce + ciphertext
    final_payload = mkpair(pkAlice_bytes, cryptogram_data)

    out_filename = filename + ".enc"
    with open(out_filename, "wb") as f:
        f.write(final_payload)
    
    print(f"Ficheiro cifrado gravado com sucesso: {out_filename}")

def dec(user, filename):
    # carregar chave privada de Bob
    try:
        with open(f"{user}.sk", "rb") as f:
            skBob = serialization.load_pem_private_key(f.read(), password=None)
    except FileNotFoundError:
        print(f"Erro: Não foi possível encontrar a chave privada de '{user}' ({user}.sk).")
        sys.exit(1)

    # ler o ficheiro cifrado
    try:
        with open(filename, "rb") as f:
            payload = f.read()
    except FileNotFoundError:
        print(f"Erro: O ficheiro '{filename}' não existe.")
        sys.exit(1)

    # extrair pkAlice e o criptograma
    pkAlice_bytes, cryptogram_data = unpair(payload)

    # desserializar pkAlice (foi gravada em DER)
    pkAlice = serialization.load_der_public_key(pkAlice_bytes)

    # derivar chave de sessão K
    shared_secret = skBob.exchange(pkAlice)
    k = derive_session_key(shared_secret)

    # decifrar
    nonce = cryptogram_data[:12]
    ciphertext = cryptogram_data[12:]
    
    aesgcm = AESGCM(k)
    try:
        cleartext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        print("Erro Crítico: Falha na autenticação (cifra adulterada ou chaves erradas).")
        sys.exit(1)

    # guardar ficheiro decifrado
    if filename.endswith(".enc"):
        out_filename = filename[:-4] + ".dec"
    else:
        out_filename = filename + ".dec"

    with open(out_filename, "wb") as f:
        f.write(cleartext)
    
    print(f"Ficheiro decifrado com sucesso: {out_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso:")
        print("  python cfich_nike.py setup <user>")
        print("  python cfich_nike.py enc <user> <fich>")
        print("  python cfich_nike.py dec <user> <fich>")
        sys.exit(1)

    op = sys.argv[1]
    user = sys.argv[2]

    if op == "setup":
        setup(user)
    elif op == "enc":
        if len(sys.argv) != 4:
            print("Erro: Falta indicar o ficheiro a cifrar.")
            sys.exit(1)
        enc(user, sys.argv[3])
    elif op == "dec":
        if len(sys.argv) != 4:
            print("Erro: Falta indicar o ficheiro a decifrar.")
            sys.exit(1)
        dec(user, sys.argv[3])
    else:
        print("Erro: Operação desconhecida. Use 'setup', 'enc' ou 'dec'.")