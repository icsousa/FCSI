import sys

def xor_bytes(b1, b2, b3):
    """
    Faz o XOR byte a byte entre 3 sequências de bytes.
    """
    return bytes(x ^ y ^ z for x, y, z in zip(b1, b2, b3))

def main():
    if len(sys.argv) != 5:
        print("Use: python3 chacha20_int_attck.py <fctxt> <pos> <ptxtAtPos> <newPtxtAtPos>")
        sys.exit(1)

    fctxt = sys.argv[1]
    pos = int(sys.argv[2]) + 16
    ptxtAtPos = sys.argv[3].encode('utf-8')
    newPtxtAtPos = sys.argv[4].encode('utf-8')

    file_pos = pos + 16

    length = min(len(ptxtAtPos), len(newPtxtAtPos)) 
    ptxtAtPos = ptxtAtPos[:length]
    newPtxtAtPos = newPtxtAtPos[:length]

    try:
        with open(fctxt, 'rb') as f:
            content = bytearray(f.read())
    except FileNotFoundError:
        print(f"Erro: Ficheiro {fctxt} não encontrado.")
        sys.exit(1)

    target_ciphertext = content[file_pos : file_pos + length]

    new_ciphertext = xor_bytes(target_ciphertext, ptxtAtPos, newPtxtAtPos)

    content[file_pos : file_pos + length] = new_ciphertext

    out_filename = fctxt + ".attck"
    with open(out_filename, 'wb') as f:
        f.write(content)

    print(f"Ataque concluído com sucesso!")
    print(f"Criptograma manipulado guardado em: {out_filename}")

if __name__ == "__main__":
    main()