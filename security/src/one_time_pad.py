import os
def encrypt_one_time_pad(m, key):
    return ''.join([chr(ord(m[i]) ^ ord(key[i])) for i in range(len(m))])

def decrypt_one_time_pad(c, key):
    return ''.join([chr(ord(c[i]) ^ ord(key[i])) for i in range(len(c))])

def generate_key(length):
    return ''.join([chr(os.urandom(1)[0]) for i in range(length)])

if __name__=='__main__':
    key = generate_key(15)
    m = "This is a test."
    c = encrypt_one_time_pad(m, key)
    print(c)
    print(decrypt_one_time_pad(c, key))
    print(m == decrypt_one_time_pad(c, key))
