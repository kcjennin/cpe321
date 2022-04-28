# For dealing with the command line
# --------------------------
import sys
import logging
import os.path as osp
# --------------------------
# For making the code look nicer
# --------------------------
from typing import Union, Any, Callable
# --------------------------

from data import english_expected
import string
import math

ALPHABET = string.ascii_lowercase

def text_process(nonplaintext: str) -> str:
    return "".join([c.lower() for c in nonplaintext if c.isalpha()])


def vigenere_encrypt(key: str, text: str) -> str:
    # preprocess the key and the text
    plaintext = text_process(text)
    key = key.lower()

    # make the key as long as the text by tiling it
    long_key = key * (len(plaintext) // len(key)) + key[:len(plaintext) % len(key)]

    # generate the cipher text
    ciphertext = []
    for i in range(len(plaintext)):
        plainchar = plaintext[i]
        keychar = long_key[i]
        print(plainchar, keychar)
        ciphernum = (ALPHABET.index(plainchar) + ALPHABET.index(keychar)) % 26
        ciphertext.append(ALPHABET[ciphernum])
    
    return "".join(ciphertext)


def vigenere_decrypt(key: str, ciphertext: str):
    # tile the key to be as long as the cipher text
    key_str = key * (len(ciphertext) // len(key)) + key[:len(ciphertext) % len(key)]
    decrypted = []

    j = 0
    for i in range(len(ciphertext)):
        if ciphertext[i].isalpha():
            # get the 0-25 representation the letter
            chr_num = ord(ciphertext[i].lower()) - ord('a')
            chr_num -= ord(key_str[j]) - ord('a')

            # make sure it isn't negative
            if chr_num < 0:
                chr_num += 26
            
            if ciphertext[i].isupper():
                decrypted.append(chr(chr_num + ord('A')))
            else:
                decrypted.append(chr(chr_num + ord('a')))
            j += 1
        else:
            decrypted.append(ciphertext[i])

    return "".join(decrypted)

def rot_n_str(n: int, text: str) -> str:
    key = string.ascii_lowercase
    key = key[n:] + key[:n]
    return convert(key, text)


def convert(key: str, text: str) -> str:
    if isinstance(key, list):
        key = "".join(key)
    key_2 = key + key.upper()
    mapping = dict(zip(key_2, string.ascii_letters))
    return "".join([mapping.get(c, c) for c in text])


def chi_squared(input_text: str, difference: bool=True) -> Union[float, list[float]]:
    counts = [0.0] * 26

    plaintext = "".join([c.lower() for c in input_text if c.isalpha()])
    length = len(plaintext)

    for c in plaintext:
        counts[ord(c) - ord('a')] += 1
    
    if difference:
        total = 0.0
        for i in range(26):
            total = total + math.pow((counts[i] - length*english_expected[i]),2)/(length*english_expected[i])
        return total
    else:
        return [x / sum(counts) for x in counts]


def command_line_process(logname: str) -> list[str]:
    # grab all the parts of the commandline
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    # set the logging level according to the cmdline arguments
    if log_opt := [x for x in opts if "log" in x]:
        loglevel = log_opt[0][6:]
        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(level=numeric_level, filename=f"{logname}", filemode="w")
        print(f"Log level: {loglevel.upper()}\n")
    else:
        print("Log level: WARNING\n")
    
    # print out cmdline
    logging.debug(args)
    logging.debug(opts)

    existing_files = []
    for arg in args:
        existing_files.append(arg) if osp.exists(arg) else logging.warning(f"Cannot find {arg}")
    
    # confirm there is at least one file to decode
    if len(existing_files) == 0:
        print("You have to provide at least one file to decrypt.")
        print(f"\tusage: {logname}.py [--log=...] [file1] [file2] ...")
        sys.exit(1)

    return existing_files


def file_decode(file: str, decoder: Callable[[str], str], mono=True) -> tuple[str, str]:
    # process each of the provided files
    with open(file, "r") as f:
        logging.debug(f"{file}:")
        orig_text = f.read()
    key = decoder(orig_text)
    if not key:
        return "", "", ""
    if mono:
        key = correction(orig_text, key)
        return file, key, convert(key, orig_text)
    else:
        return file, key, vigenere_decrypt(key, orig_text)


def string_swap(string: str, index1: int, index2: int) -> str:
    string_list = list(string)
    string_list[index1], string_list[index2] = string_list[index2], string_list[index1]
    return "".join(string_list)


def correction(text: str, key: str) -> str:
    print(f"key: {key}\n{convert(key, text)}")
    user_in = input("Does the input need changes? [Y/n]: ").lower().strip()
    if user_in == "y":
        while True:
            user_in = input("Enter two letters to swap (ex. `a b`) or `exit`: ").lower().strip()

            if user_in == "exit":
                break
            if len(user_in) != 3 or user_in[1] != " ":
                print("Invalid input.")
                continue

            # get the two letters and their indicies within the key
            letter1, letter2 = user_in.split()
            index1, index2 = ord(letter1) - ord('a'), ord(letter2) - ord('a')

            # swap the indicies
            key = string_swap(key, index1, index2)

            # reprint the text
            print(f"key: {key}\n{convert(key, text)}")
    return key
