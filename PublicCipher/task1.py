import random
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class User:
    """ Class for storing relevant client information in the exchange
    """
    def __init__(self, p=35, g=5):
        # save the p and g values
        self.p = p
        self.g = g

        # get the seed for the values to be exchanged
        self.c = random.randint(1, 1000)

    def get_C(self):
        # calculate the value to be eventually exchanged
        return (self.g ** self.c) % self.p

    def compute_s(self, C: int):
        # get the unhashed value for the key
        self.s = (C ** self.c) % self.p

    def calc_key(self):
        # hash the initial key value
        digest = hashes.Hash(hashes.SHA256())
        digest.update(self.s.to_bytes(128, 'big'))
        self.key = digest.finalize()[:16]

    def send_text(self, plaintext: str):
        # encrypt the text `m` with the key we generated earlier
        encryptor = Cipher(algorithms.AES(self.key), modes.CBC(self.key)).encryptor()
        return encryptor.update(plaintext.encode("UTF-8")) + encryptor.finalize()

    def receive_text(self, ciphertext: bytes):
        # decrypt the the cipher text and print it
        decryptor = Cipher(algorithms.AES(self.key), modes.CBC(self.key)).decryptor()
        print((decryptor.update(ciphertext) + decryptor.finalize()).decode())

class RSA:
    def __init__(self):
        self.E = 65537
        self.key_gen()

    def modinv(self, a, m):
        # Applies Extended Euclid Algorithm to inverse the modulo
        g, x, y = self.euclid_ext(a, m)
        if g != 1:
            raise Exception('modular inverse does not exist')
        else:
            return x % m

    def euclid_ext(self, a, b):
        # Found here: https://www.geeksforgeeks.org/euclidean-algorithms-basic-and-extended/
        # Base Case
        if a == 0 : 
            return b, 0, 1
            
        gcd, x1, y1 = self.euclid_ext(b%a, a)
    
        # Update x and y using results of recursive call
        return gcd, y1 - (b//a) * x1, x1

    def key_gen(self):
        # Lets pretend I can generate large primes
        P = None
        Q = None

        # Generate a public key
        self.public_key_gen(P, Q)

        # Generate a private key
        self.private_key_gen(P, Q)

    def public_key_gen(self, P, Q):
        # Public keys are two large prime numbers multiplied by eachother
        self.public_key = P * Q

    def private_key_gen(self, P, Q):
        # E*D mod(((P-1) * (Q-1)) = 1
        # Solve for D, the private key: D = (1/E) invmod ((P-1) * (Q-1))
        self.private_key = self.modinv((1/self.E), (P-1) * (Q-1))

def task1():
    # assign the two large p and g values
    p = int('B10B8F96 A080E01D DE92DE5E AE5D54EC 52C99FBC FB06A3C6 9A6A9DCA 52D23B61 6073E286 75A23D18 9838EF1E 2EE652C0 13ECB4AE A9061123 24975C3C D49B83BF ACCBDD7D 90C4BD70 98488E9C 219A7372 4EFFD6FA E5644738 FAA31A4F F55BCCC0 A151AF5F 0DC8B4BD 45BF37DF 365C1A65 E68CFDA7 6D4DA708 DF1FB2BC 2E4A4371'.replace(" ", ""), 16)
    g = int('A4D1CBD5 C3FD3412 6765A442 EFB99905 F8104DD2 58AC507F D6406CFF 14266D31 266FEA1E 5C41564B 777E690F 5504F213 160217B4 B01B886A 5E91547F 9E2749F4 D7FBD7D3 B9A92EE1 909D0D22 63F80A76 A6A24C08 7A091F53 1DBF0A01 69B6A28A D662A4D1 8E73AFA3 2D779D59 18D08BC8 858F4DCE F97C2A24 855E6EEB 22B3B2E5'.replace(" ", ""), 16)

    # create Alice and Bob with the p and g values
    Alice = User(p, g)
    Bob = User(p, g)

    # Get the exchange values
    A = Alice.get_C()
    B = Bob.get_C()

    # calculate the key primitive
    Alice.compute_s(B)
    Bob.compute_s(A)

    # hash the key
    Alice.calc_key()
    Bob.calc_key()

    # make sure the keys are the same
    assert Alice.key == Bob.key

    # try to exchange messages
    Bob.receive_text(Alice.send_text('Hi Bob!AAAAAAAAA'))
    Alice.receive_text(Bob.send_text('Hi Alice!AAAAAAA'))

def task2_1():
    '''
    Mallory changes A/B: key becomes SHA-256(0), and you can decrypt both messages.
    '''

    p = int('B10B8F96 A080E01D DE92DE5E AE5D54EC 52C99FBC FB06A3C6 9A6A9DCA 52D23B61 6073E286 75A23D18 9838EF1E 2EE652C0 13ECB4AE A9061123 24975C3C D49B83BF ACCBDD7D 90C4BD70 98488E9C 219A7372 4EFFD6FA E5644738 FAA31A4F F55BCCC0 A151AF5F 0DC8B4BD 45BF37DF 365C1A65 E68CFDA7 6D4DA708 DF1FB2BC 2E4A4371'.replace(" ", ""), 16)
    g = int('A4D1CBD5 C3FD3412 6765A442 EFB99905 F8104DD2 58AC507F D6406CFF 14266D31 266FEA1E 5C41564B 777E690F 5504F213 160217B4 B01B886A 5E91547F 9E2749F4 D7FBD7D3 B9A92EE1 909D0D22 63F80A76 A6A24C08 7A091F53 1DBF0A01 69B6A28A D662A4D1 8E73AFA3 2D779D59 18D08BC8 858F4DCE F97C2A24 855E6EEB 22B3B2E5'.replace(" ", ""), 16)

    Alice = User(p, g)
    Bob = User(p, g)

    A = Alice.get_C()
    B = Bob.get_C()

    # machine in middle
    A = p
    B = p

    Alice.compute_s(B)
    Bob.compute_s(A)

    Alice.calc_key()
    Bob.calc_key()

    assert Alice.key == Bob.key

    Bob.receive_text(Alice.send_text('Hi Bob!AAAAAAAAA'))
    Alice.receive_text(Bob.send_text('Hi Alice!AAAAAAA'))

def task2_2():
    '''
    Mallory sends a new p to Bob, and intercepts messages from both.
    '''

    p = int('B10B8F96 A080E01D DE92DE5E AE5D54EC 52C99FBC FB06A3C6 9A6A9DCA 52D23B61 6073E286 75A23D18 9838EF1E 2EE652C0 13ECB4AE A9061123 24975C3C D49B83BF ACCBDD7D 90C4BD70 98488E9C 219A7372 4EFFD6FA E5644738 FAA31A4F F55BCCC0 A151AF5F 0DC8B4BD 45BF37DF 365C1A65 E68CFDA7 6D4DA708 DF1FB2BC 2E4A4371'.replace(" ", ""), 16)
    g = int('A4D1CBD5 C3FD3412 6765A442 EFB99905 F8104DD2 58AC507F D6406CFF 14266D31 266FEA1E 5C41564B 777E690F 5504F213 160217B4 B01B886A 5E91547F 9E2749F4 D7FBD7D3 B9A92EE1 909D0D22 63F80A76 A6A24C08 7A091F53 1DBF0A01 69B6A28A D662A4D1 8E73AFA3 2D779D59 18D08BC8 858F4DCE F97C2A24 855E6EEB 22B3B2E5'.replace(" ", ""), 16)

    # Mallory sends a tampered g value to Bob
    g_b = 1

    Alice = User(p, g)
    Bob = User(p, g_b)

    # Mallory intercepts the message to Bob and creates two sessions, one to Alice and the other to Bob
    Mal_A = User(p, g)
    Mal_B = User(p, g_b)

    A = Alice.get_C()
    B = Bob.get_C()
    A_m = Mal_A.get_C()
    B_m = Mal_B.get_C()

    # Alice and Mallory have their own unique s value
    Alice.compute_s(A_m)
    Mal_A.compute_s(A)

    # Bob and Mallory have their own unique s value
    Bob.compute_s(B_m)
    Mal_B.compute_s(B)

    # Everyone calculates their own keys
    Alice.calc_key()
    Mal_A.calc_key()

    Bob.calc_key()
    Mal_B.calc_key()

    assert Alice.key == Mal_A.key
    assert Bob.key == Mal_B.key

    # Mallory can receive both Alice's and Bob's messages
    print('Mallory sees: ', end='')
    Mal_A.receive_text(Alice.send_text('Hi Bob!AAAAAAAAA'))

    print('Mallory sees: ', end='')
    Mal_B.receive_text(Bob.send_text('Hi Alice!AAAAAAA'))
    


if __name__ == '__main__':
    task2_2()