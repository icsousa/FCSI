import sys
import os
import datetime
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def cert_load(fname):
    with open(fname, "rb") as fcert:
        cert = x509.load_pem_x509_certificate(fcert.read())
    return cert

def cert_validtime(cert, now=None):
    if now is None:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
    if now < cert.not_valid_before_utc or now > cert.not_valid_after_utc:
        raise x509.verification.VerificationError("Certificate is not valid at this time")

def cert_validsubject(cert, attrs=[]):
    for attr in attrs:
        val_no_cert = cert.subject.get_attributes_for_oid(attr[0])[0].value
        if attr[1] not in val_no_cert:
            raise x509.verification.VerificationError(f"Certificate subject does not match expected value")

def valida_cert_final(nome_user, ca_cert):
    try:
        cert = cert_load(f"{nome_user}.crt")
        cert.verify_directly_issued_by(ca_cert)
        cert_validtime(cert)
        cert_validsubject(cert, [(x509.NameOID.COMMON_NAME, nome_user)])
        print(f"-> Certificado de {nome_user} validado com sucesso.")
        return cert.public_key()
    except Exception as e:
        print(f"ERRO DE VALIDAÇÃO ({nome_user}.crt): {e}")
        return None

def mkpair(x, y):
    return len(x).to_bytes(2, 'little') + x + y

def unpair(xy):
    len_x = int.from_bytes(xy[:2], 'little')
    return xy[2:len_x+2], xy[len_x+2:]

def enc(user, me, filename):
    try:
        ca = cert_load("CA.crt")
        pk_recip = valida_cert_final(user, ca) 
        if not pk_recip: return

        with open(f"{me}.key", "rb") as f:
            sk_me = serialization.load_pem_private_key(f.read(), password=b"1234")
        
        with open(filename, "rb") as f:
            msg = f.read()

        sig = sk_me.sign(msg, padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.MAX_LENGTH), hashes.SHA256())
        
        session_key = os.urandom(32)
        aes = AESGCM(session_key)
        nonce = os.urandom(12)
        ciphertext = aes.encrypt(nonce, mkpair(sig, msg), None)
        enc_session_key = pk_recip.encrypt(session_key, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

        with open(filename + ".enc", "wb") as f:
            f.write(mkpair(enc_session_key, nonce + ciphertext))
        print(f"Ficheiro {filename}.enc gerado com sucesso.")
    except Exception as e: 
        print(f"Erro no enc: {e}")

def dec(me, user, filename):
    try:
        ca = cert_load("CA.crt")
        pk_sender = valida_cert_final(user, ca) 
        if not pk_sender: return

        with open(f"{me}.key", "rb") as f:
            sk_me = serialization.load_pem_private_key(f.read(), password=b"1234")

        with open(filename, "rb") as f:
            enc_key, cryptogram = unpair(f.read())
        
        session_key = sk_me.decrypt(enc_key, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        aes = AESGCM(session_key)
        pt = aes.decrypt(cryptogram[:12], cryptogram[12:], None)
        sig, msg = unpair(pt)

        pk_sender.verify(sig, msg, padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.MAX_LENGTH), hashes.SHA256())
        
        out = filename.replace(".enc", ".dec")
        with open(out, "wb") as f: f.write(msg)
        print(f"Sucesso: Assinatura de {user} VÁLIDA. Ficheiro restaurado em {out}.")
    except Exception as e: 
        print(f"ERRO NA ASSINATURA OU DECIFRAÇÃO: {e}")

def usage():
    print("\n")
    print("  COMO EXECUTAR O PROGRAMA (cfich_certs.py)")
    print("\n")
    print("1. CIFRAR E ASSINAR (Alice envia para Bob):")
    print("   python cfich_certs.py enc BOB ALICE exemplo.txt")
    print("\n2. DECIFRAR E VERIFICAR (Bob recebe de Alice):")
    print("   python cfich_certs.py dec BOB ALICE exemplo.txt.enc")
    print("\n")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        usage()
    else:
        op = sys.argv[1]
        if op == "enc":
            enc(sys.argv[2], sys.argv[3], sys.argv[4])
        elif op == "dec":
            dec(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            usage()