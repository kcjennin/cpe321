import logging
from multiprocessing import Pool
from os import cpu_count

from util import command_line_process, file_decode, convert
import data
import string
import random

CIPHER_TEXT: str = "boof"
KEYS: int = 50
KEY_STEPS: int = 5000


def eval(text: str) -> float:
    score = 0

    # i is the right side of the trigram
    for i in range(3, len(text)):
        # isolate the trigram
        trigram = text[i-3:i]
        # if the trigram is in the dictionary, increase score
        if trigram in data.trigrams:
            score += data.trigrams[trigram]
    return score


def genetic_key(key_attempt: int) -> tuple[float, str]:
    random.seed(key_attempt)

    # start with a random key
    key = list(string.ascii_lowercase)
    random.shuffle(key)

    # evaluate the key
    cur_score = eval(convert(key, CIPHER_TEXT))

    # go until we get 5000 swaps that don't improve score
    i = 0
    while i < KEY_STEPS:
        index1, index2 = random.sample(range(26), 2)
        new_key = key.copy()
        new_key[index1], new_key[index2] = key[index2], key[index1]
        
        new_score = eval(convert(new_key, CIPHER_TEXT))
        if new_score > cur_score:
            cur_score = new_score
            key = new_key
            i = 0
        i += 1
    
    logging.debug(f"Attempt {key_attempt:2}: {key} with score {cur_score:.2f}")
    print(f"[PROGRESS] {key_attempt}/{KEYS}")

    return cur_score, "".join(key)


def initializer(text: str):
    global CIPHER_TEXT
    CIPHER_TEXT = text


def mono_solver(text: str) -> str:
    # run the function `genetic_key` in parallel
    logging.debug(f"Running `genetic_key` in parallel with {cpu_count()} threads.")
    pool = Pool(cpu_count(), initializer, (text,))
    results = pool.map(genetic_key, range(1, KEYS))

    best_score, best_key = max(results, key=lambda x: x[0])

    logging.debug(f"Best key: {best_key} with score {best_score:.2f}")
    return best_key


if __name__ == "__main__":
    # get the files from the command line
    files = command_line_process("mono.log")

    # decode them
    outputs = [file_decode(file, mono_solver) for file in files]

    # print the outputs
    print("\n---------\n|Results|\n---------\n")
    with open("mono.results", "w") as f:
        for file, key, text in outputs:
            output = f"{file}\tkey: {key}\n{text}\n"
            print(output)
            f.write(output)