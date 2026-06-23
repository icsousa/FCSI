import sys
import os
from cryptography.hazmat.primitives.asymmetric import dh, rsa, padding
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
    
    rsa_sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    rsa_pk = rsa_sk.public_key()
    
    with open(f"{user}.rsask", "wb") as f:
        f.write(rsa_sk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(f"{user}.rsapk", "wb") as f:
        f.write(rsa_pk.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    params = get_dh_parameters()
    dh_sk = params.generate_private_key()
    dh_pk = dh_sk.public_key()
    
    with open(f"{user}.dhsk", "wb") as f:
        f.write(dh_sk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    dh_pk_bytes = dh_pk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    signature = rsa_sk.sign(
        dh_pk_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    with open(f"{user}.dhpk", "wb") as f:
        f.write(mkpair(dh_pk_bytes, signature))
    
    print(f"Ficheiros gerados: {user}.dhsk, {user}.dhpk, {user}.rsask e {user}.rsapk")

def enc(user, me, filename):
    try:
        with open(f"{user}.rsapk", "rb") as f:
            rsa_pk_bob = serialization.load_pem_public_key(f.read())
            
        with open(f"{user}.dhpk", "rb") as f:
            dhpk_payload = f.read()
    except FileNotFoundError:
        print(f"Erro: Faltam chaves públicas de '{user}'. Corre o setup para este utilizador.")
        sys.exit(1)
        
    dh_pk_bob_bytes, signature_bob = unpair(dhpk_payload)
    
    try:
        rsa_pk_bob.verify(
            signature_bob, dh_pk_bob_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
    except Exception:
        print(f"Erro: Assinatura da chave DH do destinatário '{user}' é inválida.")
        sys.exit(1)
        
    dh_pk_bob = serialization.load_pem_public_key(dh_pk_bob_bytes)

    try:
        with open(f"{me}.rsask", "rb") as f:
            rsa_sk_alice = serialization.load_pem_private_key(f.read(), password=None)
    except FileNotFoundError:
        print(f"Erro: Não foi possível encontrar a chave privada de '{me}' ({me}.rsask).")
        sys.exit(1)

    try:
        with open(filename, "rb") as f:
            msg = f.read()
    except FileNotFoundError:
        print(f"Erro: O ficheiro '{filename}' não existe.")
        sys.exit(1)

    signature_msg = rsa_sk_alice.sign(
        msg,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    
    payload_to_encrypt = mkpair(signature_msg, msg)

    params = get_dh_parameters()
    ephemeral_dh_sk_alice = params.generate_private_key()
    ephemeral_dh_pk_alice = ephemeral_dh_sk_alice.public_key()
    
    shared_secret = ephemeral_dh_sk_alice.exchange(dh_pk_bob)
    k = derive_session_key(shared_secret)

    aesgcm = AESGCM(k)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, payload_to_encrypt, None)

    ephemeral_dh_pk_alice_bytes = ephemeral_dh_pk_alice.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    cryptogram_data = nonce + ciphertext
    final_payload = mkpair(ephemeral_dh_pk_alice_bytes, cryptogram_data)

    out_filename = filename + ".enc"
    with open(out_filename, "wb") as f:
        f.write(final_payload)
    
    print(f"Ficheiro cifrado gravado com sucesso: {out_filename}")

def dec(me, user, filename):
    try:
        with open(f"{me}.dhsk", "rb") as f:
            dh_sk_bob = serialization.load_pem_private_key(f.read(), password=None)
    except FileNotFoundError:
        print(f"Erro: Não foi possível encontrar a chave privada de '{me}' ({me}.dhsk).")
        sys.exit(1)

    try:
        with open(f"{user}.rsapk", "rb") as f:
            rsa_pk_alice = serialization.load_pem_public_key(f.read())
    except FileNotFoundError:
        print(f"Erro: Não foi possível encontrar a chave pública de '{user}' ({user}.rsapk).")
        sys.exit(1)

    try:
        with open(filename, "rb") as f:
            payload = f.read()
    except FileNotFoundError:
        print(f"Erro: O ficheiro '{filename}' não existe.")
        sys.exit(1)

    ephemeral_dh_pk_alice_bytes, cryptogram_data = unpair(payload)
    ephemeral_dh_pk_alice = serialization.load_pem_public_key(ephemeral_dh_pk_alice_bytes)

    shared_secret = dh_sk_bob.exchange(ephemeral_dh_pk_alice)
    k = derive_session_key(shared_secret)

    nonce = cryptogram_data[:12]
    ciphertext = cryptogram_data[12:]
    
    aesgcm = AESGCM(k)
    try:
        decrypted_payload = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception:
        print("Erro: Falha na autenticação.")
        sys.exit(1)

    signature_msg, msg = unpair(decrypted_payload)
    
    try:
        rsa_pk_alice.verify(
            signature_msg, msg,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
    except Exception:
        print("Erro: Falha na validação da assinatura RSA do remetente.")
        sys.exit(1)

    if filename.endswith(".enc"):
        out_filename = filename[:-4] + ".dec"
    else:
        out_filename = filename + ".dec"

    with open(out_filename, "wb") as f:
        f.write(msg)
    
    print(f"Ficheiro decifrado com sucesso e autenticidade validada: {out_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso:")
        print("  python cfich_nikesig.py setup <user>")
        print("  python cfich_nikesig.py enc <user> <me> <fich>")
        print("  python cfich_nikesig.py dec <me> <user> <fich>")
        sys.exit(1)

    op = sys.argv[1]

    if op == "setup":
        if len(sys.argv) != 3:
             print("Uso: python cfich_nikesig.py setup <user>")
             sys.exit(1)
        setup(sys.argv[2])
    elif op == "enc":
        if len(sys.argv) != 5:
            print("Uso: python cfich_nikesig.py enc <user> <me> <fich>")
            sys.exit(1)
        enc(sys.argv[2], sys.argv[3], sys.argv[4])
    elif op == "dec":
        if len(sys.argv) != 5:
            print("Uso: python cfich_nikesig.py dec <me> <user> <fich>")
            sys.exit(1)
        dec(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Erro: Operação desconhecida. Use 'setup', 'enc' ou 'dec'.")