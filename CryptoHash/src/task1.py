import csv
import random
import time
from util import *
import matplotlib.pyplot as plt
from os.path import exists
import pandas as pd


def _int_to_bytes(n: int, l: int):
    return n.to_bytes(l // 8, 'little')


def _find_collisions(min=8, max=50):
    for bitlen in range(min, max+2, 2):
        hash_to_str = {}
        tic = time.time()
        for i in range(2 ** bitlen):
            i_hash = short_hash(str(i).encode(), bitlen)
            if i_hash in hash_to_str:
                yield bitlen, i, hash_to_str[i_hash], i_hash, time.time() - tic
                break
            hash_to_str[i_hash] = i


def task1_b():
    init_bytes = b"Hello, world!"
    bit_len = 8 * len(init_bytes)
    bits0 = int.from_bytes(init_bytes, 'little')

    # generate a bunch of byte strings with a hamming distance of 1 from `init_bytes`
    perms = []
    for _ in random.sample(range(bit_len), 10):
        bitnum = random.randint(0, bit_len)
        bits1 = bits0 ^ (1 << bitnum)
        perms.append(_int_to_bytes(bits1, bit_len))
    
    
    print("Checking 10 pairs of bytes with hamming distances of 1:\n")
    for perm in perms:
        print(f"\t{string_SHA256(init_bytes)}\n\t{string_SHA256(perm)}\n")


def _get_all_collisions():
    with open("data/task1.csv", "w") as f:
        cols = ["Length", "Item1", "Item2", "Hash", "NumChecked", "Time"]
        rows = [cols]
        for bitlen, item2, item1, hash, time_diff in _find_collisions(min=8, max=50):
            rows.append([bitlen, item1, item2, hash, item2+1, time_diff])

            print(f"Done with {bitlen} in {time_diff:.2f} s")
        
        csv.writer(f).writerows(rows)


def task1_c():
    if not exists("data/task1.csv"):
        _get_all_collisions()
    with open("data/task1.csv") as f:
        df = pd.read_csv(f)

    _, axis = plt.subplots(1, 2)

    axis[0].grid(color='gray', linestyle='-', linewidth=1)
    axis[0].plot('Length', 'Time', data=df)
    axis[0].set_title('Collision Time vs. Digest Size')
    axis[0].set_xlabel('Digest Size (bits)')
    axis[0].set_ylabel('Time (s)')

    axis[1].grid(color='gray', linestyle='-', linewidth=1)
    axis[1].plot('Length', 'NumChecked', data=df)
    axis[1].set_title('Number of Inputs vs. Digest Size')
    axis[1].set_xlabel('Digest Size (bits)')
    axis[1].set_ylabel('Number of Inputs (Tens of Millions)')

    plt.ticklabel_format(useOffset=False)
    plt.show()

if __name__ == "__main__":
    task1_c()
