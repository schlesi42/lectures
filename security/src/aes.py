import os, random, json
from hashlib import sha256
from Crypto.Util.number import bytes_to_long
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def encrypt(m, key):
    key = sha256(str(key).encode()).digest()
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(m, 16))
    return {'iv': iv.hex(), 'enc_msg': ct.hex()}

def decrypt(key, iv, enc_msg):
    key = sha256(str(key).encode()).digest()
    cipher = AES.new(key, AES.MODE_CBC, bytes.fromhex(iv))
    enc_msg = bytes.fromhex(enc_msg)   
    return cipher.decrypt(enc_msg).decode()

m = b"Test"
key = 123456789
enc = encrypt(m, key)
print(enc)
print(decrypt(key, enc['iv'], enc['enc_msg']))

