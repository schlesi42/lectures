from collections import Counter

def rotate(c, rotation):
    if 'a' <= c <= 'z':
        return chr(((ord(c) - ord('a') + rotation) % 26) + ord('a'))
    elif 'A' <= c <= 'Z':
        return chr(((ord(c) - ord('A') + rotation) % 26) + ord('A'))
    else:
        return c

def caesar_encrypt(s, rotation):
    return ''.join([rotate(c, rotation) for c in s])

def caesar_decrypt(s, rotation):
    return ''.join([rotate(c, -rotation) for c in s])

def frequency_analysis(ciphertext):
    # Count occurrences of each character in the ciphertext
    counts = Counter(ciphertext)
    
    # Sort characters by frequency (most frequent first)
    ordered_chars = [char for char, count in counts.most_common()]
    
    # Common letter frequencies in English (you may adjust for other languages)
    english_common = 'etaoinshrdlcumwfgypbvkjxqz'
    
    for common_char in english_common:
        possible_shift = (ord(ordered_chars[0]) - ord(common_char)) % 26
        # Try to decrypt the ciphertext with the guessed shift
        decrypted = caesar_decrypt(ciphertext, possible_shift)
        print(f"Trying shift {possible_shift}: {decrypted[:50]}...")  # printing the first 50 characters as a sample


if __name__=='__main__':
    test_string = "This is a test."
    chiffre = caesar_encrypt(test_string,2)
    print(chiffre)
    deciphered = caesar_decrypt(chiffre, 2)
    print(deciphered)
    #print(test_string == deciphered)
    #print(frequency_analysis(chiffre))