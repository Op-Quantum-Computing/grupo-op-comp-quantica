def texto_para_numero(texto):
    msg_bytes = texto.encode("utf-8")
    return int.from_bytes(msg_bytes, byteorder="big")


def numero_para_texto(numero):
    if numero == 0:
        return ""
    tamanho = (numero.bit_length() + 7) // 8
    msg_bytes = numero.to_bytes(tamanho, byteorder="big")
    return msg_bytes.decode("utf-8")