from ast import Tuple
from Crypto.Cipher import AES
from secrets import token_bytes


# Generates a new AES-256 key.
def generate_new_key() -> bytes:
    token_bytes(32)


# Encrypts the passed data using the given key, in EAX mode, with AES.
# Generates the ciphertext, IV and tag.
#
# Returns the ciphertext, IV and tag as a tuple.
def encrypt_data(unencrypted_data: bytes, key: bytes) -> Tuple[bytes, bytes, bytes]:
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce

    ciphertext, tag = cipher.encrypt_and_digest(unencrypted_data)

    return ciphertext, nonce, tag


# Decrypts the passed data using the given key and IV and verifies it with the given tag, in EAX mode, with AES.
#
# Returns the unencrypted data, unchanged.
#
# Throws a ValueError exception if verification fails.
def decrypt_data(encrypted_data: bytes, key: bytes, nonce: bytes, tag: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    unencrypted_data = cipher.decrypt(encrypted_data)

    cipher.verify(tag)
    return unencrypted_data
