import os
import sys
from block_cipher import cbc_encode, cbc_decode


def main():
    global KEY
    global IV
    KEY = os.urandom(16)
    IV = os.urandom(16)    

    print(verify(submit("".join(sys.argv[1:]))))


def submit(s: str) -> str:
    s.replace(";", "%3B")
    s.replace("=", "%3D")
    new_s = "userid=456; userdata=" + s + ";session-id=31337"

    return cbc_encode(bytes(new_s, "utf8"), KEY, IV)


def verify(ciphertext: bytes) -> bool:
    plaintext = cbc_decode(ciphertext, KEY, IV)

    if b";admin=true" in plaintext:
        return True
    return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: task2.py [submit-text]")
    
    main()