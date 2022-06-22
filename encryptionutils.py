from Crypto.Cipher import AES
from secrets import token_bytes
from os import remove

from configutils import get_config, set_config


def generate_new_key(filename: str = None):
    if filename is None:
        filename
    remove(get_config("MSG", "keyfile", "Files/AnonMessages/key.bin"))

    set_config("MSG", "keyfile", filename)
    key = token_bytes(32)
    with open(filename, "wb") as key_file:
        key_file.write(key)


def encrypt_data(unencrypted_data):
    with open(get_config("MSG", "keyfile", "Files/AnonMessages/key.bin"), "rb") as key_file:
        key = key_file.read()

    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce

    ciphertext, tag = cipher.encrypt_and_digest(unencrypted_data.encode('ascii'))

    return ciphertext, nonce, tag


def unencrypt_data(encrypted_data, nonce, tag):
    with open(get_config("MSG", "keyfile", "Files/AnonMessages/key.bin"), "rb") as key_file:
        key = key_file.read()

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    unencrypted_data = cipher.decrypt(encrypted_data)

    try:
        cipher.verify(tag)
        return unencrypted_data.decode('ascii')
    except:
        return False
