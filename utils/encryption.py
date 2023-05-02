from Crypto.Cipher import AES
from utils import config

config = config.Configuration.from_yaml_file("../persistent_data/config.yaml")


def encrypt_data(unencrypted_data):
    with open(config.datafiles.keyfile, "rb") as key_file:
        key = key_file.read()

    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce

    ciphertext, tag = cipher.encrypt_and_digest(unencrypted_data.encode("ascii"))

    return ciphertext, nonce, tag


def unencrypt_data(encrypted_data, nonce, tag):
    with open(config.datafiles.keyfile, "rb") as key_file:
        key = key_file.read()

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    unencrypted_data = cipher.decrypt(encrypted_data)

    try:
        cipher.verify(tag)
        return unencrypted_data.decode("ascii")
    except ValueError:
        return False
