import os
from block_cipher import cbc_encode, cbc_decode


def main():
    global KEY
    global IV
    
    # generate a random key and initialization vector
    KEY = os.urandom(16)
    IV = os.urandom(16)    

    # set up a message, the zero block is on a block of its own
    eleven = "".join(["0" for _ in range(11)])
    zero_block = "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    fifteen = "".join(["0" for _ in range(15)])

    # encrypt the message
    message = submit(eleven + zero_block + fifteen)

    # once we have the encrypted message, xor the block before the zero block
    # with the target string
    e_block = message[16:33]
    temp = b";admin=true....."
    new_block = bytes(b ^ a for a, b in zip(e_block, temp))
    new_message = message[:16] + new_block + message[32:]

    # verify the message
    print(verify(new_message))
    print(cbc_decode(new_message, KEY, IV))


def submit(s: str) -> bytes:
    """Prepends and appends some information to the given string
    as well as URL encoding `=` and `;`

    21 before, 17 after

    Args:
        s (str): string to use as userdata

    Returns:
        bytes: the encoded output of the string with extra information
    """
    s.replace(";", "%3B")
    s.replace("=", "%3D")
    new_s = "userid=456; userdata=" + s + ";session-id=31337"

    return cbc_encode(bytes(new_s, "utf8"), KEY, IV)


def verify(ciphertext: bytes) -> bool:
    """Checks to see if the string `;admin=true` is in an encoded message

    Args:
        ciphertext (bytes): encrypted text

    Returns:
        bool: whether or not `;admin=true` was found
    """
    plaintext = cbc_decode(ciphertext, KEY, IV)

    if b";admin=true" in plaintext:
        return True
    return False


if __name__ == "__main__":
    main()