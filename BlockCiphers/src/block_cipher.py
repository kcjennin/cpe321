from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)

BLOCKSIZE = 16


def pkcs7_pad(input: bytes, blocksize: int) -> bytes:
    """Pad a byte array according to the PKCS#7 standard.

    Args:
        input (bytes): array to pad
        blocksize (int): size of blocks in bits

    Raises:
        ValueError: blocksize is greater than 256

    Returns:
        bytes: the padded array
    """
    # check the size
    if blocksize > 2040:
        raise ValueError(f"Cannot pkcs7 pad, the blocksize is too large: {blocksize}")
    if blocksize % 8:
        raise ValueError(f"Cannot pkcs7 pad, the blocksize is not divisible by 8: {blocksize % 8}")

    # change to bytes instead of bits
    blocksize //= 8

    # get the amount needed to get to the next border
    remainder = BLOCKSIZE - (len(input) % blocksize)
    
    if remainder == 0:
        return input + bytes([blocksize for _ in range(blocksize)])
    return input + bytes([remainder for _ in range(remainder)])


def pkcs7_strip(input: bytes) -> bytes:
    """Strip trailing bytes according to the PKCS#7 standard.

    Args:
        input (bytes): padded input to be stripped

    Returns:
        bytes: the stripped array of bytes
    """
    return input[:-1 * int(input[-1])]


def aes128_encrypt(data: bytes, key: bytes) -> bytes:
    if len(data) != BLOCKSIZE and len(key) != BLOCKSIZE:
        raise ValueError("aes128 only deals with 128 bits at a time")

    encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return encryptor.update(data) + encryptor.finalize()


def aes128_decrypt(data: bytes, key: bytes) -> bytes:
    if len(data) != BLOCKSIZE and len(key) != BLOCKSIZE:
        raise ValueError("aes128 only deals with 128 bits at a time")

    decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    return decryptor.update(data) + decryptor.finalize()


def ecb_encode(data: bytes, key: bytes):
    """Encode a byte array using the ECB mode and AES 128 encryption

    Args:
        data (bytes): plain text
        key (bytes): key for the AES

    Returns:
        bytes: AES 128 ECB encoded bytes
    """
    padded = pkcs7_pad(data, 128)
    return b"".join([aes128_encrypt(padded[i:i+BLOCKSIZE], key) for i in range(0, len(padded), BLOCKSIZE)])


def ecb_decode(data: bytes, key: bytes):
    """Decode a byte array that was encoded using ECB and AES 128

    Args:
        data (bytes): encrypted data
        key (bytes): key for the AES

    Returns:
        bytes: the original plain text
    """
    padded = b"".join([aes128_decrypt(data[i:i+BLOCKSIZE], key) for i in range(0, len(data), BLOCKSIZE)])
    return pkcs7_strip(padded)


def cbc_encode(data: bytes, key: bytes, iv: bytes):
    # pad to 16 bytes
    padded = pkcs7_pad(data, 128)

    # go one block at a time through the input and encrypt it
    ciphertext = []
    iv_temp = iv
    for i in range(0, len(padded), BLOCKSIZE):
        # xor the block with the iv
        data_xor_iv = bytes(a ^ b for a, b in zip(padded[i:i+BLOCKSIZE], iv_temp))
        
        # update the iv
        iv_temp = aes128_encrypt(data_xor_iv, key)
        
        # add to the cipher text
        ciphertext.append(iv_temp)
    
    return b"".join(ciphertext)



def cbc_decode(data: bytes, key: bytes, iv: bytes):
    # deal with every block but the first
    plaintext = []
    for i in reversed(range(BLOCKSIZE, len(data), BLOCKSIZE)):
        # iv is the previous block
        iv_temp = data[i-BLOCKSIZE:i]

        # decrypt the cipher text, but we still need the xor
        needs_xor = aes128_decrypt(data[i:i+BLOCKSIZE], key)
        
        # convert to plaintext
        plaintext.append(bytes(a ^ b for a, b in zip(needs_xor, iv_temp)))
    
    # do the final block with the iv
    needs_xor = aes128_decrypt(data[:BLOCKSIZE], key)
    plaintext.append(bytes(a ^ b for a, b in zip(needs_xor, iv)))

    return pkcs7_strip(b"".join(reversed(plaintext)))

