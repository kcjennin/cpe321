import random
from multiprocessing import Process, Event, Array, cpu_count
import time
from util import *

sysrandom = random.SystemRandom()


def bincount(n: int):
    return bin(n).count("1")


def int_to_bytes(n: int, l: int):
    return n.to_bytes(l // 8, 'little')


def bytes_generator(l: int) -> bytes:
    val = 0
    while True:
        if val == 2 ** l:
            return
        yield val.to_bytes(l // 8, 'little')
        val += 1


def worker(b0, b1_list, quit, foundit, output):
    h0 = short_hash(b0, 8 * len(b0))
    while not quit.is_set():
        for b1 in b1_list:
            h1 = short_hash(b1, 8 * len(h1))
            if h0 == h1:
                for i, b in enumerate(b1):
                    output[i] = b
                foundit.set()


def find_collisions():
    ''' THIS IS FUCKED, JUST USE BYTE STRINGS OF LEN 8 I GUESS, I DONT KNOW
    '''
    data = []
    # for i in range(8, 52, 2):
    for i in [8]:
        t0 = time.time()
        
        quit = Event()
        foundit = Event()
        b0 = sysrandom.randbytes(i//8)
        output = Array('i', i//8)
        
        for i in range(cpu_count()):
            p = Process(target=worker, args=(b0, ..., quit, foundit, output))


        # log the time difference
        time_diff = time.time() - t0



def main():
    init_bytes = b"Hello, world!"
    bit_len = 8 * len(init_bytes)
    bits0 = int.from_bytes(init_bytes, 'little')

    # generate a bunch of byte strings with a hamming distance of 1 from `init_bytes`
    perms = []
    for i in random.sample(range(bit_len), 10):
        bitnum = random.randint(0, bit_len)
        bits1 = bits0 ^ (1 << bitnum)
        perms.append(int_to_bytes(bits1, bit_len))
    
    
    print("Checking 10 pairs of bytes with hamming distances of 1:\n")
    for perm in perms:
        print(f"\t{string_SHA256(init_bytes)}\n\t{string_SHA256(perm)}\n")


if __name__ == "__main__":
    main()