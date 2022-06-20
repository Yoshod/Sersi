from Crypto.Cipher import AES
from secrets import token_bytes
from os import remove


def generate_new_key():
    key = token_bytes(32)
    remove("key.bin")
    key_file = open("key.bin", "wb")
    key_file.write(key)
    key_file.close()


def encrypt_data(unencrypted_data):
    key_file = open("key.bin", "rb")
    key = key_file.read()
    key_file.close()

    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce

    nonce_file = open("nonce.bin", "wb")
    nonce_file.write(nonce)
    nonce_file.close()

    ciphertext, tag = cipher.encrypt_and_digest(unencrypted_data.encode('ascii'))

    tag_file = open("tag.bin", "wb")
    tag_file.write(tag)
    tag_file.close()

    return ciphertext


def unencrypt_data(encrypted_data):
    with open("key.bin", "rb") as key_file:
        key = key_file.read()

    with open("tag.bin", "rb") as tag_file:
        tag = tag_file.read()

    with open("nonce.bin", "rb") as nonce_file:
        nonce = nonce_file.read()

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    unencrypted_data = cipher.decrypt(encrypted_data)

    try:
        cipher.verify(tag)
        return unencrypted_data.decode('ascii')
    except:
        return False