import random
from sympy import isprime, mod_inverse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from os import urandom
import time

def timeit(func):
    """Decorator to measure execution time of a function."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} executed in {end - start:.6f} seconds.")
        return result
    return wrapper

#@timeit
def generate_prime(bits):
    while True:
        p = random.getrandbits(bits)
        if isprime(p):
            return p

#@timeit
def find_primitive_root(p):
    if p == 2:
        return 1
    p1 = 2
    p2 = (p - 1) // p1

    while True:
        g = random.randint(2, p - 1)
        if not pow(g, (p - 1) // p1, p) == 1:
            if not pow(g, (p - 1) // p2, p) == 1:
                return g

#@timeit
def generate_elgamal_keys(key_size=256):
    p = generate_prime(key_size)
    g = find_primitive_root(p)
    x = random.randint(2, p - 2)  # Private key
    h = pow(g, x, p)  # Public key
    return {'publicKey': (p, g, h), 'privateKey': x}

#@timeit
def elgamal_encrypt(public_key, m):
    p, g, h = public_key
    y = random.randint(2, p - 2)
    s = pow(h, y, p)
    c1 = pow(g, y, p)
    c2 = (m * s) % p
    return (c1, c2)

#@timeit
def elgamal_decrypt(private_key, encrypted_message, p):
    c1, c2 = encrypted_message
    x = private_key
    s = pow(c1, x, p)
    m = (c2 * mod_inverse(s, p)) % p
    return m

#@timeit
def generate_aes_key():
    return urandom(32)  # Generate a 256-bit key

#@timeit
def aes_encrypt(key, plaintext):
    iv = urandom(16)  # AES block size is 16 bytes
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return iv + ciphertext  # Prepend IV for use in decryption

#@timeit
def aes_decrypt(key, ciphertext):
    iv = ciphertext[:16]  # Extract the IV from the beginning
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext[16:]) + decryptor.finalize()
    return plaintext.decode()

# # Example usage
# key_size = 256  # Key size in bits for ElGamal
# keys = generate_elgamal_keys(key_size)
# public_key = keys['publicKey']
# private_key = keys['privateKey']
#
# # Generate AES key and encrypt it with ElGamal
# aes_key = generate_aes_key()
# # Simulate converting AES key to an integer for ElGamal encryption
# aes_key_int = int.from_bytes(aes_key, byteorder='big', signed=False)
# encrypted_aes_key = elgamal_encrypt(public_key, aes_key_int)
#
# # Decrypt AES key with ElGamal
# decrypted_aes_key_int = elgamal_decrypt(private_key, encrypted_aes_key, public_key[0])
# decrypted_aes_key = decrypted_aes_key_int.to_bytes((decrypted_aes_key_int.bit_length() + 7) // 8, byteorder='big')
#
# # Encrypt and decrypt a message with AES
# plaintext = "Hello, World!"
# ciphertext = aes_encrypt(decrypted_aes_key, plaintext)
# decrypted_text = aes_decrypt(decrypted_aes_key, ciphertext)
