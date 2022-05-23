# This is for testing, not for actual code
# ---------------
import logging
# ---------------
from util import chi_squared, command_line_process, file_decode, convert
import string


# guess the cipher key using chi squared values
def caesar_chi(text: str, get_rot_3: bool=False) -> str:
    chi_values = []
    key = string.ascii_lowercase
    for i in range(26):
        new_text = convert(key, text)
        chi_val = chi_squared(new_text)
        chi_values.append((new_text, chi_val))
        logging.debug(f"\tkey: {i:2}\tchi: {chi_val:.2f}")
        key = key[1:] + key[:1]
    
    min_index = chi_values.index(min(chi_values, key=lambda x: x[1]))
    if get_rot_3:
        return chr(ord('a') + min_index)
    return key[min_index:] + key[:min_index]


if __name__ == "__main__":
    # get the files to decode
    files = command_line_process("caesar.log")

    # decode them
    outputs = [file_decode(file, caesar_chi) for file in files]

    # print the outputs
    print("\n---------\n|Results|\n---------\n")
    with open("caesar.results", "w") as f:
        for file, key, text in outputs:
            output = f"{file}\tkey: {key}\n{text}\n"
            print(output)
            f.write(output)