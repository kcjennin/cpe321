from caesar import caesar_chi
from util import command_line_process, file_decode, ALPHABET, text_process

MAX_KEY_LEN: int = 13


def twist_alg(ciphertext: str) -> int:
    # get the columns for each of the possible key lengths
    all_key_lengths = {}
    for key_len in range(1, MAX_KEY_LEN+1):
        cols = {}
        for i in range(key_len):
            cols[i] = ciphertext[i::key_len]
        all_key_lengths[key_len] = cols

    # get the letter frequencies 
    all_key_frequencies = {}
    for k, cols in all_key_lengths.items():
        # get the frequencies of all the letters in each column
        letter_frequencies = {}
        for i, col in cols.items():
            # get the counts of each letter
            letter_counts = {}
            for letter in col:
                if letter not in letter_counts:
                    letter_counts[letter] = 0
                letter_counts[letter] += 1
            letter_frequencies[i] = letter_counts
        all_key_frequencies[k] = letter_frequencies
    
    # get all possible letters for each column
    all_key_letters = {}
    for key_len in all_key_frequencies:
        sub_dict = {}
        for num in all_key_frequencies[key_len]:
            letters_in = []
            for letter in all_key_frequencies[key_len][num]:
                letters_in.append(letter[0])
            sub_dict[num] = letters_in
        all_key_letters[key_len] = sub_dict

    # fill in all the frequencies that didn't show up in the column
    all_key_frequencies_complete = all_key_frequencies.copy()
    for c in ALPHABET:
        for index in all_key_letters:
            for i in all_key_letters[index]:
                if c not in all_key_letters[index][i]:
                    all_key_frequencies_complete[index][i][c] = 0
    
    # sort the key frequencies in descending order
    all_key_frequencies_complete_sorted = {}
    for index in all_key_frequencies_complete:
        sub_dict = {}
        for i in all_key_frequencies_complete[index]:
            sub_dict[i] = (sorted(all_key_frequencies_complete[index][i].items(), key=lambda x: x[1], reverse=True))
        all_key_frequencies_complete_sorted[index] = sub_dict
    
    # convert all the numbers to percentages
    all_key_percentages = {}
    for i in all_key_frequencies_complete_sorted:
        sub_dict = {}
        for j in all_key_frequencies_complete_sorted[i]:
            percentage_list = []
            if (j - 1) <= (len(ciphertext) % i):
                divisor = (len(ciphertext) // i) + 1
            else:
                divisor = len(ciphertext) // i
            
            for k in all_key_frequencies_complete_sorted[i][j]:
                tuple_new = (k[0], k[1] / divisor)
                percentage_list.append(tuple_new)
            sub_dict[j] = percentage_list
        all_key_percentages[i] = sub_dict
    
    # collect all the letter percentages without their letters
    cj = {}
    for i in all_key_percentages:
        final = [0] * 26
        for j in all_key_percentages[i]:
            cj_list = [ k[1] for k in all_key_percentages[i][j] ]
            final = [ final[n] + cj_list[n] for n in range(len(cj_list))]
        cj[i] = final
    
    # using the twist algorithm
    twists = {}
    for i in cj:
        twist = 0
        for j in enumerate(cj[i]):
            if j[0] <= 12:
                twist += j[1]
            else:
                twist -= j[1]
        twist *= 100 / i
        twists[i] = twist

    # using the twist+ algorithm
    twistplus = {}
    twistlist = list(twists.values())
    for i in twistlist:
        subtact = 0
        for j in range(twistlist.index(i)):
            subtact += (twistlist[j] / twistlist.index(i))
        number = i - subtact
        if twistlist.index(i) != 0:
            twistplus[twistlist.index(i) + 1] = number
    
    def twistplus_key(d: dict) -> int:
        mode_val = 0
        for i, j in d.items():
            if j > mode_val:
                mode = i
                mode_val = j
        return mode
    
    return twistplus_key(twistplus)


def vigenere_solver(ciphertext: str) -> str:
    plain_ciphertext = text_process(ciphertext)
    key_len = twist_alg(plain_ciphertext)

    print(f"Key Length: {key_len}")

    key_letters = []
    for i in range(key_len):
        # get the text to analyze
        col = plain_ciphertext[i::key_len]
        key_letters.append(caesar_chi(col, True))
    
    return "".join(key_letters)
    

if __name__ == "__main__":
    # get the files from the command line
    files = command_line_process("vigenere.log")

    # decode them
    outputs = [file_decode(file, vigenere_solver, mono=False) for file in files]

    # print the outputs
    print("\n---------\n|Results|\n---------\n")
    with open("vigenere.results", "w") as f:
        for file, key, text in outputs:
            output = f"{file}\tkey: {key}\n{text}\n"
            print(output)
            f.write(output)